"""
Utilitaires pour la configuration.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


def load_config(config_path: str | None = None) -> dict:
    """
    Charge la configuration depuis config.json et les variables d'environnement.

    Args:
        config_path: Chemin vers config.json (optionnel)

    Returns:
        Dictionnaire de configuration
    """
    # Charger les variables d'environnement
    load_dotenv()

    # Charger config.json
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    else:
        config_path = Path(config_path)

    with open(config_path) as f:
        config = json.load(f)

    # Override avec variables d'environnement si présentes
    if project_id := os.getenv("GOOGLE_CLOUD_PROJECT"):
        config["project_id"] = project_id

    if location := os.getenv("GOOGLE_CLOUD_LOCATION"):
        config["location"] = location

    if model := os.getenv("VERTEX_AI_MODEL"):
        config["model"] = model

    if temperature := os.getenv("VERTEX_AI_TEMPERATURE"):
        config["temperature"] = float(temperature)

    return config
