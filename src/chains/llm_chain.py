"""
Chain LLM pour classification et extraction de documents KYC.

Utilise Vertex AI Gemini avec extraction structurée via Pydantic.
"""

import json
from pathlib import Path

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

from .configuration import Configuration
from .prompts import (
    PROMPT_CLASSIFICATION,
    PROMPT_EXTRACTION_CNI,
    PROMPT_EXTRACTION_JUSTIFICATIF,
    PROMPT_EXTRACTION_PASSEPORT,
    PROMPT_EXTRACTION_PERMIS,
    PROMPT_EXTRACTION_RIB,
)
from .schemas import (
    RIB,
    CarteIdentite,
    ClassificationDocument,
    JustificatifDomicile,
    Passeport,
    PermisConduire,
    ResultatExtractionKYC,
    TypeDocument,
)


class KYCDocumentChain:
    """
    Chain pour classification et extraction de documents KYC.

    Pipeline:
    1. Classification du type de document
    2. Extraction structurée selon le schéma correspondant
    3. Validation des règles métier
    """

    def __init__(self, config: Configuration | None = None):
        """
        Initialise la chain.

        Args:
            config: Configuration (si None, charge depuis config.json)
        """
        self.config = config or Configuration()

        # Initialiser Vertex AI
        vertexai.init(project=self.config.project_id, location=self.config.location)

        # Créer le modèle
        self.model = GenerativeModel(self.config.model)

        # Configuration de génération
        self.generation_config = GenerationConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
            response_mime_type="application/json",
        )

    def _load_image(self, image_path: str | Path) -> Part:
        """
        Charge une image pour l'envoyer au modèle.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Part contenant l'image encodée
        """
        image_path = Path(image_path)

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Déterminer le MIME type
        suffix = image_path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
        }
        mime_type = mime_types.get(suffix, "image/jpeg")

        return Part.from_data(data=image_bytes, mime_type=mime_type)

    def classify_document(self, image_path: str | Path) -> ClassificationDocument:
        """
        Classifie le type de document.

        Args:
            image_path: Chemin vers l'image du document

        Returns:
            Résultat de classification
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_CLASSIFICATION, image_part],
            generation_config=self.generation_config,
        )

        # Parser la réponse JSON
        result_json = json.loads(response.text)
        return ClassificationDocument(**result_json)

    def extract_cni(self, image_path: str | Path) -> CarteIdentite:
        """
        Extrait les données d'une Carte Nationale d'Identité.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Données structurées de la CNI
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_CNI, image_part],
            generation_config=self.generation_config,
        )

        result_json = json.loads(response.text)
        return CarteIdentite(**result_json)

    def extract_passeport(self, image_path: str | Path) -> Passeport:
        """
        Extrait les données d'un passeport.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Données structurées du passeport
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_PASSEPORT, image_part],
            generation_config=self.generation_config,
        )

        result_json = json.loads(response.text)
        return Passeport(**result_json)

    def extract_permis(self, image_path: str | Path) -> PermisConduire:
        """
        Extrait les données d'un permis de conduire.

        LE CAS PARFAIT POUR LA DÉMO: cases à cocher!

        Args:
            image_path: Chemin vers l'image

        Returns:
            Données structurées du permis
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_PERMIS, image_part],
            generation_config=self.generation_config,
        )

        result_json = json.loads(response.text)
        return PermisConduire(**result_json)

    def extract_justificatif(self, image_path: str | Path) -> JustificatifDomicile:
        """
        Extrait les données d'un justificatif de domicile.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Données structurées du justificatif
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_JUSTIFICATIF, image_part],
            generation_config=self.generation_config,
        )

        result_json = json.loads(response.text)
        return JustificatifDomicile(**result_json)

    def extract_rib(self, image_path: str | Path) -> RIB:
        """
        Extrait les données d'un RIB.

        Inclut validation du checksum IBAN.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Données structurées du RIB
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_RIB, image_part],
            generation_config=self.generation_config,
        )

        result_json = json.loads(response.text)
        return RIB(**result_json)

    def process_document(self, image_path: str | Path) -> ResultatExtractionKYC:
        """
        Pipeline complet: classification + extraction + validation.

        C'est LA MÉTHODE PRINCIPALE du démonstrateur!

        Args:
            image_path: Chemin vers l'image du document

        Returns:
            Résultat complet avec classification, extraction et validation
        """
        erreurs = []
        avertissements = []

        try:
            # 1. Classification
            print(f"🔍 Classification du document: {image_path}")
            classification = self.classify_document(image_path)
            print(
                f"   ✓ Type détecté: {classification.type_detecte.value} "
                f"(confiance: {classification.confiance:.2%})"
            )

            # 2. Extraction selon le type
            print("📄 Extraction des données...")
            extraction_result = None

            if classification.type_detecte == TypeDocument.CARTE_IDENTITE:
                extraction_result = self.extract_cni(image_path)
            elif classification.type_detecte == TypeDocument.PASSEPORT:
                extraction_result = self.extract_passeport(image_path)
            elif classification.type_detecte == TypeDocument.PERMIS_CONDUIRE:
                extraction_result = self.extract_permis(image_path)
            elif classification.type_detecte == TypeDocument.JUSTIFICATIF_DOMICILE:
                extraction_result = self.extract_justificatif(image_path)
            elif classification.type_detecte == TypeDocument.RIB:
                extraction_result = self.extract_rib(image_path)

            print("   ✓ Extraction réussie")

            # 3. Construction du résultat
            result = ResultatExtractionKYC(
                classification=classification,
                extraction_reussie=True,
                regles_metier_validees=True,
                erreurs=erreurs,
                avertissements=avertissements,
            )

            # Assigner l'extraction au bon champ
            if classification.type_detecte == TypeDocument.CARTE_IDENTITE:
                result.carte_identite = extraction_result
            elif classification.type_detecte == TypeDocument.PASSEPORT:
                result.passeport = extraction_result
            elif classification.type_detecte == TypeDocument.PERMIS_CONDUIRE:
                result.permis_conduire = extraction_result
            elif classification.type_detecte == TypeDocument.JUSTIFICATIF_DOMICILE:
                result.justificatif_domicile = extraction_result
            elif classification.type_detecte == TypeDocument.RIB:
                result.rib = extraction_result

            print("✅ Traitement terminé avec succès\n")
            return result

        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}\n")
            erreurs.append(str(e))
            return ResultatExtractionKYC(
                classification=classification if "classification" in locals() else None,
                extraction_reussie=False,
                regles_metier_validees=False,
                erreurs=erreurs,
                avertissements=avertissements,
            )
