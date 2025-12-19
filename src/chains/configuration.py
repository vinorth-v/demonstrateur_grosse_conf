"""
Configuration pour les chains LLM.

Basé sur Vertex AI (Google Cloud).
"""

import json
from pathlib import Path
from typing import Any


class Configuration:
    """Classe de configuration pour les chains LLM."""

    def __init__(self, config_path: str | None = None):
        """
        Initialise la configuration.

        Args:
            config_path: Chemin vers le fichier config.json
        """
        if config_path is None:
            # Par défaut: config/config.json à la racine du projet
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        else:
            config_path = Path(config_path)

        with open(config_path) as f:
            self._config = json.load(f)

    @property
    def project_id(self) -> str:
        """ID du projet Google Cloud."""
        return self._config["project_id"]

    @property
    def location(self) -> str:
        """Région Google Cloud."""
        return self._config["location"]

    @property
    def model(self) -> str:
        """Modèle Vertex AI à utiliser."""
        return self._config["model"]

    @property
    def temperature(self) -> float:
        """Température pour la génération."""
        return self._config["temperature"]

    @property
    def max_output_tokens(self) -> int:
        """Nombre maximum de tokens en sortie."""
        return self._config["max_output_tokens"]

    @property
    def document_types(self) -> list[str]:
        """Types de documents supportés."""
        return self._config["document_types"]

    @property
    def business_rules(self) -> dict[str, Any]:
        """Règles métier."""
        return self._config["business_rules"]

    def get_rule(self, rule_name: str) -> Any:
        """
        Récupère une règle métier spécifique.

        Args:
            rule_name: Nom de la règle

        Returns:
            Valeur de la règle
        """
        return self.business_rules.get(rule_name)
