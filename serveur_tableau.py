# Auteur : Michel Jazeron — michel.jazeron@gmail.com
from pathlib import Path  # Construit un chemin indépendant du dossier de lancement.
from fastapi.responses import FileResponse  # Permet de transmettre la page HTML au navigateur.
import asyncio  # Gère les opérations réseau asynchrones.
from typing import Annotated, Literal  # Décrit les types et les valeurs autorisées.
from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect  # Importe le serveur et les connexions.
from pydantic import BaseModel, ConfigDict, Field  # Importe la validation des données.

app = FastAPI(title="Tableau interactif — Michel Jazeron")  # Crée l’application.
tableaux: set[WebSocket] = set()  # Conserve les tableaux actuellement connectés.
verrou = asyncio.Lock()  # Garantit le même ordre de diffusion pour tous les tableaux.

Coordonnee = Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)]  # Accepte une position positive ou nulle et finie.
Dimension = Annotated[float, Field(gt=0, allow_inf_nan=False, strict=True)]  # Accepte une dimension strictement positive et finie.
Composante = Annotated[int, Field(ge=0, le=255, strict=True)]  # Limite une composante de couleur à un entier entre 0 et 255.


class FormeBase(BaseModel):  # Définit les propriétés communes aux formes.
    model_config = ConfigDict(extra="forbid")  # Refuse les champs inconnus pour détecter les fautes de saisie.
    color: tuple[Composante, Composante, Composante]  # Exige trois composantes : rouge, vert et bleu.


class Point(FormeBase):  # Décrit un point.
    shape: Literal["point"]  # Impose le nom prévu par l’API.
    x: Coordonnee  # Définit la position horizontale.
    y: Coordonnee  # Définit la position verticale.


class Ligne(FormeBase):  # Décrit une ligne entre deux points.
    shape: Literal["line"]  # Impose le nom prévu par l’API.
    x1: Coordonnee  # Définit la position horizontale du départ.
    y1: Coordonnee  # Définit la position verticale du départ.
    x2: Coordonnee  # Définit la position horizontale de l’arrivée.
    y2: Coordonnee  # Définit la position verticale de l’arrivée.


class Cercle(FormeBase):  # Décrit un cercle.
    shape: Literal["circle"]  # Impose le nom prévu par l’API.
    x: Coordonnee  # Définit la position horizontale du centre.
    y: Coordonnee  # Définit la position verticale du centre.
    radius: Dimension  # Définit le rayon du cercle.


class Rectangle(FormeBase):  # Décrit un rectangle.
    shape: Literal["rectangle"]  # Impose le nom prévu par l’API.
    x: Coordonnee  # Définit la position horizontale du coin supérieur gauche.
    y: Coordonnee  # Définit la position verticale du coin supérieur gauche.
    width: Dimension  # Définit la largeur.
    height: Dimension  # Définit la hauteur.


class Carre(FormeBase):  # Décrit un carré.
    shape: Literal["square"]  # Impose le nom prévu par l’API.
    x: Coordonnee  # Définit la position horizontale du coin supérieur gauche.
    y: Coordonnee  # Définit la position verticale du coin supérieur gauche.
    cote: Dimension  # Définit la longueur du côté.


Forme = Annotated[Point | Ligne | Cercle | Rectangle | Carre, Body(discriminator="shape")]  # Sélectionne les règles selon la forme.


@app.post("/draw")  # Reçoit les demandes de dessin conformément au sujet.
async def dessiner(forme: Forme) -> dict:  # Traite uniquement une forme validée.
    donnees = forme.model_dump(mode="json")  # Convertit la forme en données compatibles avec JSON.
    destinataires = 0  # Compte les connexions auxquelles la forme a été envoyée.
    async with verrou:  # Évite que plusieurs demandes mélangent leurs diffusions.
        for tableau in tuple(tableaux):  # Parcourt une copie des connexions.
            try:  # Tente l’envoi à ce tableau.
                await asyncio.wait_for(tableau.send_json(donnees), timeout=2)  # Limite l’attente pour un destinataire lent.
                destinataires += 1  # Compte un envoi réussi, sans présumer du rendu graphique.
            except (WebSocketDisconnect, OSError, RuntimeError, TimeoutError):  # Traite une connexion inutilisable.
                tableaux.discard(tableau)  # Retire cette connexion des prochains envois.
                try:  # Tente de fermer proprement cette connexion.
                    await asyncio.wait_for(tableau.close(), timeout=1)  # Borne aussi la durée de fermeture.
                except (WebSocketDisconnect, OSError, RuntimeError, TimeoutError):  # Accepte une connexion déjà fermée.
                    pass  # Poursuit la diffusion aux autres tableaux.
    return {"status": "ok", "destinataires": destinataires}  # Confirme le traitement et le nombre d’envois.


@app.websocket("/ws")  # Ouvre le canal utilisé par les tableaux web.
async def connecter_tableau(connexion: WebSocket) -> None:  # Gère la durée de vie d’une connexion.
    await connexion.accept()  # Accepte la connexion du navigateur.
    tableaux.add(connexion)  # Inscrit le tableau parmi les destinataires.
    try:  # Maintient la connexion ouverte.
        while True:  # Attend jusqu’à la déconnexion du navigateur.
            await connexion.receive_text()  # Détecte la déconnexion ; les dessins arrivent uniquement par HTTP.
    except WebSocketDisconnect:  # Traite la fermeture du tableau.
        pass  # Une déconnexion normale ne constitue pas une panne du serveur.
    finally:  # Nettoie la liste même si la connexion se termine sur une erreur.
        tableaux.discard(connexion)  # Retire le tableau déconnecté.
DOSSIER = Path(__file__).resolve().parent  # Repère le dossier contenant le serveur.

@app.get("/")  # Associe l’adresse principale du serveur à la page du tableau.
async def afficher_tableau() -> FileResponse:  # Définit la réponse destinée au navigateur.
    return FileResponse(DOSSIER / "tableau.html")  # Envoie le fichier HTML situé à côté du serveur.