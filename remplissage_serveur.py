from flask import Flask, request, jsonify, render_template_string , render_template
import requests
import sqlite3
import random




app = Flask(__name__)

DATABASE = 'logement.db'

# Fonction pour établir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def accueil():
    return render_template('accueil.html')

# 2.1 Remplissage de la base de données
# Endpoint pour ajouter une mesure (POST)
@app.route('/ajouter_mesure', methods=['POST'])
def ajouter_mesure():
    data = request.json
    valeur = data['valeur']
    id_capteur_actionneur = data['id_capteur_actionneur']

    conn = get_db_connection()
    c = conn.cursor()
    query = """
    INSERT INTO Mesure (valeur, date_insertion, id_capteur_actionneur)
    VALUES (?, datetime('now'), ?)
    """
    c.execute(query, (valeur, id_capteur_actionneur))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Mesure ajoutée : valeur={valeur}, id_capteur_actionneur={id_capteur_actionneur}"}), 201

# Endpoint pour ajouter une facture (POST)
@app.route('/ajouter_facture', methods=['POST'])
def ajouter_facture():
    data = request.json
    type_facture = data['type_facture']
    montant = data['montant']
    consommation = data['consommation']
    id_logement = data['id_logement']

    conn = get_db_connection()
    c = conn.cursor()
    query = """
    INSERT INTO Facture (type_facture, date, montant, consommation, id_logement)
    VALUES (?, datetime('now'), ?, ?, ?)
    """
    c.execute(query, (type_facture, montant, consommation, id_logement))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Facture ajoutée : type={type_facture}, montant={montant}, consommation={consommation}, logement={id_logement}"}), 201

# Endpoint pour afficher les logements (GET)
@app.route('/logements', methods=['GET'])
def afficher_logements():
    conn = get_db_connection()
    query = "SELECT * FROM Logement"
    logements = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(logement) for logement in logements])

# Endpoint pour remplir plusieurs mesures dynamiquement (POST)
@app.route('/remplir_mesures', methods=['POST'])
def remplir_mesures():
    data = request.json
    nombre_mesures = data['nombre_mesures']
    id_capteur_actionneur = data['id_capteur_actionneur']
    conn = get_db_connection()
    c = conn.cursor()
    for _ in range(nombre_mesures):
        valeur = random.uniform(15.0, 30.0)
        query = """
        INSERT INTO Mesure (valeur, date_insertion, id_capteur_actionneur)
        VALUES (?, datetime('now'), ?)
        """
        c.execute(query, (valeur, id_capteur_actionneur))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{nombre_mesures} mesures ajoutées pour le capteur {id_capteur_actionneur}"}), 201

# Endpoint pour remplir plusieurs factures dynamiquement (POST)
@app.route('/remplir_factures', methods=['POST'])
def remplir_factures():
    data = request.json
    nombre_factures = data['nombre_factures']
    id_logement = data['id_logement']
    types_factures = ["Eau", "Electricite", "Dechets"]
    conn = get_db_connection()
    c = conn.cursor()
    for _ in range(nombre_factures):
        type_facture = random.choice(types_factures)
        montant = random.uniform(10.0, 100.0)
        consommation = random.uniform(5.0, 50.0)
        query = """
        INSERT INTO Facture (type_facture, date, montant, consommation, id_logement)
        VALUES (?, datetime('now'), ?, ?, ?)
        """
        c.execute(query, (type_facture, montant, consommation, id_logement))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{nombre_factures} factures ajoutées pour le logement {id_logement}"}), 201

# 2.2 Serveur web avec graphique
@app.route('/factures_graphique')
def factures_graphique():
    conn = get_db_connection()
    c = conn.cursor()
    query = """
    SELECT type_facture, SUM(montant) as total_montant
    FROM Facture
    GROUP BY type_facture
    """
    factures = c.execute(query).fetchall()
    conn.close()

    # Transformer les données pour Google Charts
    data = [["Type de Facture", "Montant Total"]]
    for facture in factures:
        data.append([facture['type_facture'], facture['total_montant']])

    # Convertir les données en format compatible avec Google Charts
    chart_data = str(data).replace("'", '"')

    # Renvoyer le modèle HTML avec les données
    return render_template('factures_graphique.html', chart_data=chart_data)



@app.route('/meteo', methods=['GET'])
def afficher_meteo():
    ville = request.args.get('ville')
    if not ville:
        return render_template('meteo.html', error="Veuillez renseigner une ville pour voir les prévisions météo.")
    
    icon_map = {
        "clear sky": "sunny.png",
        "few clouds": "partly_cloudy.png",
        "scattered clouds": "cloudy.png",
        "rain": "rain.png",
        "snow": "snow.png",
        "thunderstorm": "thunderstorm.png",
        "mist": "mist.png",
        "default": "default.png"
    }
    OPENWEATHER_API_KEY = "acc7d79f0b57f1b8ce4a31a652181c33"
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        'q': ville,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'cnt': 40
    }
    response = requests.get(OPENWEATHER_URL, params=params)

    if response.status_code != 200:
        return render_template('meteo.html', error="Impossible de récupérer les données météo pour cette ville.")

    data = response.json()

    # Initialisation des données groupées par jour
    daily_data = {}
    for item in data['list']:
        date = item['dt_txt'].split(' ')[0]
        time = item['dt_txt'].split(' ')[1]
        temp = item['main']['temp']
        description = item['weather'][0]['description']
        precipitation = item.get('rain', {}).get('3h', 0)
        icon = icon_map.get(description, icon_map["default"])

        # Si la date n'est pas encore présente, initialisez-la
        if date not in daily_data:
            daily_data[date] = {
                'times': [],
                'temps': [],
                'precipitation': [],
                'icons': [],
                'description': description,  # La première description sera utilisée
                'min_temp': temp,  # Initialisez min et max avec la première température
                'max_temp': temp
            }

        # Mise à jour des données pour chaque jour
        daily_data[date]['times'].append(time)
        daily_data[date]['temps'].append(temp)
        daily_data[date]['precipitation'].append(precipitation)
        daily_data[date]['icons'].append(icon)
        daily_data[date]['min_temp'] = min(daily_data[date]['min_temp'], temp)
        daily_data[date]['max_temp'] = max(daily_data[date]['max_temp'], temp)

    # Transformation des données pour le template
    chart_data = [
        {
            'date': date,
            'times': values['times'],
            'temps': values['temps'],
            'precipitation': values['precipitation'],
            'icons': values['icons'],
            'description': values['description'],  # Description du jour
            'min_temp': values['min_temp'],        # Température minimale
            'max_temp': values['max_temp']         # Température maximale
        }
        for date, values in daily_data.items()
    ]

    return render_template('meteo.html', ville=ville.capitalize(), chart_data=chart_data)

# Point d'entrée pour recevoir les données du capteur


@app.route('/api/donnees-capteur1', methods=['POST'])
def recevoir_donnees_capteur():
    try:
        # Récupérer les données JSON de la requête
        data = request.get_json()
        temperature = data.get('temperature')
        humidite = data.get('humidité')
        ref_commerciale = data.get('ref_commerciale')
        port_communication = data.get('port_communication')
        type_nom = data.get('type_nom')
        unite_mesure = data.get('unite_mesure')
        precision_plage = data.get('precision_plage')

        # Connecter à la base de données
        conn = sqlite3.connect('logement.db')
        cursor = conn.cursor()

        # Vérifier et insérer dans Type_Capteur_Actionneur
        cursor.execute("""
            SELECT id_type FROM Type_Capteur_Actionneur WHERE nom_type = ?
        """, (type_nom,))
        type_result = cursor.fetchone()

        if type_result is None:
            cursor.execute("""
                INSERT INTO Type_Capteur_Actionneur (nom_type, unite_mesure, precision_plage)
                VALUES (?, ?, ?)
            """, (type_nom, unite_mesure, precision_plage))
            type_id = cursor.lastrowid
        else:
            type_id = type_result[0]

        # Vérifier et insérer dans Capteur_Actionneur
        cursor.execute("""
            SELECT id_capteur_actionneur FROM Capteur_Actionneur WHERE ref_commerciale = ?
        """, (ref_commerciale,))
        capteur_result = cursor.fetchone()

        if capteur_result is None:
            cursor.execute("""
                INSERT INTO Capteur_Actionneur (ref_commerciale, port_communication, id_type, date_insertion)
                VALUES (?, ?, ?, datetime('now'))
            """, (ref_commerciale, port_communication, type_id))
            capteur_id = cursor.lastrowid
        else:
            capteur_id = capteur_result[0]

        # Insérer les mesures dans la table Mesure
        if temperature is not None:
            cursor.execute("""
                INSERT INTO Mesure (valeur, date_insertion, id_capteur_actionneur)
                VALUES (?, datetime('now'), ?)
            """, (temperature, capteur_id))

        if humidite is not None:
            cursor.execute("""
                INSERT INTO Mesure (valeur, date_insertion, id_capteur_actionneur)
                VALUES (?, datetime('now'), ?)
            """, (humidite, capteur_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Données insérées avec succès'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/consommation')
def consommation():
    return render_template('consommation.html')

@app.route('/consommation/<type>/<echelle>')
def consommation_detail(type, echelle):
    conn = get_db_connection()
    c = conn.cursor()

    # Choisir la colonne (montant ou consommation)
    colonne = "consommation" if type != "montant" else "montant"

    # Échelles de temps
    if echelle == "jour":
        query = f"""
        SELECT date(date) as periode, SUM({colonne}) as total
        FROM Facture
        WHERE type_facture = ?
        GROUP BY periode
        """
    elif echelle == "semaine":
        query = f"""
        SELECT strftime('%Y-%W', date) as periode, SUM({colonne}) as total
        FROM Facture
        WHERE type_facture = ?
        GROUP BY periode
        """
    elif echelle == "mois":
        query = f"""
        SELECT strftime('%Y-%m', date) as periode, SUM({colonne}) as total
        FROM Facture
        WHERE type_facture = ?
        GROUP BY periode
        """
    elif echelle == "annee":
        query = f"""
        SELECT strftime('%Y', date) as periode, SUM({colonne}) as total
        FROM Facture
        WHERE type_facture = ?
        GROUP BY periode
        """
    else:
        return jsonify({"error": "Échelle non reconnue"}), 400

    # Exécuter la requête
    data = c.execute(query, (type.capitalize(),)).fetchall()
    conn.close()

    # Transformer les données pour Google Charts
    chart_data = [["Période", "Total"]] + [[row["periode"], row["total"]] for row in data]
    

    return render_template(
        'consommation_detail.html',
        type=type.capitalize(),
        echelle=echelle.capitalize(),
        chart_data=str(chart_data).replace("'", '"')
    )

@app.route('/etat_capteurs')
def etat_capteurs():
    conn = get_db_connection()
    c = conn.cursor()

    # Requête pour récupérer les capteurs/actionneurs et vérifier leur dernière mesure
    query = """
    SELECT 
        c.id_capteur_actionneur, 
        c.ref_commerciale, 
        c.port_communication, 
        t.nom_type, 
        t.unite_mesure, 
        p.nom_piece, 
        c.date_insertion,
        MAX(m.date_insertion) AS derniere_mesure,
        CASE 
            WHEN MAX(m.date_insertion) >= datetime('now', '-30 minutes') THEN 'En Ligne'
            ELSE 'Hors Ligne'
        END AS etat
    FROM 
        Capteur_Actionneur c
    LEFT JOIN 
        Mesure m ON c.id_capteur_actionneur = m.id_capteur_actionneur
    INNER JOIN 
        Type_Capteur_Actionneur t ON c.id_type = t.id_type
    INNER JOIN 
        Piece p ON c.id_piece = p.id_piece
    GROUP BY 
        c.id_capteur_actionneur, 
        c.ref_commerciale, 
        c.port_communication, 
        t.nom_type, 
        t.unite_mesure, 
        p.nom_piece, 
        c.date_insertion
    
    """

    # Exécution de la requête
    capteurs = c.execute(query).fetchall()

    # Fermer la connexion
    conn.close()

    # Renvoyer les données au template HTML
    return render_template('etat_capteurs.html', capteurs=capteurs)


@app.route('/economies1')
def index():
    return render_template('economies.html')

@app.route('/economies', methods=['GET'])
def economies():
    # Si aucun paramètre 'scale' n'est fourni, rendre le fichier HTML
    if not request.args.get('scale'):
        return render_template('economies.html')

    # Sinon, récupérer les données JSON pour l'échelle demandée
    scale = request.args.get('scale', 'month')  # Valeur par défaut : 'month'

    conn = get_db_connection()
    c = conn.cursor()

    # Requête SQL dynamique selon l'échelle
    if scale == 'year':
        query = """
        SELECT 
            strftime('%Y', date) AS periode,
            SUM(consommation) AS consommation_totale,
            SUM(montant) AS montant_total
        FROM Facture
        GROUP BY periode
        ORDER BY periode;
        """
    else:  # Default to 'month'
        query = """
        SELECT 
            strftime('%Y-%m', date) AS periode,
            SUM(consommation) AS consommation_totale,
            SUM(montant) AS montant_total
        FROM Facture
        GROUP BY periode
        ORDER BY periode;
        """
    
    result = c.execute(query).fetchall()
    conn.close()

    # Transformation des données en JSON
    economies_data = [
        {"periode": row["periode"], "consommation": row["consommation_totale"], "montant": row["montant_total"]}
        for row in result
    ]
    return jsonify(economies_data)

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'GET':
        # Si aucun paramètre 'type', renvoyer la page HTML
        if not request.args.get('type'):
            return render_template('configuration.html')

        # Identifier le type de données demandées pour les requêtes dynamiques
        data_type = request.args.get('type')

        if data_type == 'types':  # Récupérer les types de capteurs/actionneurs
            types = c.execute("SELECT id_type AS id, nom_type AS nom, unite_mesure AS unite FROM Type_Capteur_Actionneur").fetchall()
            conn.close()
            return jsonify([dict(row) for row in types])

        elif data_type == 'pieces':  # Récupérer les pièces
            pieces = c.execute("SELECT id_piece AS id, nom_piece AS nom FROM Piece").fetchall()
            conn.close()
            return jsonify([dict(row) for row in pieces])

        else:  # Pas de type spécifié
            conn.close()
            return jsonify({"error": "Type de données non spécifié"}), 400

    elif request.method == 'POST':
        # Récupérer les données JSON envoyées
        data = request.get_json()

        # Identifier le type de configuration
        config_type = data.get('config_type')

        if config_type == 'logement':  # Configuration du logement
            numero_rue = data.get('numeroRue')
            nom_rue = data.get('nomRue')
            ville = data.get('ville')
            code_postal = data.get('codePostal')
            telephone = data.get('telephone')
            adresse_ip = data.get('adresseIP')

            c.execute("""
                INSERT INTO Logement (numero_rue, nom_rue, ville, code_postal, telephone, adresse_ip) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (numero_rue, nom_rue, ville, code_postal, telephone, adresse_ip))
            conn.commit()
            conn.close()
            return jsonify({"message": "Paramètres du logement enregistrés avec succès"}), 200

        elif config_type == 'capteur':  # Ajouter un capteur/actionneur
            type_capteur = data.get('typeCapteur')
            ref_commerciale = data.get('refCommerciale')
            port_communication = data.get('portCommunication')
            id_piece = data.get('piece')

            c.execute("""
                INSERT INTO Capteur_Actionneur (ref_commerciale, port_communication, id_piece, id_type) 
                VALUES (?, ?, ?, ?)
            """, (ref_commerciale, port_communication, id_piece, type_capteur))
            conn.commit()
            conn.close()
            return jsonify({"message": "Capteur/Actionneur ajouté avec succès"}), 200

        else:  # Type de configuration non pris en charge
            conn.close()
            return jsonify({"error": "Type de configuration non pris en charge"}), 400

    else:  # Méthode HTTP non prise en charge
        conn.close()
        return jsonify({"error": "Méthode HTTP non prise en charge"}), 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
