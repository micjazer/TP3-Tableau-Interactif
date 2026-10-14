# TP3 — Tableau interactif



Michel Jazeron — michel.jazeron@gmail.com



Un client Python permet de saisir des points, lignes, cercles, rectangles et carrés.

Le serveur FastAPI reçoit les formes par HTTP et les diffuse par WebSocket aux tableaux ouverts dans le navigateur.



## Installation sous Windows / PowerShell



Prérequis : Python 3.13 et un navigateur récent.

Depuis le dossier du projet :



```powershell

python -m venv .venv # Crée l’environnement Python isolé.

.\.venv\Scripts\python.exe -m pip install -r requirements.txt # Installe les dépendances.

```



## Lancement



Dans un premier terminal, depuis le dossier du projet :



```powershell

.\.venv\Scripts\python.exe -m uvicorn serveur_tableau:app --host 127.0.0.1 --port 8001 --no-use-colors # Démarre le serveur local.

```



Ouvrir http://127.0.0.1:8001 dans une ou plusieurs fenêtres.

Attendre l’indication « Connecté » avant d’envoyer des formes.



Dans un second terminal, depuis le même dossier :



```powershell

.\.venv\Scripts\python.exe .\client_tableau.py # Lance la saisie interactive des formes.

```



Choisir une forme et saisir ses paramètres. Plusieurs clients Python peuvent être lancés.

Saisir 0 dans le menu pour quitter le client ; utiliser Ctrl+C dans le terminal du serveur pour l’arrêter.



## Utilisation et limites



- Tableau de 1 000 × 600 pixels, origine en haut à gauche.

- Pour un cercle, X et Y désignent son centre ; pour un rectangle ou un carré, son coin supérieur gauche.

- Couleurs : trois entiers rouge, vert et bleu entre 0 et 255.

- Les formes se superposent dans leur ordre de réception ; les parties hors du tableau sont masquées.

- API : POST /draw pour envoyer une forme ; WebSocket /ws pour la recevoir.

- Les tableaux reçoivent uniquement les nouveaux envois : aucun historique n’est conservé sur le serveur.

- Actualiser une page efface ses dessins. Après une déconnexion, actualiser la page pour se reconnecter.

- Utiliser un seul processus serveur, sans option --workers.

- La commande proposée limite l’accès à cet ordinateur.


