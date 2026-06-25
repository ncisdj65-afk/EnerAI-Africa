# EnerAI-Box — Phase 1 : Acquisition de données avec ESP32

## Objectif

Cette phase valide la première brique physique du projet EnerAI-Africa.

Le prototype EnerAI-Box utilise un ESP32 pour :

- mesurer la température ;
- mesurer l'humidité ;
- mesurer la luminosité ;
- commander un module relais ;
- simuler une première décision énergétique locale.

Cette étape permet de démontrer que le projet n'est pas uniquement logiciel, mais qu'il peut être connecté à un système physique de suivi énergétique.

---

## Matériel utilisé

- ESP32-WROOM-32
- DHT11
- LDR
- Résistance 10 kΩ
- Module relais
- Breadboard
- Fils jumper
- Câble USB

---

## Connexions

### DHT11

| DHT11 | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| DATA | GPIO4 |

### LDR

Montage en diviseur de tension :

```text
3.3V ---- LDR ---- GPIO34 ---- Résistance 10 kΩ ---- GND