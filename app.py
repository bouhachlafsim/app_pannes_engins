from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Dossier des images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Création automatique de la base si elle n'existe pas
def init_db():
    if not os.path.exists('pannes.db'):
        with sqlite3.connect('pannes.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pannes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    heure TEXT NOT NULL,
                    description TEXT NOT NULL,
                    image TEXT
                )
            ''')

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# Ajouter une panne
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        date = request.form['date']
        heure = request.form['heure']
        description = request.form['description']
        image_file = request.files['image']

        image_path = ""
        if image_file and image_file.filename != '':
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"/static/uploads/{filename}"

        with sqlite3.connect('pannes.db') as conn:
            conn.execute(
                "INSERT INTO pannes (date, heure, description, image) VALUES (?, ?, ?, ?)",
                (date, heure, description, image_path)
            )

        return redirect(url_for('ajouter'))

    return render_template('ajouter.html')

# Afficher les engins en panne
@app.route('/pannes')
def pannes():
    with sqlite3.connect('pannes.db') as conn:
        conn.row_factory = sqlite3.Row
        pannes = conn.execute("SELECT * FROM pannes ORDER BY id DESC").fetchall()
    return render_template('pannes.html', pannes=pannes)

# Supprimer une panne (image incluse)
@app.route('/supprimer/<int:id>', methods=['POST'])
def supprimer(id):
    with sqlite3.connect('pannes.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT image FROM pannes WHERE id = ?", (id,))
        row = cur.fetchone()
        if row and row[0]:
            image_path = os.path.join(os.getcwd(), row[0].lstrip('/'))
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Erreur suppression image : {e}")
        cur.execute("DELETE FROM pannes WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for('pannes'))

# Lancer l'application
if __name__ == '__main__':
    init_db()
    app.run(debug=True)