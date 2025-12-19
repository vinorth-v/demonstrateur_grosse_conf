"""
Pipeline principal pour traiter des dossiers KYC complets.

Traite plusieurs documents d'un même client et valide la cohérence.
"""

from pathlib import Path

from .chains.configuration import Configuration
from .chains.llm_chain import KYCDocumentChain
from .chains.schemas import (
    DossierKYC,
    TypeDocument,
)


class KYCPipeline:
    """
    Pipeline pour traiter un dossier KYC complet.

    Un dossier KYC contient:
    - 1 pièce d'identité (CNI ou Passeport)
    - 1 justificatif de domicile
    - 1 RIB
    - (optionnel) 1 permis de conduire
    """

    def __init__(self, config: Configuration | None = None):
        """
        Initialise le pipeline.

        Args:
            config: Configuration
        """
        self.config = config or Configuration()
        self.chain = KYCDocumentChain(self.config)

    def process_folder(self, folder_path: str | Path) -> DossierKYC:
        """
        Traite tous les documents d'un dossier.

        Args:
            folder_path: Chemin vers le dossier contenant les documents

        Returns:
            Dossier KYC avec tous les documents extraits et validés
        """
        folder_path = Path(folder_path)

        print(f"\n{'=' * 70}")
        print(f"🏦 Traitement du dossier KYC: {folder_path.name}")
        print(f"{'=' * 70}\n")

        # Trouver tous les documents images
        extensions = [".jpg", ".jpeg", ".png", ".pdf"]
        documents = [f for f in folder_path.iterdir() if f.suffix.lower() in extensions]

        print(f"📁 {len(documents)} document(s) trouvé(s)\n")

        # Traiter chaque document
        results = {}
        for doc_path in documents:
            result = self.chain.process_document(doc_path)
            if result.extraction_reussie:
                type_doc = result.classification.type_detecte
                results[type_doc] = result

        # Construire le dossier KYC
        print(f"\n{'=' * 70}")
        print("📋 Construction du dossier KYC")
        print(f"{'=' * 70}\n")

        # Extraire les documents par type
        piece_identite = None
        justificatif = None
        rib = None
        permis = None

        # Pièce d'identité (CNI ou Passeport)
        if TypeDocument.CARTE_IDENTITE in results:
            piece_identite = results[TypeDocument.CARTE_IDENTITE].carte_identite
            print("✓ Carte d'identité trouvée")
        elif TypeDocument.PASSEPORT in results:
            piece_identite = results[TypeDocument.PASSEPORT].passeport
            print("✓ Passeport trouvé")
        else:
            print("✗ Aucune pièce d'identité trouvée")

        # Justificatif de domicile
        if TypeDocument.JUSTIFICATIF_DOMICILE in results:
            justificatif = results[
                TypeDocument.JUSTIFICATIF_DOMICILE
            ].justificatif_domicile
            print("✓ Justificatif de domicile trouvé")
        else:
            print("✗ Justificatif de domicile manquant")

        # RIB
        if TypeDocument.RIB in results:
            rib = results[TypeDocument.RIB].rib
            print("✓ RIB trouvé")
        else:
            print("✗ RIB manquant")

        # Permis (optionnel)
        if TypeDocument.PERMIS_CONDUIRE in results:
            permis = results[TypeDocument.PERMIS_CONDUIRE].permis_conduire
            print("✓ Permis de conduire trouvé (optionnel)")

        # Vérifier que tous les documents requis sont présents
        if not (piece_identite and justificatif and rib):
            print("\n❌ Dossier incomplet - documents manquants\n")
            raise ValueError(
                "Dossier KYC incomplet. Documents requis: "
                "pièce d'identité + justificatif de domicile + RIB"
            )

        # Créer le dossier
        dossier = DossierKYC(
            piece_identite=piece_identite,
            justificatif_domicile=justificatif,
            rib=rib,
            permis_conduire=permis,
        )

        # Valider la cohérence
        print(f"\n{'=' * 70}")
        print("🔍 Validation de la cohérence du dossier")
        print(f"{'=' * 70}\n")

        is_valid = dossier.valider_coherence()

        if is_valid:
            print("✅ Dossier KYC VALIDÉ\n")
        else:
            print("❌ Dossier KYC REJETÉ\n")
            print("Erreurs détectées:")
            for erreur in dossier.erreurs_validation:
                print(f"  - {erreur}")
            print()

        return dossier

    def process_documents(
        self, id_path: str | Path, address_path: str | Path, rib_path: str | Path
    ) -> DossierKYC:
        """
        Traite des documents individuels (non dans un dossier).

        Args:
            id_path: Chemin vers la pièce d'identité
            address_path: Chemin vers le justificatif de domicile
            rib_path: Chemin vers le RIB

        Returns:
            Dossier KYC validé
        """
        print(f"\n{'=' * 70}")
        print("🏦 Traitement de documents KYC individuels")
        print(f"{'=' * 70}\n")

        # Traiter chaque document
        print("1️⃣ Pièce d'identité...")
        result_id = self.chain.process_document(id_path)
        if not result_id.extraction_reussie:
            raise ValueError(f"Échec extraction pièce d'identité: {result_id.erreurs}")

        # Extraire selon le type
        if result_id.carte_identite:
            piece_identite = result_id.carte_identite
        elif result_id.passeport:
            piece_identite = result_id.passeport
        else:
            raise ValueError("Type de pièce d'identité non reconnu")

        print("2️⃣ Justificatif de domicile...")
        result_address = self.chain.process_document(address_path)
        if (
            not result_address.extraction_reussie
            or not result_address.justificatif_domicile
        ):
            raise ValueError(f"Échec extraction justificatif: {result_address.erreurs}")
        justificatif = result_address.justificatif_domicile

        print("3️⃣ RIB...")
        result_rib = self.chain.process_document(rib_path)
        if not result_rib.extraction_reussie or not result_rib.rib:
            raise ValueError(f"Échec extraction RIB: {result_rib.erreurs}")
        rib = result_rib.rib

        # Créer et valider le dossier
        dossier = DossierKYC(
            piece_identite=piece_identite, justificatif_domicile=justificatif, rib=rib
        )

        print(f"\n{'=' * 70}")
        print("🔍 Validation de la cohérence")
        print(f"{'=' * 70}\n")

        is_valid = dossier.valider_coherence()

        if is_valid:
            print("✅ Dossier KYC VALIDÉ\n")
        else:
            print("❌ Dossier KYC REJETÉ\n")
            for erreur in dossier.erreurs_validation:
                print(f"  - {erreur}")
            print()

        return dossier
