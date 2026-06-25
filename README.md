## Demonstration Video

A final demonstration video of the EnerAI-Africa prototype is available here:

[Watch the EnerAI-Africa demo](assets/demo/EnerAI_Africa_FINAL_Narcisse_DJAINANTE.mp4)

# EnerAI-Africa

## Présentation du projet

**EnerAI-Africa** est un prototype intelligent combinant **Intelligence Artificielle**, **données météo/solaires** et **IoT embarqué** pour améliorer la gestion énergétique dans les contextes africains.

Le projet vise à prédire la consommation électrique, estimer le contexte solaire et prendre des décisions intelligentes de gestion de charge. Il intègre également un prototype physique appelé **EnerAI-Box**, basé sur un microcontrôleur ESP32, capable de mesurer des données locales et de représenter l’activation ou la désactivation d’une charge non critique.

L’objectif global est de contribuer à une gestion énergétique plus fiable, plus économique et plus favorable aux énergies renouvelables pour les ménages, écoles, centres de santé, administrations, mini-réseaux et infrastructures communautaires en Afrique.

---

## Problématique

Dans de nombreux pays africains, l’alimentation électrique reste instable. Les ménages, entreprises, établissements scolaires, centres de santé et administrations publiques utilisent souvent plusieurs sources d’énergie :

* réseau électrique public ;
* panneaux solaires photovoltaïques ;
* batteries de stockage ;
* groupes électrogènes.

Cependant, le choix de la source d’énergie ou la gestion des charges est souvent manuel ou basé sur des règles simples. Cela peut entraîner :

* une consommation excessive de carburant ;
* des coûts d’exploitation élevés ;
* une mauvaise valorisation de l’énergie solaire ;
* des interruptions de service ;
* une faible efficacité énergétique ;
* une difficulté à anticiper les pics de consommation.

EnerAI-Africa propose une approche basée sur l’IA et l’IoT pour anticiper la demande énergétique et soutenir une prise de décision plus intelligente.

---

## Objectif général

Développer un prototype IA + IoT capable de prédire le contexte énergétique et de recommander une action de gestion de charge en fonction de la demande prévue, du contexte solaire et des mesures locales collectées en temps réel.

---

## Objectifs spécifiques

* Collecter et nettoyer des données de consommation électrique, météo et solaire.
* Construire un modèle de prévision de consommation électrique.
* Intégrer les données météo et solaires dans le pipeline de modélisation.
* Développer une API locale capable de recevoir des données IoT.
* Développer un moteur de décision hybride IA/IoT.
* Connecter un ESP32 à l’API via Wi-Fi.
* Utiliser des capteurs locaux pour mesurer température, humidité et luminosité.
* Représenter physiquement la décision énergétique à l’aide d’une LED simulant une charge non critique.
* Préparer une base évolutive vers la gestion de charges réelles, mini-réseaux et systèmes hybrides solaire-batterie-réseau-groupe électrogène.

---

## Architecture générale

```text
Données historiques
  ├── Consommation électrique
  ├── Données météo
  └── Données solaires
        ↓
Pipeline IA EnerAI-Africa
        ↓
Prévision / estimation du contexte énergétique
        ↓
API FastAPI locale
        ↑
ESP32 EnerAI-Box
  ├── DHT11 : température et humidité
  ├── LDR : luminosité locale
  └── LED GPIO25 : charge non critique simulée
        ↓
Moteur de décision hybride IA/IoT
        ↓
Décision : ON / OFF / économie / protection
```

---

## EnerAI-Box : prototype IoT physique

La partie embarquée du projet est appelée **EnerAI-Box**.

Elle utilise :

* un ESP32 ;
* un capteur DHT11 pour la température et l’humidité ;
* une LDR pour estimer la luminosité locale ;
* une LED sur GPIO25 pour représenter une charge non critique ;
* une connexion Wi-Fi vers une API Python locale.

Le système fonctionne ainsi :

```text
ESP32 → envoie les mesures à l’API FastAPI
API → calcule une décision énergétique hybride
ESP32 → reçoit relay_command
LED GPIO25 → représente l’état de la charge
```

Comportement démontré :

```text
Luminosité faible → solar_status LOW → relay_command OFF → LED éteinte
Luminosité favorable → solar_status GOOD → relay_command ON → LED allumée
Température critique → PROTECTION_MODE → LED éteinte
```

La LED représente une charge non critique. Elle est utilisée pour une démonstration basse tension sûre et fiable.

---

## Moteur de décision hybride IA/IoT

Le moteur de décision ne se base pas uniquement sur la luminosité locale. Il combine plusieurs informations :

* température locale ;
* humidité locale ;
* luminosité locale ;
* consommation prévue ou estimée ;
* niveau de demande énergétique ;
* estimation solaire historique ;
* statut solaire local ;
* état thermique du système.

Exemple de réponse API :

```json
{
  "relay_command": "ON",
  "energy_mode": "NORMAL_SOLAR_MODE",
  "decision": "GOOD_SOLAR_LOAD_ON",
  "predicted_consumption": 0.184,
  "demand_level": "MEDIUM",
  "solar_status": "GOOD",
  "temperature_status": "NORMAL",
  "reason": "Local solar availability is favorable and no critical condition is detected. The non-critical load is allowed."
}
```

---

## Données utilisées

Le prototype utilise plusieurs sources de données :

* données de consommation électrique ;
* données météorologiques ;
* données solaires ;
* données IoT collectées par l’ESP32.

Dans cette version de prototype, certaines données de consommation sont utilisées comme données de référence méthodologique. L’objectif est de démontrer le pipeline complet IA + IoT. Une version opérationnelle devra intégrer des données locales réelles provenant de sites africains pilotes.

---

## Modélisation IA

Le pipeline de Machine Learning permet de :

* nettoyer les données ;
* corriger les incohérences temporelles ;
* générer des variables temporelles ;
* intégrer les variables météo et solaires ;
* entraîner un modèle de prévision ;
* produire une estimation de la demande énergétique.

Le modèle est ensuite exploité dans le moteur de décision hybride pour enrichir la décision envoyée à l’ESP32.

---

## Technologies utilisées

### Intelligence Artificielle et données

* Python
* Pandas
* NumPy
* Scikit-learn
* Joblib

### API et intégration IoT

* FastAPI
* Uvicorn
* JSON HTTP POST

### Système embarqué

* ESP32
* Arduino IDE
* DHT11
* LDR
* LED de statut sur GPIO25
* ArduinoJson

### Gestion de projet

* Git
* GitHub
* Jupyter Notebook
* VS Code

---

## Organisation du dépôt

```text
EnerAI-Africa/
│
├── data/
│   ├── raw/              # Données brutes
│   ├── processed/        # Données nettoyées et datasets de modélisation
│   └── iot/              # Données collectées par l’ESP32
│
├── docs/
│   └── hardware/         # Documentation technique EnerAI-Box
│
├── firmware/
│   ├── esp32_data_acquisition/
│   └── esp32_wifi_sender/
│
├── models/               # Modèles entraînés
│
├── notebooks/            # Notebooks d’exploration et de modélisation
│
├── reports/              # Rapports de projet
│
├── src/
│   ├── data_collection/  # Scripts de collecte de données
│   ├── iot/              # API FastAPI et moteur de décision hybride
│   └── predict.py        # Script de prédiction
│
├── README.md
└── .gitignore
```

---

## Principaux fichiers techniques

```text
src/iot/enerai_iot_api.py
```

API FastAPI recevant les mesures ESP32 et retournant une décision énergétique.

```text
src/iot/enerai_decision_engine.py
```

Moteur de décision hybride IA/IoT.

```text
firmware/esp32_wifi_sender/esp32_wifi_sender.ino
```

Firmware ESP32 pour envoyer les mesures à l’API et appliquer la décision reçue.

```text
data/iot/enerai_box_measurements_sample.csv
```

Échantillon de mesures IoT collectées pendant les tests.

```text
docs/hardware/enerai_box_phase3_hybrid_ai_iot_control.md
```

Documentation de la phase de contrôle hybride IA/IoT.

---

## Lancement de l’API locale

Depuis la racine du projet :

```bash
python -m uvicorn src.iot.enerai_iot_api:app --host 0.0.0.0 --port 8000 --reload
```

Tester dans le navigateur :

```text
http://127.0.0.1:8000
```

Ou depuis un ESP32 connecté au même réseau Wi-Fi :

```text
http://ADRESSE_IP_DU_PC:8000/sensor-data
```

---

## Sécurité et démonstration

Pour la démonstration finale, la LED sur GPIO25 représente une charge non critique basse tension.

Le prototype n’utilise pas de charge 220V. Cette approche permet une démonstration sûre, stable et reproductible.

Une version future pourra intégrer :

* relais industriel ;
* capteur de courant ;
* mesure de puissance réelle ;
* stockage local ;
* tableau de bord ;
* intégration solaire réelle ;
* pilotage de batteries ou micro-réseaux.

---

## Limites actuelles

Cette version est un prototype. Elle démontre l’architecture complète, mais certaines limites restent présentes :

* les données de consommation utilisées ne proviennent pas encore d’un site africain réel ;
* la charge électrique est simulée par une LED ;
* la mesure de puissance réelle n’est pas encore intégrée ;
* la décision énergétique reste basée sur un moteur hybride simple, extensible vers une optimisation plus avancée.

Ces limites sont assumées et constituent les prochaines étapes de développement.

---

## Perspectives

Les prochaines évolutions prévues sont :

* intégration de données réelles de consommation au Tchad ou dans d’autres pays africains ;
* ajout d’un capteur de courant ou d’énergie ;
* développement d’un tableau de bord interactif ;
* estimation des économies de carburant ;
* recommandation automatique entre solaire, batterie, réseau et groupe électrogène ;
* expérimentation dans une école, un centre de santé ou un bâtiment public ;
* extension vers une plateforme de pilotage de mini-réseaux.

---

## Vision

EnerAI-Africa ambitionne de devenir une solution intelligente d’aide à la décision énergétique pour les infrastructures africaines. En combinant prévision IA, données solaires, données météo et IoT embarqué, le projet propose une approche concrète pour améliorer la continuité de service, réduire les coûts énergétiques et accélérer l’intégration des énergies renouvelables.
