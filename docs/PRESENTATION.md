# 🎤 Guide de présentation pour la conférence

## Timing: 15 minutes

### Slide 1: Titre (30 sec)
**"De 6 mois à 2 jours : La révolution LLM pour le traitement documentaire"**

### Slide 2: Le problème (2 min)
- Exemple concret: documents KYC bancaires
- Montrer les différents types de documents
- Complexité: formats variés, cases à cocher, validation métier

**Point clé**: "Il y a 2 ans, ce projet aurait pris 6 mois et 100k€"

### Slide 3: L'approche classique (2 min)
Dérouler le calvaire du deep learning classique:
- ❌ 10 000+ images annotées
- ❌ Bounding boxes pour chaque champ
- ❌ CNN pour classification
- ❌ Détection d'objets pour localisation
- ❌ Classificateur binaire pour cases cochées
- ❌ Post-processing OCR complexe
- ❌ Maintenance cauchemardesque

**Anecdote**: "Et si le format change? Ré-entraînement complet!"

### Slide 4: L'approche LLM (1 min)
- ✅ Quelques prompts bien rédigés
- ✅ Schémas Pydantic
- ✅ Règles métier en Python
- ✅ C'est tout!

**Transition**: "Montrons-le en live..."

### DÉMO LIVE (8 min)

#### Partie 1: Classification (1 min)
```bash
python src/main.py examples/cni_exemple.jpg
```
- "Le LLM regarde le document"
- "Identifie instantanément que c'est une CNI"
- Montrer la confiance à 98%

#### Partie 2: Extraction structurée (2 min)
- Montrer le JSON retourné
- Souligner la structure Pydantic
- Validation automatique des dates

**Point technique**: "Avant, ça nécessitait du template matching ou de l'OCR + regex complexe"

#### Partie 3: ⭐ LE MOMENT FORT - Cases à cocher (3 min)
```bash
python src/main.py examples/permis_exemple.jpg
```

**Setup dramatique**:
1. Afficher le permis de conduire
2. Zoomer sur la section des catégories
3. "Regardez ces cases cochées. B et A2."

**Expliquer l'approche classique**:
- "Avant, il fallait:"
  - "1. Annoter des bounding boxes pour CHAQUE catégorie"
  - "2. Entraîner un détecteur pour localiser les cases"
  - "3. Entraîner un classificateur: cochée ou non?"
  - "4. Gérer les cas ambigus: partiellement cochée, croix vs coche, etc."
  - "Des centaines d'heures de travail!"

**Révélation**:
- "Maintenant, regardez ce que je fais:"
- Afficher le prompt: *"Quelles catégories sont cochées?"*
- Lancer l'extraction
- Résultat: `["B", "A2"]`
- **"C'EST TOUT!"**

**Silence dramatique de 2 secondes**

"Le LLM VOIT l'image. Il COMPREND que ce sont des cases. 
Il IDENTIFIE lesquelles sont cochées. Visuellement. 
Comme un humain."

**Impact**: "C'est ÇA, la vraie révolution."

#### Partie 4: Dossier complet (2 min)
```bash
python src/main.py --folder examples/dossier_client_001/
```

- Pipeline automatique
- Validation de cohérence entre documents
- Rapport final: ACCEPTÉ ou REJETÉ

### Slide 5: Comparaison chiffrée (1 min)

| Critère | Deep Learning | LLM |
|---------|--------------|-----|
| Temps dev | 3-6 mois | 2 jours |
| Coût setup | 100k€ | ~0€ |
| Dataset | 10k images | 0 |
| Nouveaux formats | Ré-entraîner | Adapter prompt |

### Slide 6: Cas d'usage idéaux (1 min)
Où les LLM multimodaux excellent:
- ✅ Documents à mise en page variable
- ✅ Formulaires avec cases à cocher
- ✅ Validation de cohérence contextuelle
- ✅ Multi-format / multi-langue
- ✅ Besoin de compréhension sémantique

### Slide 7: Limites actuelles (30 sec)
Honnêteté:
- Coût par document (vs one-time training)
- Latence ~2-3 secondes
- Dépendance à un provider

**Mais**: "Les modèles s'améliorent et se démocratisent chaque mois"

### Slide 8: Conclusion (30 sec)
**Messages clés:**
1. Paradigm shift: de "entraîner" à "poser les bonnes questions"
2. Démocratisation de l'IA documentaire
3. Time-to-market révolutionnaire
4. On n'a pas encore vu le plein potentiel

**Phrase finale**: 
"Si vous avez un projet de traitement de documents, 
ne commencez pas par annoter des bounding boxes. 
Commencez par écrire un prompt. 
Vous me remercierez dans 6 mois."

## 🎯 Points d'attention

### Timing
- Garder 8 min pour la démo live
- Ne pas s'attarder sur les slides
- Le public doit VOIR le code fonctionner

### Dramatisation
- Le moment "cases cochées" est LE climax
- Préparer ce moment comme un magicien prépare son tour
- Laisser le temps à l'audience de comprendre l'ampleur de la simplification

### Backup plan
- Avoir des screenshots de la démo au cas où
- Tester la connexion API avant
- Préparer une vidéo screencast en backup

### Questions attendues

**Q: "Mais le coût API n'est-il pas prohibitif?"**
R: "Comparons: 0.03€/doc en API vs infrastructure GPU 24/7. 
Pour < 100k docs/mois, l'API est moins chère."

**Q: "Et la confidentialité des données?"**
R: "Google Cloud permet du deployment on-premise avec Vertex AI. 
Ou utilisez un modèle open-source hébergé localement."

**Q: "Quelle est la précision comparée?"**
R: "Dans nos tests: 92-97% pour LLM vs 85-92% pour notre ancien CNN. 
Et surtout: beaucoup moins de faux positifs."

**Q: "Ça marche avec quelle quantité de documents?"**
R: "Testé avec succès sur 500+ documents variés. 
Zero-shot, sans fine-tuning."

## 📝 Script mot-à-mot (optionnel)

### Introduction
"Bonjour à tous. Je vais vous montrer quelque chose qui m'a bluffé.

Vous voyez ces documents? CNI, passeports, factures, RIB. 
Des trucs qu'on traite tous les jours dans les banques, assurances, administrations.

Il y a 2 ans, si on me demandait de créer un système pour extraire automatiquement 
les données de ces documents, je vous aurais dit: 
'Ok, je reviens dans 6 mois avec une équipe de data scientists.'

Aujourd'hui, je peux faire la même chose en 2 jours. Seul. 
Et avec de meilleurs résultats.

Laissez-moi vous montrer comment..."

### Transition vers la démo
"Assez parlé. Voyons ça en action..."

### Moment cases cochées
"Et maintenant, le truc qui m'a fait dire 'wow'.

Regardez ce permis de conduire. Vous voyez ces petites cases? 
A, B, C, toutes ces catégories?

En deep learning classique, détecter quelles cases sont cochées, 
c'est un cauchemar. Des bounding boxes partout. 
Un modèle pour chaque case. Des faux positifs à gérer.

Avec un LLM multimodal... regardez ma requête: 
'Quelles catégories sont cochées?'

[Lancer l'extraction]

Voilà. B et A2. Correct.

C'est... magique? Non, c'est juste que le modèle VOIT l'image. 
Comme vous et moi. Il comprend visuellement.

Ça change TOUT."

### Conclusion
"Alors, pourquoi je vous montre ça?

Parce que si vous avez dans vos cartons un projet qui nécessite 
de traiter des documents, d'extraire des données, de comprendre 
des formulaires...

Ne partez pas bille en tête sur du deep learning classique.

Testez d'abord un LLM multimodal. Vous allez gagner 
des mois de développement.

Et si ça fait le job? C'est tout bénéf.

Merci!"

## 🎬 Checklist avant la conf

- [ ] Tester la démo 3 fois le matin même
- [ ] Vérifier la connexion WiFi / 4G backup
- [ ] Credentials Google Cloud valides
- [ ] Écran partagé configuré
- [ ] Terminal en police large et lisible
- [ ] Documents d'exemple bien préparés
- [ ] Chronomètre pour le timing
- [ ] Bouteille d'eau à portée
- [ ] Screencast backup au cas où
- [ ] Slides PDF en backup
- [ ] Contact pour questions après

Bon courage! 🚀
