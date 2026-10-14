import math  # Permet de vérifier qu’un nombre est fini.
import requests  # Permet d’envoyer les demandes HTTP au serveur.

URL_DESSIN = "http://127.0.0.1:8001/draw"  # Définit l’adresse de réception des formes.

FORMES = {  # Associe chaque choix du menu au nom attendu par l’API.
    "1": "point",  # Associe le choix 1 au point.
    "2": "line",  # Associe le choix 2 à la ligne.
    "3": "circle",  # Associe le choix 3 au cercle.
    "4": "rectangle",  # Associe le choix 4 au rectangle.
    "5": "square",  # Associe le choix 5 au carré.
}  # Termine le dictionnaire des formes.


def lire_nombre(message: str, strictement_positif: bool = False) -> float:  # Lit une coordonnée ou une dimension.
    while True:  # Recommence tant que la saisie est incorrecte.
        try:  # Tente de convertir la saisie en nombre.
            valeur = float(input(message).replace(",", "."))  # Accepte le point ou la virgule comme séparateur décimal.
        except ValueError:  # Intercepte une saisie qui ne représente pas un nombre.
            print("Michel, saisis un nombre valide.")  # Explique la correction attendue.
            continue  # Recommence la saisie.
        if not math.isfinite(valeur):  # Refuse les valeurs infinies et les valeurs indéfinies.
            print("Le nombre doit être fini.")  # Explique pourquoi la valeur est refusée.
            continue  # Recommence la saisie.
        if valeur < 0 or (strictement_positif and valeur == 0):  # Vérifie les limites des coordonnées et dimensions.
            print("Valeur attendue : supérieure à zéro." if strictement_positif else "Valeur attendue : zéro ou plus.")  # Précise la limite applicable.
            continue  # Recommence la saisie.
        return valeur  # Renvoie le nombre validé.


def lire_couleur() -> list[int]:  # Demande les trois composantes de la couleur.
    couleur = []  # Prépare la liste des composantes rouge, verte et bleue.
    for composante in ("Rouge", "Vert", "Bleu"):  # Demande chaque composante dans l’ordre prévu par l’API.
        while True:  # Recommence tant que cette composante est incorrecte.
            try:  # Tente de convertir la saisie en entier.
                valeur = int(input(f"{composante} (entier entre 0 et 255) : "))  # Lit la valeur de la composante.
            except ValueError:  # Intercepte une saisie qui n’est pas un entier.
                print("Saisis un nombre entier entre 0 et 255.")  # Explique le format attendu.
                continue  # Recommence la saisie de cette composante.
            if 0 <= valeur <= 255:  # Vérifie les limites autorisées pour une couleur.
                couleur.append(valeur)  # Ajoute la composante à la liste.
                break  # Passe à la composante suivante.
            print("La valeur doit être comprise entre 0 et 255.")  # Signale une composante hors limites.
    return couleur  # Renvoie les trois composantes validées.


def preparer_forme(type_forme: str) -> dict:  # Construit les données attendues par l’API.
    forme = {"shape": type_forme}  # Indique le type de forme demandé.
    if type_forme == "line":  # Demande les deux extrémités d’une ligne.
        forme["x1"] = lire_nombre("X du début : ")  # Lit la position horizontale du début.
        forme["y1"] = lire_nombre("Y du début : ")  # Lit la position verticale du début.
        forme["x2"] = lire_nombre("X de la fin : ")  # Lit la position horizontale de la fin.
        forme["y2"] = lire_nombre("Y de la fin : ")  # Lit la position verticale de la fin.
    else:  # Demande une position pour les autres formes.
        if type_forme == "circle":  # Précise le repère utilisé pour un cercle.
            print("Pour le cercle, X et Y représentent son centre.")  # Explique la position demandée.
        elif type_forme in ("rectangle", "square"):  # Précise le repère des rectangles et carrés.
            print("X et Y représentent le coin supérieur gauche.")  # Explique la position demandée.
        forme["x"] = lire_nombre("X : ")  # Lit la position horizontale.
        forme["y"] = lire_nombre("Y : ")  # Lit la position verticale.
        if type_forme == "circle":  # Demande la dimension du cercle.
            forme["radius"] = lire_nombre("Rayon : ", True)  # Lit un rayon strictement positif.
        elif type_forme == "rectangle":  # Demande les dimensions du rectangle.
            forme["width"] = lire_nombre("Largeur : ", True)  # Lit une largeur strictement positive.
            forme["height"] = lire_nombre("Hauteur : ", True)  # Lit une hauteur strictement positive.
        elif type_forme == "square":  # Demande la dimension du carré.
            forme["cote"] = lire_nombre("Longueur du côté : ", True)  # Lit un côté strictement positif.
    forme["color"] = lire_couleur()  # Ajoute la couleur choisie.
    return forme  # Renvoie les données complètes de la forme.


def envoyer_forme(forme: dict) -> None:  # Transmet une forme au serveur.
    try:  # Encadre la communication pour gérer les erreurs.
        reponse = requests.post(URL_DESSIN, json=forme, timeout=15)  # Envoie les données au format JSON avec un délai d’attente.
        reponse.raise_for_status()  # Signale une réponse HTTP indiquant un échec.
    except requests.Timeout:  # Intercepte un dépassement du délai d’attente.
        print("Délai dépassé : vérifie les tableaux avant de renvoyer la forme, car elle a pu être reçue.")  # Évite un renvoi involontaire en double.
        return  # Termine cette tentative d’envoi.
    except requests.HTTPError:  # Intercepte une réponse d’erreur du serveur.
        print(f"Demande refusée ou erreur du serveur : HTTP {reponse.status_code}.")  # Affiche le code reçu.
        print(reponse.text)  # Affiche les précisions transmises par le serveur.
        return  # Termine cette tentative d’envoi.
    except requests.RequestException as erreur:  # Intercepte les autres problèmes de communication.
        print(f"Communication impossible avec le serveur : {erreur}")  # Affiche le problème rencontré.
        return  # Termine cette tentative d’envoi.
    try:  # Vérifie que la réponse contient le résultat attendu.
        resultat = reponse.json()  # Convertit la réponse JSON en données Python.
        destinataires = resultat["destinataires"]  # Récupère le nombre de tableaux auxquels le serveur a envoyé la forme.
    except (ValueError, KeyError, TypeError):  # Intercepte une réponse inattendue.
        print("Réponse du serveur inattendue : vérifie les tableaux avant de réessayer.")  # Signale que le résultat ne peut pas être confirmé.
        return  # Termine le traitement de cette réponse.
    print(f"Forme transmise à {destinataires} tableau(x).")  # Affiche le résultat annoncé par le serveur.
    if destinataires == 0:  # Vérifie si aucun tableau n’était disponible.
        print("Ouvre un tableau dans le navigateur avant le prochain envoi.")  # Explique comment recevoir les prochaines formes.


def main() -> None:  # Organise le menu et les envois successifs.
    print("Client du tableau interactif — Michel Jazeron")  # Présente le programme.
    print("Contact : michel.jazeron@gmail.com")  # Indique l’auteur du projet.
    print("Tableau : 1 000 × 600 pixels ; origine en haut à gauche.")  # Rappelle le repère du dessin.
    print("Les parties situées hors du tableau ne seront pas visibles.")  # Explique la limite de la surface d’affichage.
    while True:  # Permet d’envoyer plusieurs formes sans relancer le programme.
        print("\n1. Point | 2. Ligne | 3. Cercle | 4. Rectangle | 5. Carré | 0. Quitter")  # Affiche les choix disponibles.
        choix = input("Michel, choisis une forme : ").strip()  # Lit le choix et retire les espaces inutiles.
        if choix == "0":  # Détecte la demande de fermeture.
            print("À bientôt, Michel.")  # Confirme la fermeture du client.
            break  # Termine la boucle du menu.
        if choix not in FORMES:  # Vérifie que le choix correspond à une forme.
            print("Choisis un numéro entre 0 et 5.")  # Indique les choix autorisés.
            continue  # Réaffiche le menu.
        forme = preparer_forme(FORMES[choix])  # Demande les paramètres de la forme sélectionnée.
        envoyer_forme(forme)  # Transmet la forme au serveur.


if __name__ == "__main__":  # Lance le menu uniquement lorsque ce fichier est exécuté directement.
    try:  # Permet une fermeture propre pendant une saisie.
        main()  # Démarre le client interactif.
    except (KeyboardInterrupt, EOFError):  # Intercepte Ctrl+C ou la fermeture de l’entrée du terminal.
        print("\nClient fermé, Michel.")  # Confirme l’arrêt sans afficher de trace d’erreur.