

- commencer par une problématique métier par exemple : il vous ai sûrement déjà arriver de devoir classifier et extraire des informations de milliers voire de millions de documents ? en tout cas c'est le problème de la KYC qui est Know Your Customer (CNI, passeports, justificatifs de domiciles etc), et le client nous envoie ces documents et aimeraient qu'on puisse extraire les informations en temps réel.

- la première étape c'est de classifier c'est ce qu'on appelle la RAD (reconnaissance automatique de documents)
- puis après la deuxième étape c'est de récupérer ces informations dedans avec la LAD (lecture automatique de documents)

et là on commence notre pitch:
- avant, pour faire ça, il fallait entraîner des modèles de Deep Learning, ça requierait plusieurs étapes: collecte de dataset, annotations de dataset par des annotateurs externes, review de ces annotations et recorrection si besoin, une fois qu'on a les annotations finales, entrainement d'un modèle de Computer vision et enfin évaluation du modèle de computer vision, et réentrainer tant qu'on a pas de perfs satisfaisantes
- mais maintenant ce que je veux vous montrer c'est que tous ces efforts sont vachement réduits grâce aux LLMs (là montrer les prompts de RAD puis de LAD pour passeport par ex), voilà on peut faire ça avec un simple prompt : expliquer rapidement ce qu'il y a dans le prompt de la RAD et dans le prompt de la LAD (aide moi à faire ça: schéma, pièges, key exemples etc)

- là question que vous allez probablement me poser comme question comment je structure tout ça correctement ? et là parler du structured output (là montrer un exemple pour passeport par ex) : schéma pydantic qui va nous permettre d'extraire les différents champs + structured output -> pourquoi ? permet de limiter les hallucinations, de rendre le système plus déterministe car à l'origine il est probabiliste, et là expliquer rapidement le code (typage, description pour LLM en sortie etc), (donc dèls le début peut être mettre à gauche le prompt et à droit les basemodel etc), (il faut qu'à la fin les spectateurs ressortent outillés)

- comme ces données sont confidentiels, là en effet ce sont des cas de test non réels, mais il convient bien sûr de tourner cela dans un environnement sécurisé, donc soit vous hostez votre propre LLM soit avec un accord valable chez votre cloud provider

- et là on lance un exemple pour passeport par ex avec just passeport (on montre l'image du passeport sur un côté splitté pour montrer que même pour un humain c'est compliqué à lire l'image et sur l'autre côté splitté montrer autre chose ? ou on montre juste l'image?) (tu peux lancer toi même pour voir l'output et décrire l'output en temps réel: d'abord partie RAD puis partie LAD)

- et après on peut faire exactement la même chose pour la CNI ou un autre doc 

- on peut dire en parallèle que sur un autre use case j'ai actuellement sur 6000 documents validés : 100% de précision sur la RAD et 98.7% sur la LAD (avec des cases à cocher), et j'ai fait un trade-off Gemini Flash sur la RAD et Gemini Pro sur la LAD

- et après demander si vous voulez que je teste un autre document ou qu'on passe aux questions
