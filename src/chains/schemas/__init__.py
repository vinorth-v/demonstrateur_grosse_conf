"""__init__.py pour le module schemas."""

from .kyc_schemas import (
    RIB,
    CarteIdentite,
    ClassificationDocument,
    DossierKYC,
    JustificatifDomicile,
    Passeport,
    PermisConduire,
    ResultatExtractionKYC,
    TypeDocument,
)

__all__ = [
    "CarteIdentite",
    "Passeport",
    "PermisConduire",
    "JustificatifDomicile",
    "RIB",
    "TypeDocument",
    "ClassificationDocument",
    "ResultatExtractionKYC",
    "DossierKYC",
]
