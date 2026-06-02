# EnerAI-Africa
# Présentation du projet

EnerAI Africa est une plateforme intelligente de gestion énergétique conçue pour optimiser l'utilisation des systèmes énergétiques hybrides dans les infrastructures africaines. Le système exploite l'Intelligence Artificielle (IA) et le Machine Learning (ML) afin de prédire la consommation énergétique, estimer la production solaire et recommander la source d'énergie la plus adaptée parmi le solaire, les batteries, le réseau électrique et les groupes électrogènes.

L'objectif est de réduire les coûts énergétiques, améliorer la continuité de service et favoriser l'utilisation des énergies renouvelables en Afrique.

# Problématique

Dans de nombreux pays africains, les ménages, entreprises, établissements scolaires, centres de santé et administrations publiques sont confrontés à une alimentation électrique instable.

Pour garantir la disponibilité de l'énergie, ils utilisent souvent plusieurs sources :

- Réseau électrique public ;
- Panneaux solaires photovoltaïques ;
- Batteries de stockage ;
- Groupes électrogènes.

Cependant, le choix de la source d'énergie est généralement effectué de manière manuelle ou à l'aide de règles simples, ce qui entraîne :

- Une consommation excessive de carburant ;
- Des coûts d'exploitation élevés ;
- Une mauvaise valorisation de l'énergie solaire ;
- Des interruptions de service ;
- Une faible efficacité énergétique.

Une solution intelligente capable d'analyser les données et de prendre des décisions optimales est donc nécessaire.

# Objectif Général

Développer une plateforme basée sur l'Intelligence Artificielle permettant de prédire les besoins énergétiques et de recommander automatiquement la source d'énergie la plus efficace à utiliser à un instant donné.

# Objectifs Spécifiques
- Collecter et traiter des données énergétiques et météorologiques.
- Prédire la consommation électrique future à l'aide du Machine Learning.
- Estimer la production d'énergie solaire.
- Optimiser le choix de la source d'énergie.
- Réduire l'utilisation des énergies fossiles.
- Fournir un tableau de bord interactif de suivi énergétique.
- Préparer l'automatisation du système à l'aide d'un ESP32.
  
# Fonctionnalités Principales
- Module d'acquisition des données
- Collecte des données de consommation électrique ;
- Intégration des données météorologiques ;
- Suivi de la production solaire.
- Module d'Intelligence Artificielle
- Prévision de la consommation énergétique ;
- Prévision de la production solaire ;
- Analyse des tendances de consommation.
- Moteur de Décision
- Recommandation intelligente de la source d'énergie ;
- Priorisation des énergies renouvelables ;
- Réduction des coûts d'exploitation.

# Tableau de Bord
- Visualisation en temps réel ;
- Historique des consommations ;
- Prévisions énergétiques ;
- Recommandations du système ;
- Estimation des économies réalisées.

# Module Embarqué (Phase future)
- Communication avec ESP32 ;
- Commande de relais ;
- Basculement automatique entre les sources d'énergie.

# Technologies Utilisées
Développement: Python
Analyse de données:
- Pandas
- NumPy
Intelligence Artificielle:
- Scikit-Learn
- XGBoost
Visualisation
- Matplotlib
- Streamlit
Base de données: SQLite
Système embarqué: ESP32
Gestion de versions
- Git
- GitHub


 📂 Organisation du dépôt
- data : jeux de données bruts et nettoyés
- notebooks : notebooks Jupyter pour exploration et prototypage
- src : code source principal (Python, scripts utilitaires)
- docs : documentation technique et guides
- dashboard : applications interactives (Streamlit, Dash)
- hardware : schémas électroniques, code embarqué
- models : modèles entraînés et checkpoints
- reports : rapports et présentations
- README.md : ce fichier



