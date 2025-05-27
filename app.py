from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

# Initialisation de Flask
app = Flask(__name__)

# Dossier pour les images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Créer automatiquement la base SQLite et la table si elles n'existent pas
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

# ✅ Route d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# ✅ Route pour ajouter une panne
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

        return redirect(url_for('ajouter'))  # reste sur la même page

    return render_template('ajouter.html')

# ✅ Route pour afficher les pannes
@app.route('/pannes')
def pannes():
    with sqlite3.connect('pannes.db') as conn:
        conn.row_factory = sqlite3.Row
        pannes = conn.execute("SELECT * FROM pannes ORDER BY id DESC").fetchall()
    return render_template('pannes.html', pannes=pannes)

# ✅ Route pour supprimer une panne
@app.route('/supprimer/<int:id>', methods=['POST'])
def supprimer(id):
    with sqlite3.connect('pannes.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT image FROM pannes WHERE id = ?", (id,))
        row = cur.fetchone()
        if row and row['image']:
            image_path = row['image'].lstrip('/')
            if os.path.exists(image_path):
                os.remove(image_path)
        cur.execute("DELETE FROM pannes WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for('pannes'))

# ✅ Lancer le serveur localement
if __name__ == '__main__':
    init_db()
    app.run(debug=True)