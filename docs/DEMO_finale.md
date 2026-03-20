# DEMO FINALE — KYC avec LLM Multimodal (5-6 min)

---

## PHASE 1 — La problématique (0:00 - 0:45)

**[Écran : rien de spécial, juste toi face au public]**

> "Est-ce qu'il vous est déjà arrivé de devoir classifier et extraire des informations de milliers, voire de millions de documents ?
>
> C'est le problème de la **KYC — Know Your Customer**. Le client nous envoie des CNI, des passeports, des justificatifs de domicile, des RIB... et on doit extraire les informations en temps réel.
>
> Il y a deux grandes étapes :
> - La **RAD** — Reconnaissance Automatique de Documents : c'est quoi ce document ?
> - La **LAD** — Lecture Automatique de Documents : qu'est-ce qu'il y a dedans ?
>
> Avant, pour faire ça, il fallait faire du Deep Learning et pour ça il fallait :
> 1. Collecter un dataset de milliers d'images
> 2. Les faire annoter par des annotateurs externes
> 3. Reviewer et corriger ces annotations
> 4. Entraîner un modèle de Computer Vision
> 5. L'évaluer, le réentraîner, encore et encore
>
> On parle de **6 mois de développement, 3 à 5 ML engineers, des annotateurs, et facilement 100 000 euros**.
>
> Ce que je vais vous montrer aujourd'hui, c'est que tout ça peut être remplacé par un **prompt** et un **schéma de données**."

---

## PHASE 2 — Le prompt, c'est le nouveau modèle (0:45 - 1:45)

**[Écran : ouvrir `src/chains/prompts.py` — PROMPT_CLASSIFICATION en plein écran]**

> "Voici le prompt de classification — la RAD. Regardez : on décrit simplement au LLM les types de documents qu'on attend, et on lui demande de nous dire lequel c'est, avec un score de confiance.
>
> **Trente lignes de texte.** C'est tout. Pas de CNN, pas de dataset, pas d'entraînement.
>
> Le LLM est multimodal : il **voit** l'image et il **comprend** ce qu'il voit."

**[Scroller vers PROMPT_EXTRACTION_PASSEPORT]**

> "Et voici le prompt d'extraction — la LAD. Là, on lui dit : 'Voici un passeport, extrais-moi le nom, le prénom, la date de naissance, le numéro, la MRZ...'
>
> On guide le modèle avec des instructions précises : le format des dates, comment lire la zone MRZ, quels champs sont obligatoires.
>
> C'est du **prompt engineering** — et c'est ça qui remplace des mois d'annotation et d'entraînement."

---

## PHASE 3 — Le structured output, la clé de voûte (1:45 - 3:00)

**[Écran : ouvrir `src/chains/schemas/kyc_schemas.py` — classe Passeport en plein écran]**

> "Mais la question que vous allez me poser, c'est : comment on **structure** tout ça correctement ? Comment on évite que le LLM nous renvoie n'importe quoi ?
>
> La réponse, c'est le **structured output** avec **Pydantic**.
>
> Regardez ce schéma. C'est une classe Python qui décrit exactement ce qu'on attend en sortie : chaque champ a un **type** — `str`, `date`, `Optional` — et une **description** qui aide le LLM à comprendre ce qu'on veut.
>
> Par exemple ici, `numero_document` c'est un `str` avec la description 'Numéro du passeport'. Le LLM sait exactement quoi mettre dedans.
>
> Et surtout, Pydantic **valide** la sortie. Si le LLM renvoie une date dans le mauvais format, ça casse. Si un champ obligatoire manque, ça casse. On ne fait **jamais confiance aveuglément** à une sortie de modèle."

**[Scroller vers la classe RIB — montrer le validateur IBAN]**

> "Mieux encore : on peut ajouter des **règles métier** directement dans le schéma. Ici sur le RIB, on a un validateur qui vérifie le **checksum IBAN** — l'algorithme modulo 97. Si l'IBAN extrait ne passe pas cette validation mathématique, on le sait immédiatement.
>
> C'est comme ça qu'on gère les hallucinations : le **LLM extrait**, les **règles métier valident**."

**[Montrer rapidement la classe JustificatifDomicile — le validateur de récence]**

> "Autre exemple : le justificatif de domicile. On vérifie automatiquement qu'il date de **moins de 3 mois** — c'est une exigence réglementaire."

---

## PHASE 4 — La démo live (3:00 - 4:30)

**[Écran : afficher `examples/passeport.webp` en plein écran]**

> "Passons à la pratique. Voici un passeport de test — évidemment ce sont des données fictives, pas de vrais documents clients.
>
> Regardez cette image : même pour un humain, lire la zone MRZ en bas, ces deux lignes de caractères, c'est fastidieux."

**[Écran : basculer sur le terminal, lancer `just passeport`]**

> "Je lance le traitement."

**[Pendant que ça tourne (~3-4 sec)]**

> "Derrière, le LLM reçoit l'image, la classifie — c'est la RAD — puis extrait les données — c'est la LAD — et enfin Pydantic valide le tout."

**[Résultat affiché]**

> "Voilà. **Classification** : passeport, avec un score de confiance. Puis toutes les données extraites : nom, prénom, date de naissance, numéro, dates d'émission et d'expiration, la MRZ complète... Tout structuré, tout validé.
>
> Et vous voyez le coût en bas : quelques fractions de centimes par document."

**[Écran : basculer sur le deuxième terminal avec le résultat CNI pré-lancé]**

> "Et voilà la même chose pour une carte d'identité. Différent format, différentes données, mais **aucun changement de code, aucun réentraînement**. Le LLM s'adapte."

---

## PHASE 5 — L'impact et les résultats (4:30 - 5:15)

> "Récapitulons ce qu'on vient de voir :
>
> - **5 types de documents** supportés : CNI, passeport, permis de conduire, justificatif de domicile, RIB
> - **800 lignes de Python** au total. En deep learning classique, c'est 10 000 à 15 000 lignes sans compter les scripts d'entraînement
> - **Développement total : 2 jours.** Contre 6 mois avant.
>
> Et en termes de performance : sur un autre projet client avec des documents fiscaux, sur **6 000 documents validés**, j'obtiens **100% de précision sur la classification** et **98.7% sur l'extraction** — et ça inclut des cases à cocher.
>
> D'ailleurs les cases à cocher, c'est le cas qui tue. Un permis de conduire avec ses 14 catégories ? En deep learning classique : 40 à 60 heures de développement — annotation, détection, classification binaire. Avec un LLM multimodal : **15 minutes**. Il voit les cases, il comprend lesquelles sont cochées."

---

## PHASE 6 — Le message à retenir (5:15 - 5:45)

> "Un dernier point important : comme ce sont des données confidentielles, il convient de faire tourner ça dans un **environnement sécurisé**. Ici on utilise Vertex AI en Europe, mais on peut aussi héberger son propre LLM si nécessaire. L'architecture est découplée du provider.
>
> Ce que je veux que vous reteniez, c'est que pour faire de la RAD/LAD aujourd'hui, vous avez besoin de **trois choses** :
> 1. Un **prompt** bien écrit qui guide le modèle
> 2. Un **schéma Pydantic** qui structure et valide la sortie
> 3. Des **règles métier** qui contrôlent les hallucinations
>
> C'est ça le changement de paradigme. On passe de mois d'entraînement à des jours de développement.
>
> Est-ce que vous voulez que je teste un autre type de document, ou on passe aux questions ?"

---

## Préparation avant la démo

### Commandes à préparer

```bash
# Terminal 1 — prêt à lancer en live
just passeport

# Terminal 2 — pré-lancer AVANT la démo (résultat déjà affiché)
just cni
```

### Fichiers à avoir ouverts dans VS Code (dans cet ordre d'onglets)

1. `src/chains/prompts.py` — scrollé sur PROMPT_CLASSIFICATION
2. `src/chains/schemas/kyc_schemas.py` — scrollé sur la classe Passeport
3. `examples/passeport.webp` (preview)
4. Terminal 1 prêt
5. Terminal 2 avec résultat CNI

### Backup plan

- Si le terminal plante ou la latence est trop longue : "Pendant que ça tourne, laissez-moi vous montrer le code..." → basculer sur les schemas
- Si Vertex AI est down : avoir des **screenshots des résultats** prêts dans un dossier `backup/`
- Avoir le résultat CNI pré-lancé = filet de sécurité

### Tips de présentation

- **Rythme** : ni trop rapide ni trop lent. Tu as 5-6 min, profites-en pour laisser les gens absorber
- **Public mixte** : quand tu montres du code, explique ce que ça fait en termes simples. "Ce champ dit au modèle ce qu'on attend" plutôt que "c'est un Field avec une description Pydantic"
- **Impact** : insiste sur les chiffres avant/après (6 mois → 2 jours, 100k€ → quelques euros)
- **Transition naturelle** : chaque phase amène la suivante. Problème → solution (prompt) → comment structurer (Pydantic) → preuve (live) → résultats → message clé

---

## FAQ — Réponses aux questions

### Questions critiques

#### "Comment vous gérez le RGPD / la confidentialité des données ?"

> "C'est LA bonne question dans le bancaire. On a traité ça à trois niveaux :
>
> **Infrastructure** : Vertex AI en Europe (Frankfurt). Les données ne quittent jamais l'UE. Certifié ISO 27001, SOC 2.
>
> **Contractuel** : Google signe un DPA — Data Processing Agreement — qui garantit qu'aucune donnée client n'entraîne leurs modèles. Zéro rétention après traitement.
>
> **Métier** : Chez nous, la DPO a validé avant le pilote. Le DPIA a été positif notamment parce qu'on remplace un process manuel où des humains voient exactement les mêmes données.
>
> Et chaque appel API est loggé et auditable."

#### "Et si demain Google change son pricing ou ses conditions ?"

> "On a trois parades :
>
> **Architecture découplée** : notre code n'est pas lié à Vertex AI. On peut basculer sur Claude, GPT-4V ou Mistral en changeant une vingtaine de lignes.
>
> **Exit strategy** : les modèles open-source multimodaux progressent vite. En quelques mois, le self-hosted devient viable si nécessaire.
>
> **Pricing actuel** : à 0.005€ par document, même si ça double, on reste 100 fois moins cher que l'ancien process."

#### "C'est en production ou c'est un POC ?"

> "Le démonstrateur que je vous montre ici est un POC qui illustre l'approche. Sur un autre périmètre, on a validé l'approche sur 6 000 documents réels avec les résultats que j'ai mentionnés. L'objectif est d'industrialiser ça avec les bonnes briques de sécurité et de monitoring."

### Questions probables

#### "Comment vous gérez les hallucinations ?"

> "Le LLM extrait, les règles métier valident. Exemple concret : sur un IBAN, on vérifie le checksum modulo 97. Si ça ne passe pas, rejet automatique et revue humaine.
>
> On ne fait jamais confiance aveuglément à une sortie de modèle. C'est tout l'intérêt du structured output avec Pydantic : on a un filet de sécurité typé et validé."

#### "Et pour les documents de mauvaise qualité ou manuscrits ?"

> "Le LLM est plus robuste que les anciens OCR sur les documents dégradés. Il utilise le contexte global pour interpréter les caractères ambigus — là où un OCR classique travaille caractère par caractère.
>
> Mais on a un seuil de confiance. En dessous de 85%, on route vers une revue humaine. Environ 5% des documents. L'humain reste dans la boucle."

#### "Pourquoi pas un modèle open-source on-premise ?"

> "C'est l'option la plus sécurisée, mais aujourd'hui les modèles open-source multimodaux ont encore 6 à 12 mois de retard sur les APIs propriétaires en compréhension visuelle. Pour du KYC bancaire, on ne peut pas se permettre 5-10% de précision en moins.
>
> Et le self-hosting, c'est des GPU A100/H100, une équipe infra, 50k€/an minimum. Avec l'API, on est à 2k€/an pour notre volume.
>
> Mais l'architecture est prête à basculer le jour où les modèles open-source rattrapent."

#### "Ça coûte combien ?"

> "Environ 0.005€ par document avec Gemini. Un dossier KYC complet — identité + justificatif + RIB — c'est moins de 5 centimes."

#### "Temps de traitement réel ?"

> "2 à 4 secondes par document. Pour un dossier KYC complet, on est à environ 10 secondes end-to-end. L'ancien process avec traitement humain : 48 heures minimum."

#### "C'est quoi l'équipe nécessaire ?"

> "Avant : 3 à 5 ML engineers + 2-3 annotateurs pendant 6 mois. Maintenant : 1 développeur pendant 2 jours. C'est la vraie démocratisation de l'IA."

### Questions bonus auxquelles penser

#### "Comment vous mesurez la qualité en production ?"

> "Trois KPIs : taux d'extraction réussie (cible 95%), taux de rejet automatique (cible < 5%), taux d'erreur détecté en revue humaine (cible < 1%). On échantillonne 2% des documents pour audit manuel hebdomadaire."

#### "Et l'explicabilité pour les auditeurs ?"

> "Le prompt est versionné dans Git. Les règles métier sont explicites dans le code. Un auditeur peut relire le prompt et comprendre exactement ce qu'on demande au modèle. C'est plus explicable qu'un CNN à 10 millions de paramètres."

#### "Comment vous gérez l'évolution des formats de documents ?"

> "C'est un des gros avantages de l'approche LLM. Si le format d'une CNI change, avec du deep learning classique il faut réannoter et réentraîner. Avec un LLM, il suffit d'adapter le prompt ou le schéma. Pas de nouveau dataset, pas de réentraînement."

#### "Est-ce que ça marche pour des documents dans d'autres langues ?"

> "Les LLMs multimodaux sont nativement multilingues. On peut traiter des documents en anglais, espagnol, arabe... Il suffit d'adapter le prompt. On a testé sur des passeports étrangers sans aucun changement de code."

#### "Et si le modèle se trompe de classification ?"

> "C'est pour ça qu'on a le score de confiance. En dessous d'un certain seuil, on peut demander une double vérification — soit un deuxième appel au LLM avec un prompt différent, soit un routage vers un humain. En pratique, sur nos tests, la classification est à 100%."

#### "Comment vous gérez la montée en charge ?"

> "L'API Vertex AI scale automatiquement. On peut paralléliser les appels : 10, 50, 100 documents en simultané. C'est l'avantage d'une architecture cloud-native. Pas de GPU à provisionner, pas de queue à gérer."
