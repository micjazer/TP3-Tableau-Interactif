# Conception — TP3, partie II : tableau interactif

Michel Jazeron — michel.jazeron@gmail.com

## Ma démarche avec l’IA

J’ai utilisé ChatGPT comme aide à la conception, à la programmation et à la compréhension du code. Je lui ai transmis le sujet, les cinq formats de formes imposés par l’API et les contraintes du TP. J’ai demandé de privilégier les bibliothèques vues en cours, des explications en français et un accompagnement étape par étape avec des captures pour mon rapport.

L’IA a proposé l’organisation technique et fourni une grande partie du code commenté. De mon côté, j’ai créé les fichiers sur mon ordinateur, exécuté les commandes et les programmes, puis transmis les résultats pour vérifier chaque étape. Ce document a également été rédigé avec son aide à partir de nos échanges ; je le relis et le personnalise avant la remise.

## Les choix de conception

J’ai confirmé que FastAPI, Uvicorn et requests correspondaient aux outils étudiés en cours. L’application comprend trois éléments : une page HTML/CSS/JavaScript qui affiche les formes, un serveur Python qui les reçoit et les diffuse, et un client Python qui demande leurs paramètres dans le terminal.

Le client utilise POST /draw avec les champs prévus dans le sujet. La page reçoit les formes par WebSocket sur /ws. Cette séparation respecte le fonctionnement demandé : la saisie se fait dans le client Python et l’affichage dans le navigateur.

La solution proposée utilise un repère fixe de 1 000 × 600 pixels, avec un affichage adapté à la largeur de la fenêtre. Les coordonnées restent ainsi identiques entre les tableaux. Le menu en français, l’état de connexion et le compteur de formes rendent le fonctionnement visible pendant les essais.

La vérification des données existe à deux niveaux : le client permet de corriger une saisie et le serveur contrôle les demandes reçues, même lorsqu’elles proviennent d’un autre outil.

## Mes vérifications

J’ai testé les cinq formes dans deux fenêtres de navigateur. J’ai vérifié qu’une couleur valide était acceptée et qu’une composante supérieure à 255 était refusée par le serveur. Dans le client, j’ai essayé une coordonnée contenant du texte, un côté négatif et une couleur hors limites, puis corrigé ces valeurs sans relancer le programme.

J’ai également lancé deux clients Python et constaté que leurs formes apparaissaient sur les deux tableaux connectés. Enfin, j’ai corrigé les caractères ajoutés lors du copier-coller du README avec l’aide de l’IA.

## Les limites de cette version

Le serveur ne conserve pas l’historique des dessins. Une nouvelle page reçoit uniquement les formes envoyées après sa connexion ; une actualisation efface son contenu. Les compteurs de deux pages ouvertes à des moments différents peuvent donc différer.

Le lancement actuel est local et utilise un seul processus serveur. Après une déconnexion, il faut actualiser la page pour se reconnecter. Ces limites sont indiquées dans le README pour rendre l’utilisation prévisible.
