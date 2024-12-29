import sqlite3
import random

# Connexion à la base de données
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row  # Accès aux colonnes par leur nom
c = conn.cursor()

# Fonction pour ajouter une mesure
def ajouter_mesure(valeur, id_capteur_actionneur):
    query = """
    INSERT INTO Mesure (valeur, date_insertion, id_capteur_actionneur)
    VALUES (?, datetime('now'), ?)
    """
    c.execute(query, (valeur, id_capteur_actionneur))
    print(f"Mesure ajoutée : valeur={valeur:.2f}, id_capteur_actionneur={id_capteur_actionneur}")

# Fonction pour ajouter une facture
def ajouter_facture(type_facture, montant, consommation, id_logement):
    query = """
    INSERT INTO Facture (type_facture, date, montant, consommation, id_logement)
    VALUES (?, datetime('now'), ?, ?, ?)
    """
    c.execute(query, (type_facture, montant, consommation, id_logement))
    print(f"Facture ajoutée : type={type_facture}, montant={montant:.2f}, consommation={consommation}, logement={id_logement}")

# Fonction pour insérer plusieurs mesures
def remplir_mesures(nombre_mesures, id_capteur_actionneur):
    for _ in range(nombre_mesures):
        valeur = random.uniform(15.0, 30.0)  # Générer une valeur aléatoire entre 15 et 30
        ajouter_mesure(valeur, id_capteur_actionneur)

# Fonction pour insérer plusieurs factures
def remplir_factures(nombre_factures, id_logement):
    types_factures = ["Eau", "Electricite", "Dechets"]
    for _ in range(nombre_factures):
        type_facture = random.choice(types_factures)  # Choisir un type de facture aléatoire
        montant = random.uniform(10.0, 100.0)  # Générer un montant aléatoire
        consommation = random.uniform(5.0, 50.0)  # Générer une consommation aléatoire
        ajouter_facture(type_facture, montant, consommation, id_logement)

# Fonction pour afficher tous les logements
def afficher_logements():
    query = "SELECT * FROM Logement"
    logements = c.execute(query).fetchall()
    for logement in logements:
        print(f"Logement ID: {logement['id_logement']}, Adresse: {logement['numero_rue']} {logement['nom_rue']}, Ville: {logement['ville']}, Téléphone: {logement['telephone']}, IP: {logement['adresse_ip']}")

# Appel des fonctions pour remplir la base
print("Ajout de 5 mesures pour le capteur 1")
remplir_mesures(5, 1)

print("Ajout de 3 factures pour le logement 13")
remplir_factures(3, 13)

print("Affichage des logements disponibles")
afficher_logements()

# Sauvegarder les modifications et fermer la connexion
conn.commit()
conn.close()
