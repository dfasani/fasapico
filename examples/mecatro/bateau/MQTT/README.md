
# 🚤 Serveur Autopilote pour Bateau - Raspberry Pi Pico W

Ce projet permet de piloter un petit bateau via un Raspberry Pi Pico W en utilisant MQTT pour la communication et un mode autopilote.
Il simule les capteurs GPS et cap compas, et permet le contrôle manuel du safran et du moteur.

## 🧩 Fonctionnalités

- **Contrôle manuel du safran et du moteur** via MQTT :
  - Sujet `bateau/safran` : commande l'angle du safran (-90° à +90°).
  - Sujet `bateau/vitesse` : commande la vitesse du moteur (-100% à +100%).  
- **Mode autopilote** activable via MQTT :
  - Sujet `bateau/autopilote` avec payload "on" ou "off" pour activer/désactiver le mode automatique.
- **Capteurs simulés** :
  - GPS avec dérive aléatoire réaliste.
  - Cap compas avec bruit aléatoire.
- **Connexion WiFi** automatique avec vérification de la connectivité.
- **Connexion à un broker MQTT public** (broker.emqx.io) pour publication et réception des commandes.

## 📦 Composants matériels

- Raspberry Pi Pico W
- Servo-moteur pour le **safran** (connecté à la broche GP15)
- Moteur à courant continu + Pont en H (L298) :
  - `ENA` : GP16 (PWM)
  - `IN1` : GP17
  - `IN2` : GP18

## 🔧 Description du code

- Connexion WiFi et vérification d'accès internet.
- Publication périodique des données GPS et cap sur MQTT.
- Réception des commandes MQTT pour contrôle du safran, du moteur et activation du pilote automatique.
- Calcul de l’angle vers la destination (ICAM Bretagne) pour le mode autopilote.
- Gestion des timers pour capteurs simulés et pilotage automatique.

## 🧠 Pilotage automatique

L'autopilote :
- Simule la lecture GPS et de cap,
- Calcule l'angle entre la position actuelle et la destination (ICAM Bretagne),
- Corrige dynamiquement le cap à l'aide du safran,
- Contrôle le moteur pour maintenir la vitesse.

## 🛠️ À faire / Idées d'amélioration

- Intégration d’un vrai module GPS (ex. NEO-6M).
- Utilisation d’un capteur compas réel (ex. HMC5883L ou LSM303).
- Gestion d’erreurs plus robuste sur MQTT.
- Ajout d’une interface web ou application mobile pour contrôle et suivi.
- Ajout de la gestion de la sécurité et des limites physiques.

## 🧪 Exemple d'utilisation

1. Flasher le script sur le Raspberry Pi Pico W.
2. Le dispositif se connecte automatiquement au WiFi `Icam_IOT` avec le mot de passe défini.
3. Connecter un client MQTT (ex. MQTT Explorer) au broker `broker.emqx.io`.
4. Publier des messages sur les topics `bateau/safran`, `bateau/vitesse` ou `bateau/autopilote` pour contrôler le bateau.
5. Consulter les topics `bateau/gps`, `bateau/cap` pour recevoir les données simulées.

---

© Projet pédagogique ICAM – Vannes. Développé avec ❤️ par David Fasani.
