# 🎯 DEMO RAPIDE - 2 Minutes Non-Stop

## ⏱️ Script de présentation fluide

---

### 🎬 DÉMARRAGE (0:00 - 0:20)

**[Montrer : examples/passeport.webp et cni.webp côte à côte]**

> "Imaginez : vous devez créer un système qui traite automatiquement des documents KYC pour une banque. 
> Passeports, cartes d'identité, RIB, justificatifs de domicile. Extraction complète, validation métier.
> 
> Il y a 2 ans, ce projet : **6 mois de développement, 100 000 euros, 10 000 images annotées**."

---

### 💡 LA RÉVÉLATION (0:20 - 0:40)

**[Montrer : src/chains/prompts.py - PROMPT_CLASSIFICATION]**

> "Aujourd'hui, regardez ça. Un prompt. Trente lignes de texte.
> 
> **[Lancer : `uv run python src/main.py examples/passeport.webp`]**
> 
> Le LLM **voit** l'image. Il **comprend** que c'est un passeport. 
> Classification : 99% de confiance. **Instantané.**"

---

### ⭐ LE MOMENT FORT (0:40 - 1:10)

**[Montrer : examples/passeport.webp avec les données MRZ visibles]**

> "Mais le vrai changement, c'est l'extraction structurée.
> 
> **[Montrer : terminal - résultat JSON]**
> 
> Numéro de passeport, nom, prénom, dates, nationalité, MRZ complète. 
> Tout extrait. Tout validé par Pydantic. **Automatiquement.**
> 
> **[Montrer : src/chains/schemas/kyc_schemas.py - classe Passeport]**
> 
> Avant : des bounding boxes, du template matching, de l'OCR, du post-processing...
> Des centaines d'heures de code.
> 
> Maintenant : Un schéma Pydantic. **Cinquante lignes.**"

---

### 🚀 L'IMPACT (1:10 - 1:40)

**[Lancer : `uv run python src/main.py examples/cni.webp`]**

> "Même chose avec une carte d'identité. Différent format. Différentes données.
> 
> **[Résultat s'affiche]**
> 
> Aucun changement de code. Aucun ré-entraînement. Le LLM s'adapte.
> 
> **[Montrer rapidement : src/chains/schemas/kyc_schemas.py - classes CarteIdentite, RIB, JustificatifDomicile]**
> 
> CNI, passeport, RIB, justificatifs... Cinq types de documents. 
> Développement total : **2 jours.**"

---

### 💰 LA CONCLUSION (1:40 - 2:00)

**[Afficher : terminal propre, prêt à relancer]**

> "**De 6 mois à 2 jours. De 100k€ à quelques euros d'API calls.**
> 
> Pas de dataset. Pas d'annotation. Pas de GPU. Pas d'entraînement.
> 
> Juste du Python, des prompts bien écrits, et un LLM multimodal.
> 
> C'est ça, la révolution. Et elle est **déjà là**."

---

## 🎯 Commandes à préparer en avance

```bash
# Terminal 1 - Prêt à exécuter
uv run python src/main.py examples/passeport.webp

# Terminal 2 - Prêt à exécuter  
uv run python src/main.py examples/cni.webp
```

## 📂 Fichiers à avoir ouverts dans VS Code

1. `examples/passeport.webp` (preview)
2. `examples/cni.webp` (preview)
3. `src/chains/prompts.py` (lignes 1-50)
4. `src/chains/schemas/kyc_schemas.py` (classe Passeport visible)
5. Terminal prêt

## 💡 Tips

- **Rythme** : Parler vite mais clairement, sans pause
- **Énergie** : Enthousiasme croissant jusqu'à la conclusion
- **Gestes** : Pointer l'écran quand on dit "regardez ça"
- **Silence stratégique** : 1 seconde après "C'est ça, la révolution"
- **Backup** : Si un terminal plante, basculer sur l'autre

## 🎬 Post-démo (si questions)

**Q : "Ça coûte combien ?"**
> "Environ 0.02€ par document avec Gemini. Un traitement KYC complet : 0.10€."

**Q : "C'est précis ?"**  
> "Plus précis que nos anciens modèles CNN. Le LLM comprend le contexte, pas juste des pixels."

**Q : "Et la sécurité ?"**
> "Vertex AI, cloud privé Google, compliance bancaire. Zéro donnée ne quitte notre VPC."
