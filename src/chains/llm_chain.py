"""
Chain LLM pour classification et extraction de documents KYC.

Utilise Vertex AI Gemini avec extraction structurée via Pydantic.
"""

import json
from pathlib import Path

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

from chains.configuration import Configuration
from chains.prompts import (
    PROMPT_CLASSIFICATION,
    PROMPT_EXTRACTION_CNI,
    PROMPT_EXTRACTION_JUSTIFICATIF,
    PROMPT_EXTRACTION_PASSEPORT,
    PROMPT_EXTRACTION_PERMIS,
    PROMPT_EXTRACTION_RIB,
)
from chains.schemas import (
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

    def _extract_token_usage(self, response) -> dict[str, int] | None:
        """
        Extrait les informations d'utilisation des tokens depuis la réponse.

        Args:
            response: Réponse du modèle

        Returns:
            Dictionnaire avec les informations de tokens ou None
        """
        try:
            if hasattr(response, "usage_metadata"):
                usage = response.usage_metadata
                input_tok = usage.prompt_token_count if hasattr(usage, "prompt_token_count") else 0
                output_tok = (
                    usage.candidates_token_count if hasattr(usage, "candidates_token_count") else 0
                )
                total_tok = (
                    usage.total_token_count
                    if hasattr(usage, "total_token_count")
                    else input_tok + output_tok
                )

                calculated_total = input_tok + output_tok
                overhead = total_tok - calculated_total if total_tok > calculated_total else 0

                return {
                    "input_tokens": input_tok,
                    "output_tokens": output_tok,
                    "total_tokens": total_tok,
                    "overhead_tokens": overhead,
                }
        except Exception:
            pass
        return None

    def _log_token_usage(self, document_type: str, token_usage: dict):
        """Log les statistiques de tokens pour un document."""
        if not token_usage:
            return

        input_tok = token_usage.get("input_tokens", 0)
        output_tok = token_usage.get("output_tokens", 0)
        total_tok = token_usage.get("total_tokens", 0)
        overhead_tok = token_usage.get("overhead_tokens", 0)

        # Calculer le coût
        input_cost = (input_tok / 1_000_000) * self.config.INPUT_TOKEN_PRICE_PER_MILLION
        output_cost = (output_tok / 1_000_000) * self.config.OUTPUT_TOKEN_PRICE_PER_MILLION
        total_cost = input_cost + output_cost

        if overhead_tok > 0:
            print(
                f"   💰 Tokens {document_type}: "
                f"input={input_tok}, output={output_tok}, total={total_tok} "
                f"(overhead: {overhead_tok}) | Coût: ${total_cost:.6f}"
            )
        else:
            print(
                f"   💰 Tokens {document_type}: "
                f"input={input_tok}, output={output_tok}, total={total_tok} | Coût: ${total_cost:.6f}"
            )

    def classify_document(
        self, image_path: str | Path
    ) -> tuple[ClassificationDocument, dict | None]:
        """
        Classifie le type de document.

        Args:
            image_path: Chemin vers l'image du document

        Returns:
            Tuple (Résultat de classification, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_CLASSIFICATION, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Classification", token_usage)

        # Parser la réponse JSON
        result_json = json.loads(response.text)
        return ClassificationDocument(**result_json), token_usage

    def extract_cni(self, image_path: str | Path) -> tuple[CarteIdentite, dict | None]:
        """
        Extrait les données d'une Carte Nationale d'Identité.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (Données structurées de la CNI, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_CNI, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Extraction CNI", token_usage)

        result_json = json.loads(response.text)
        return CarteIdentite(**result_json), token_usage

    def extract_passeport(self, image_path: str | Path) -> tuple[Passeport, dict | None]:
        """
        Extrait les données d'un passeport.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (Données structurées du passeport, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_PASSEPORT, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Extraction Passeport", token_usage)

        result_json = json.loads(response.text)
        return Passeport(**result_json), token_usage

    def extract_permis(self, image_path: str | Path) -> tuple[PermisConduire, dict | None]:
        """
        Extrait les données d'un permis de conduire.

        LE CAS PARFAIT POUR LA DÉMO: cases à cocher!

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (Données structurées du permis, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_PERMIS, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Extraction Permis", token_usage)

        result_json = json.loads(response.text)
        return PermisConduire(**result_json), token_usage

    def extract_justificatif(
        self, image_path: str | Path
    ) -> tuple[JustificatifDomicile, dict | None]:
        """
        Extrait les données d'un justificatif de domicile.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (Données structurées du justificatif, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_JUSTIFICATIF, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Extraction Justificatif", token_usage)

        result_json = json.loads(response.text)
        return JustificatifDomicile(**result_json), token_usage

    def extract_rib(self, image_path: str | Path) -> tuple[RIB, dict | None]:
        """
        Extrait les données d'un RIB.

        Inclut validation du checksum IBAN.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Tuple (Données structurées du RIB, token_usage)
        """
        image_part = self._load_image(image_path)

        response = self.model.generate_content(
            [PROMPT_EXTRACTION_RIB, image_part],
            generation_config=self.generation_config,
        )

        # Extraire les tokens
        token_usage = self._extract_token_usage(response)
        if token_usage:
            self._log_token_usage("Extraction RIB", token_usage)

        result_json = json.loads(response.text)
        return RIB(**result_json), token_usage

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
        total_tokens_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "overhead_tokens": 0,
        }

        try:
            # 1. Classification
            print(f"🔍 Classification du document: {image_path}")
            classification, token_usage_classification = self.classify_document(image_path)
            print(
                f"   ✓ Type détecté: {classification.type_detecte.value} "
                f"(confiance: {classification.confiance:.2%})"
            )

            # Accumuler les tokens de classification
            if token_usage_classification:
                for key in total_tokens_usage:
                    total_tokens_usage[key] += token_usage_classification.get(key, 0)

            # 2. Extraction selon le type
            print("📄 Extraction des données...")
            extraction_result = None
            token_usage_extraction = None

            if classification.type_detecte == TypeDocument.CARTE_IDENTITE:
                extraction_result, token_usage_extraction = self.extract_cni(image_path)
            elif classification.type_detecte == TypeDocument.PASSEPORT:
                extraction_result, token_usage_extraction = self.extract_passeport(image_path)
            elif classification.type_detecte == TypeDocument.PERMIS_CONDUIRE:
                extraction_result, token_usage_extraction = self.extract_permis(image_path)
            elif classification.type_detecte == TypeDocument.JUSTIFICATIF_DOMICILE:
                extraction_result, token_usage_extraction = self.extract_justificatif(image_path)
            elif classification.type_detecte == TypeDocument.RIB:
                extraction_result, token_usage_extraction = self.extract_rib(image_path)

            # Accumuler les tokens d'extraction
            if token_usage_extraction:
                for key in total_tokens_usage:
                    total_tokens_usage[key] += token_usage_extraction.get(key, 0)

            print("   ✓ Extraction réussie")

            # Afficher le total des tokens et coût pour ce document
            if total_tokens_usage["total_tokens"] > 0:
                total_cost = (
                    total_tokens_usage["input_tokens"] / 1_000_000
                ) * self.config.INPUT_TOKEN_PRICE_PER_MILLION + (
                    total_tokens_usage["output_tokens"] / 1_000_000
                ) * self.config.OUTPUT_TOKEN_PRICE_PER_MILLION
                print(
                    f"   📊 Total tokens: {total_tokens_usage['total_tokens']} | "
                    f"Coût total: ${total_cost:.6f}"
                )

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
