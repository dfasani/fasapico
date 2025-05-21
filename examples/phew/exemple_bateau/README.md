# 🚤 Serveur Autopilote pour Bateau - Raspberry Pi Pico W

Ce projet permet de piloter un petit bateau via un Raspberry Pi Pico W en utilisant une interface web locale (WiFi) et un mode autopilote. Il s'appuie sur la bibliothèque `phew` pour créer un serveur HTTP minimaliste accessible en point d'accès.
Cela permet de commander et relever des informations sur le bateau sans aucune infrastructure (pas de broker MQTT, pas d'accès à internet nécessaire)

## 🧩 Fonctionnalités

- **Contrôle manuel du safran et du moteur** via des requêtes HTTP :
  - `/safran?angle=30` : Oriente le safran à +30°.
  - `/vitesse?v=60` : Fait avancer le moteur à 60% de sa puissance.
- **Mode autopilote** activable via :
  - `/autopilote?etat=on` ou `off` : Active/désactive le mode de navigation automatique vers l'ICAM Vannes.
- **Capteurs simulés** :
  - GPS simulé avec une dérive réaliste.
  - Cap compas simulé avec bruit aléatoire.
- **Serveur HTTP embarqué** en mode point d'accès WiFi (`Bateau_Pico` / mot de passe : `motdepasse`).
- **État consultable** à tout moment :
  - `/etat` : Affiche le cap, les coordonnées GPS actuelles et l'état du pilote auto.

## 📦 Composants matériels

- Raspberry Pi Pico W
- Servo-moteur pour le **safran** (connecté à la broche GP15)
- Moteur à courant continu + Pont en H (L298) :
  - `ENA` : GP16 (PWM)
  - `IN1` : GP17
  - `IN2` : GP18

## 🔧 Fichiers

- `bateau_avec_pilote_auto.py` : Code principal du serveur, des capteurs simulés et du pilote automatique.
- `README.md` : Ce fichier de documentation.

## 🧠 Pilotage automatique

L'autopilote :
- Simule la lecture GPS et de cap,
- Calcule l'angle entre la position actuelle et la destination (ICAM Vannes),
- Corrige dynamiquement le cap à l'aide du safran,
- Contrôle le moteur pour maintenir la vitesse.

## 🛠️ À faire / Idées d'amélioration

- Intégration d’un vrai module GPS (ex. NEO-6M).
- Utilisation d’un capteur compas (ex. HMC5883L ou LSM303).
- Interface web utilisateur pour pilotage en direct.
- Application mobile qui se connecte directement et envoie des requêtes

## 🧪 Exemple de test rapide

1. Démarre le Pico : il crée un point d'accès WiFi `Bateau_Pico`.
2. Connecte-toi avec ton smartphone ou PC (mot de passe : `motdepasse`).
3. Accède à `http://192.168.4.1/safran?angle=30` pour tourner le safran.
4. Lance `/autopilote?etat=on` pour activer la navigation automatique.

---

© Projet pédagogique ICAM – Vannes. Développé avec ❤️ par David Fasani.
