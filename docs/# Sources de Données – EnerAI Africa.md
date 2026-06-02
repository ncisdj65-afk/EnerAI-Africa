# Sources de Données – EnerAI Africa

## Objectif

Ce document recense l'ensemble des jeux de données utilisés dans le projet EnerAI Africa pour l'entraînement des modèles de Machine Learning et la validation du système de gestion énergétique intelligente.

---

# 1. Données de Consommation Électrique

## Source

Nom du dataset : Household Data

Lien : https://data.open-power-system-data.org/household_data/latest/

Fournisseur : Open Power System Data

Format :  CSV


Variables disponibles :

* Date
* Heure
* Consommation (kWh)
* Puissance (kW)
* Tension (V)
* Courant (A)

Utilisation prévue :

Prédiction de la consommation énergétique future.

Statut :

* [ ] Identifiée
* [ ] Téléchargée
* [ ] Nettoyée
* [ ] Utilisée

---

# 2. Données Météorologiques

## Source

Nom du dataset : NASA POWER

Lien : _______________________

Format :

* [ ] CSV
* [ ] API

Variables disponibles :

* Température
* Humidité
* Vitesse du vent
* Couverture nuageuse

Utilisation prévue :

Amélioration des prédictions énergétiques.

Statut :

* [ ] Identifiée
* [ ] Téléchargée
* [ ] Nettoyée
* [ ] Utilisée

---

# 3. Données Solaires

## Source

Nom du dataset : _______________________

Lien : _______________________

Format :

* [ ] CSV
* [ ] API

Variables disponibles :

* Irradiation solaire
* Production photovoltaïque
* Durée d'ensoleillement

Utilisation prévue :

Prédiction de la production solaire.

Statut :

* [ ] Identifiée
* [ ] Téléchargée
* [ ] Nettoyée
* [ ] Utilisée

---

# Tableau de Synthèse

| Source      | Type         | Format  | Utilisation            | Statut       |
| ----------- | ------------ | ------- | ---------------------- | ------------ |
| NASA POWER  | Météo        | CSV/API | Prévision solaire      | Identifiée   |
| À compléter | Consommation | CSV     | Prévision consommation | En recherche |
| À compléter | Solaire      | CSV     | Production solaire     | En recherche |

---

# Remarques

* Les datasets doivent être libres d'utilisation.
* Les données doivent couvrir plusieurs mois ou années.
* Les séries temporelles horaires sont privilégiées.
* Toutes les sources doivent être documentées pour assurer la reproductibilité du projet.
