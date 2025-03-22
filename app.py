from flask import Flask, jsonify
import sqlite3
import pandas as pd
import threading

app = Flask(__name__)

db_name = "annonces.db"
csv_file = "Mubawab_Annonces.xlsx"

# Initialisation de la base de données
def init_db():
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS annonces (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            titre TEXT,
                            prix TEXT,
                            localisation TEXT,
                            superficie TEXT,
                            pieces TEXT,
                            chambres TEXT,
                            salles_de_bain TEXT,
                            lien TEXT)
                        ''')
        conn.commit()

# Route d'accueil
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bienvenue sur l'API des annonces immobilières !"}), 200

# Récupérer les annonces depuis la base de données
@app.route("/annonces", methods=["GET"])
def get_annonces():
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM annonces")
        annonces = [
            {
                "id": row[0],
                "titre": row[1],
                "prix": row[2],
                "localisation": row[3],
                "superficie": row[4],
                "pieces": row[5],
                "chambres": row[6],
                "salles_de_bain": row[7],
                "lien": row[8],
            }
            for row in cursor.fetchall()
        ]
    return jsonify({"annonces": annonces})

# Récupérer les annonces depuis le fichier CSV
@app.route("/annonces_csv", methods=["GET"])
def get_annonces_csv():
    try:
        df = pd.read_excel(csv_file)
        annonces = df.to_dict(orient="records")
        return jsonify({"annonces": annonces})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer le scraping en arrière-plan
@app.route("/scrape", methods=["POST"])
def launch_scraping():
    try:
        from scrapping import scrape_annonces  # Importation du script de scraping
        thread = threading.Thread(target=scrape_annonces)
        thread.start()
        return jsonify({"message": "Scraping lancé en arrière-plan !"})
    except ImportError:
        return jsonify({"error": "Le fichier scrapping.py est introuvable !"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
