"""Schémas KYC pour l'extraction de documents d'identité, justificatifs et IBAN."""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    """Types de documents d'identité acceptés."""

    PASSPORT = "passport"
    NATIONAL_ID = "national_id_card"
    DRIVERS_LICENSE = "drivers_license"


class Gender(str, Enum):
    """Genre."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class IdentityDocument(BaseModel):
    """Schéma pour l'extraction de documents d'identité."""

    document_type: DocumentType = Field(
        description="Type de document : passeport, carte d'identité nationale, ou permis de conduire"
    )

    document_number: str = Field(description="Numéro du document d'identité")

    last_name: str = Field(description="Nom de famille (en majuscules)")

    first_name: str = Field(description="Prénom(s)")

    birth_date: date = Field(description="Date de naissance au format YYYY-MM-DD")

    birth_place: Optional[str] = Field(
        None, description="Lieu de naissance (ville et pays)"
    )

    nationality: str = Field(description="Nationalité")

    gender: Optional[Gender] = Field(None, description="Genre : M, F, ou X")

    issue_date: date = Field(
        description="Date de délivrance du document au format YYYY-MM-DD"
    )

    expiry_date: date = Field(
        description="Date d'expiration du document au format YYYY-MM-DD"
    )

    issuing_authority: Optional[str] = Field(
        None, description="Autorité émettrice du document"
    )

    address: Optional[str] = Field(
        None, description="Adresse complète (si présente sur le document)"
    )

    is_valid: bool = Field(
        False,
        description="Indicateur : le document est-il encore valide à la date d'aujourd'hui ?",
    )

    mrz_line1: Optional[str] = Field(
        None,
        description="Première ligne de la zone de lecture automatique (MRZ) si présente",
    )

    mrz_line2: Optional[str] = Field(
        None,
        description="Deuxième ligne de la zone de lecture automatique (MRZ) si présente",
    )

    @field_validator("last_name")
    @classmethod
    def uppercase_last_name(cls, v: str) -> str:
        """Nom de famille en majuscules."""
        return v.upper()

    @field_validator("is_valid", mode="before")
    @classmethod
    def check_validity(cls, v, info):
        """Vérifie si le document est encore valide."""
        if "expiry_date" in info.data:
            return info.data["expiry_date"] >= date.today()
        return False


class ProofOfAddressType(str, Enum):
    """Types de justificatifs de domicile acceptés."""

    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_NOTICE = "tax_notice"
    RENTAL_AGREEMENT = "rental_agreement"
    RESIDENCE_CERTIFICATE = "residence_certificate"


class ProofOfAddress(BaseModel):
    """Schéma pour l'extraction de justificatifs de domicile."""

    document_type: ProofOfAddressType = Field(
        description="Type de justificatif : facture, relevé bancaire, avis d'imposition, etc."
    )

    document_date: date = Field(description="Date du document au format YYYY-MM-DD")

    full_name: str = Field(description="Nom complet du titulaire (prénom et nom)")

    address_line1: str = Field(
        description="Première ligne de l'adresse (numéro et rue)"
    )

    address_line2: Optional[str] = Field(
        None, description="Complément d'adresse (bâtiment, appartement, etc.)"
    )

    postal_code: str = Field(description="Code postal")

    city: str = Field(description="Ville")

    country: str = Field("France", description="Pays")

    issuer: Optional[str] = Field(
        None, description="Émetteur du document (EDF, banque, etc.)"
    )

    is_recent: bool = Field(False, description="Le document a-t-il moins de 3 mois ?")

    @field_validator("is_recent", mode="before")
    @classmethod
    def check_recency(cls, v, info):
        """Vérifie si le document a moins de 3 mois."""
        if "document_date" in info.data:
            from datetime import timedelta

            three_months_ago = date.today() - timedelta(days=90)
            return info.data["document_date"] >= three_months_ago
        return False


class IBANDocument(BaseModel):
    """Schéma pour l'extraction de RIB/IBAN."""

    account_holder_name: str = Field(description="Nom du titulaire du compte")

    iban: str = Field(description="Numéro IBAN complet (format international)")

    bic_swift: Optional[str] = Field(None, description="Code BIC/SWIFT de la banque")

    bank_name: str = Field(description="Nom de la banque")

    bank_address: Optional[str] = Field(
        None, description="Adresse de l'agence bancaire"
    )

    account_number: Optional[str] = Field(
        None, description="Numéro de compte national (si différent de l'IBAN)"
    )

    sort_code: Optional[str] = Field(None, description="Code guichet ou code banque")

    is_iban_valid: bool = Field(
        False, description="L'IBAN respecte-t-il le format et le checksum ?"
    )

    @field_validator("iban")
    @classmethod
    def clean_iban(cls, v: str) -> str:
        """Nettoie l'IBAN en supprimant les espaces."""
        return v.replace(" ", "").upper()

    @field_validator("is_iban_valid", mode="before")
    @classmethod
    def validate_iban_checksum(cls, v, info):
        """Valide le checksum de l'IBAN."""
        if "iban" in info.data:
            iban = info.data["iban"].replace(" ", "")
            # Vérifie la longueur minimale
            if len(iban) < 15:
                return False

            # Réarrange : déplace les 4 premiers caractères à la fin
            rearranged = iban[4:] + iban[:4]

            # Convertit les lettres en chiffres (A=10, B=11, ..., Z=35)
            numeric = ""
            for char in rearranged:
                if char.isdigit():
                    numeric += char
                else:
                    numeric += str(ord(char) - ord("A") + 10)

            # Vérifie que le modulo 97 = 1
            return int(numeric) % 97 == 1
        return False


class KYCDossier(BaseModel):
    """Dossier KYC complet avec cohérence entre documents."""

    identity_document: IdentityDocument = Field(
        description="Document d'identité du client"
    )

    proof_of_address: ProofOfAddress = Field(description="Justificatif de domicile")

    iban_document: IBANDocument = Field(description="RIB/IBAN du client")

    name_match: bool = Field(
        False, description="Les noms correspondent-ils entre les documents ?"
    )

    address_match: bool = Field(
        False,
        description="Les adresses correspondent-elles entre pièce d'identité et justificatif ?",
    )

    all_documents_valid: bool = Field(
        False, description="Tous les documents sont-ils valides et récents ?"
    )

    kyc_status: str = Field(
        "PENDING", description="Statut global du KYC : APPROVED, REJECTED, ou PENDING"
    )

    rejection_reasons: list[str] = Field(
        default_factory=list, description="Liste des raisons de rejet si applicable"
    )
