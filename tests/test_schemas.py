"""Tests pour les schémas KYC."""

from datetime import date, timedelta

import pytest

from chains.schemas import (
    RIB,
    CarteIdentite,
    DossierKYC,
    JustificatifDomicile,
    Passeport,
    Sexe,
    TypeJustificatifDomicile,
)


class TestCarteIdentite:
    """Tests pour le schéma CarteIdentite."""

    def test_cni_valide(self):
        """Test d'une CNI valide."""
        cni = CarteIdentite(
            numero_document="123456789012",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris (75)",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
            nationalite="FRA",
        )

        assert cni.est_valide is True
        assert cni.numero_document == "123456789012"

    def test_cni_expiree(self):
        """Test d'une CNI expirée."""
        cni = CarteIdentite(
            numero_document="123456789012",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris (75)",
            date_emission=date(2010, 1, 1),
            date_expiration=date(2020, 1, 1),
            nationalite="FRA",
        )

        assert cni.est_valide is False

    def test_numero_avec_espaces(self):
        """Test normalisation du numéro avec espaces."""
        cni = CarteIdentite(
            numero_document="123 456 789 012",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris (75)",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
        )

        assert cni.numero_document == "123456789012"

    def test_numero_invalide(self):
        """Test avec un numéro invalide (trop court)."""
        with pytest.raises(ValueError, match="12 caractères"):
            CarteIdentite(
                numero_document="12345",
                nom="MARTIN",
                prenom="Jean",
                sexe=Sexe.M,
                date_naissance=date(1990, 5, 15),
                lieu_naissance="Paris (75)",
                date_emission=date(2020, 1, 1),
                date_expiration=date(2030, 1, 1),
            )


class TestPasseport:
    """Tests pour le schéma Passeport."""

    def test_passeport_valide(self):
        """Test d'un passeport valide."""
        pp = Passeport(
            numero_passeport="24AX12345",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
            autorite_delivrance="Préfecture de Paris",
        )

        assert pp.numero_passeport == "24AX12345"
        assert pp.est_valide is True

    def test_numero_passeport_normalisation(self):
        """Test normalisation du numéro de passeport."""
        pp = Passeport(
            numero_passeport="24 ax 123 45",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
            autorite_delivrance="Préfecture de Paris",
        )

        assert pp.numero_passeport == "24AX12345"


class TestJustificatifDomicile:
    """Tests pour le schéma JustificatifDomicile."""

    def test_justificatif_recent(self):
        """Test d'un justificatif récent (< 3 mois)."""
        date_recente = date.today() - timedelta(days=30)

        justif = JustificatifDomicile(
            type_justificatif=TypeJustificatifDomicile.FACTURE_ELECTRICITE,
            nom_titulaire="MARTIN",
            prenom_titulaire="Jean",
            adresse_ligne1="10 rue de la Paix",
            code_postal="75001",
            ville="Paris",
            date_document=date_recente,
            emetteur="EDF",
            montant=120.50,
        )

        assert justif.est_recent is True

    def test_justificatif_ancien(self):
        """Test d'un justificatif trop ancien (> 3 mois)."""
        date_ancienne = date.today() - timedelta(days=100)

        justif = JustificatifDomicile(
            type_justificatif=TypeJustificatifDomicile.FACTURE_ELECTRICITE,
            nom_titulaire="MARTIN",
            adresse_ligne1="10 rue de la Paix",
            code_postal="75001",
            ville="Paris",
            date_document=date_ancienne,
            emetteur="EDF",
        )

        assert justif.est_recent is False

    def test_code_postal_invalide(self):
        """Test avec un code postal invalide."""
        with pytest.raises(ValueError, match="5 chiffres"):
            JustificatifDomicile(
                type_justificatif=TypeJustificatifDomicile.FACTURE_ELECTRICITE,
                nom_titulaire="MARTIN",
                adresse_ligne1="10 rue de la Paix",
                code_postal="750",
                ville="Paris",
                date_document=date.today(),
                emetteur="EDF",
            )


class TestRIB:
    """Tests pour le schéma RIB."""

    def test_rib_valide(self):
        """Test d'un RIB avec IBAN valide."""
        rib = RIB(
            nom_titulaire="MARTIN",
            prenom_titulaire="Jean",
            code_banque="30004",
            code_guichet="00810",
            numero_compte="00001234567",
            cle_rib="89",
            iban="FR7630004008100001234567889",
            bic="BNPAFRPP",
            nom_banque="BNP Paribas",
        )

        # L'IBAN devrait être validé par le checksum modulo 97
        assert rib.iban_valide is True
        assert rib.iban == "FR7630004008100001234567889"

    def test_iban_normalisation(self):
        """Test normalisation de l'IBAN avec espaces."""
        rib = RIB(
            nom_titulaire="MARTIN",
            code_banque="30004",
            code_guichet="00810",
            numero_compte="00001234567",
            cle_rib="89",
            iban="FR76 3000 4008 1000 0123 4567 889",
            bic="BNPAFRPP",
            nom_banque="BNP Paribas",
        )

        assert rib.iban == "FR7630004008100001234567889"

    def test_iban_invalide_longueur(self):
        """Test avec un IBAN de longueur invalide."""
        with pytest.raises(ValueError, match="27 caractères"):
            RIB(
                nom_titulaire="MARTIN",
                code_banque="30004",
                code_guichet="00810",
                numero_compte="00001234567",
                cle_rib="89",
                iban="FR7612345",
                bic="BNPAFRPP",
                nom_banque="BNP Paribas",
            )


class TestDossierKYC:
    """Tests pour le schéma DossierKYC complet."""

    def test_dossier_coherent(self):
        """Test d'un dossier KYC cohérent."""
        # CNI
        cni = CarteIdentite(
            numero_document="123456789012",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris (75)",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
        )

        # Justificatif récent
        justif = JustificatifDomicile(
            type_justificatif=TypeJustificatifDomicile.FACTURE_ELECTRICITE,
            nom_titulaire="MARTIN",
            prenom_titulaire="Jean",
            adresse_ligne1="10 rue de la Paix",
            code_postal="75001",
            ville="Paris",
            date_document=date.today() - timedelta(days=30),
            emetteur="EDF",
        )

        # RIB valide
        rib = RIB(
            nom_titulaire="MARTIN",
            prenom_titulaire="Jean",
            code_banque="30004",
            code_guichet="00810",
            numero_compte="00001234567",
            cle_rib="89",
            iban="FR7630004008100001234567889",
            bic="BNPAFRPP",
            nom_banque="BNP Paribas",
        )

        dossier = DossierKYC(piece_identite=cni, justificatif_domicile=justif, rib=rib)

        is_valid = dossier.valider_coherence()
        assert is_valid is True
        assert dossier.dossier_complet is True
        assert dossier.coherence_identite is True

    def test_dossier_incohérent_nom(self):
        """Test d'un dossier avec incohérence de nom."""
        cni = CarteIdentite(
            numero_document="123456789012",
            nom="MARTIN",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date(1990, 5, 15),
            lieu_naissance="Paris (75)",
            date_emission=date(2020, 1, 1),
            date_expiration=date(2030, 1, 1),
        )

        justif = JustificatifDomicile(
            type_justificatif=TypeJustificatifDomicile.FACTURE_ELECTRICITE,
            nom_titulaire="DUPONT",  # Nom différent!
            adresse_ligne1="10 rue de la Paix",
            code_postal="75001",
            ville="Paris",
            date_document=date.today() - timedelta(days=30),
            emetteur="EDF",
        )

        rib = RIB(
            nom_titulaire="MARTIN",
            code_banque="30004",
            code_guichet="00810",
            numero_compte="00001234567",
            cle_rib="89",
            iban="FR7630004008100001234567889",
            bic="BNPAFRPP",
            nom_banque="BNP Paribas",
        )

        dossier = DossierKYC(piece_identite=cni, justificatif_domicile=justif, rib=rib)

        is_valid = dossier.valider_coherence()
        assert is_valid is False
        assert dossier.coherence_identite is False
        assert len(dossier.erreurs_validation) > 0
