-- Suppression des tables dans l'ordre pour éviter les erreurs de dépendances
DROP TABLE IF EXISTS Mesure; 
DROP TABLE IF EXISTS Facture; 
DROP TABLE IF EXISTS Capteur_Actionneur; 
DROP TABLE IF EXISTS Type_Capteur_Actionneur; 
DROP TABLE IF EXISTS Piece; 
DROP TABLE IF EXISTS Logement;
DROP TABLE IF EXISTS Meteo;

-- Création des tables
CREATE TABLE Logement (
    id_logement INTEGER PRIMARY KEY,  
    numero_rue TEXT,                  -- Numéro de rue
    nom_rue TEXT,                     -- Nom de la rue
    ville TEXT,                       -- Ville
    code_postal TEXT,                 -- Code postal
    telephone TEXT,                   -- Numéro de téléphone
    adresse_ip TEXT,                  -- Adresse IP
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Date d'insertion
);

CREATE TABLE Piece (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,    
    nom_piece TEXT,                    
    x INTEGER,                         
    y INTEGER,                         
    z INTEGER,                         
    id_logement INTEGER,               
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)  
);

CREATE TABLE Type_Capteur_Actionneur (
    id_type INTEGER PRIMARY KEY,       
    nom_type TEXT,                     
    unite_mesure TEXT,                 
    precision_plage TEXT               
);

CREATE TABLE Capteur_Actionneur (
    id_capteur_actionneur INTEGER PRIMARY KEY,  
    ref_commerciale TEXT,                       
    port_communication INTEGER,                
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    id_piece INTEGER,                           
    id_type INTEGER,                            
    FOREIGN KEY (id_piece) REFERENCES Piece(id_piece),  
    FOREIGN KEY (id_type) REFERENCES Type_Capteur_Actionneur(id_type)  
);

CREATE TABLE Mesure (
    id_mesure INTEGER PRIMARY KEY,     
    valeur REAL,                       
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    id_capteur_actionneur INTEGER,     
    FOREIGN KEY (id_capteur_actionneur) REFERENCES Capteur_Actionneur(id_capteur_actionneur)  
);

CREATE TABLE Facture (
    id_facture INTEGER PRIMARY KEY,    
    type_facture TEXT,                 
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                    
    montant REAL,                      
    consommation REAL,                 
    id_logement INTEGER,               
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)  
);

-- Insertion des données
INSERT INTO Logement (id_logement, numero_rue, nom_rue, ville, code_postal, telephone, adresse_ip, date_insertion) 
VALUES (13, "10", "Rue Principale", "Monaco", "98000", "0764562899", "10.29.255.254", "2024-01-01 10:00:00");

INSERT INTO Piece (nom_piece, x, y, z, id_logement)
VALUES 
("Piece_Du_Roi", 3, 0, -2, 13),
("Piece_De_la_Renne", 5, 1, 8, 13),
("Piece_Du_Prince", 8, 3, 9, 13),
("Piece_De_la_Princesse", 2, 1, 7, 13);

INSERT INTO Type_Capteur_Actionneur (id_type, nom_type, unite_mesure, precision_plage) 
VALUES 
(12, "ATX", "degré", "+-5%"),
(13, "Lamp", "lux", "+-3%"),
(14, "Gaz", "ppm", "+-10%"),
(15, "STM32", "kWh", "+-3%"),
(16, "Volet", "angle", "+-2%");

INSERT INTO Capteur_Actionneur (id_capteur_actionneur, ref_commerciale, port_communication, date_insertion, id_piece, id_type) 
VALUES 
(1, "01", 1800, "2024-01-01 10:10:00", 1, 12),
(2, "02", 1800, "2024-01-01 10:15:00", 2, 13),
(3, "03", 1800, "2024-01-01 10:20:00", 3, 14),
(4, "04", 1800, "2024-01-01 10:25:00", 4, 15);

INSERT INTO Mesure (id_mesure, valeur, date_insertion, id_capteur_actionneur) 
VALUES 
(1, 17.09, "2024-01-01 10:20:00", 1),
(2, 18.50, "2024-01-01 10:25:00", 2),
(3, 19.75, "2024-01-01 10:30:00", 1),
(4, 16.80, "2024-01-01 10:35:00", 2),
(5, 21.00, "2024-01-01 10:40:00", 3),
(6, 22.50, "2024-01-01 10:45:00", 4);


INSERT INTO Facture (id_facture, type_facture, date, montant, consommation, id_logement) 
VALUES 
(1, "Electricite", "2024-01-02 12:00:00", 75, 18, 13),
(2, "Eau", "2024-02-01 12:00:00", 50, 12, 13),
(3, "Dechets", "2024-03-01 12:00:00", 20, 5, 13),
(4, "Electricite", "2024-04-01 12:00:00", 10, 8, 13);
