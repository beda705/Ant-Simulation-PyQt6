#Simulation de Colonie de Fourmis V1.0

Simulation multi-agents interactive développée en Python avec PyQt6. Elle modélise le comportement complexe d'une colonie de fourmis cherchant de la nourriture grâce à un système de phéromones dynamiques.

#Fonctionnalités

- **Configuration interactive** : Placez vos nids et vos sources de nourriture où vous le souhaitez sur la carte.
- **Système d'obstacles** : Dessinez des murs avec l'outil crayon pour tester l'intelligence de vos fourmis.
- **Algorithme de Phéromones** : 
  - Les fourmis déposent des traces chimiques lorsqu'elles rentrent au nid.
  - Les autres fourmis suivent ces traces pour optimiser leur chemin.
  - Évaporation naturelle des phéromones au fil du temps.
- **Multi-threading** : Chaque fourmi tourne sur son propre thread pour une simulation fluide.
- **Gestion de la vitesse** : Contrôlez la rapidité de la simulation en temps réel.
- **Multi-colonies** : Ajoutez plusieurs nids de couleurs différentes.
