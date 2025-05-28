from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Utile pour les messages flash

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------- Page d'accueil --------------------------
@app.route('/')
def accueil():
    return render_template('accueil.html', year=2025)

# -------------------------- Ajouter une panne --------------------------
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter_panne():
    if request.method == 'POST':
        image = request.files['image']
        date_heure = request.form['date_heure']
        description = request.form['description']

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            conn = sqlite3.connect('pannes.db')
            c = conn.cursor()
            c.execute('''INSERT INTO pannes (image, date_heure, description) VALUES (?, ?, ?)''',
                      (filename, date_heure, description))
            conn.commit()
            conn.close()
            return redirect(url_for('pannes'))

    return render_template('ajouter.html', year=2025)

# -------------------------- Voir les pannes --------------------------
@app.route('/pannes')
def pannes():
    conn = sqlite3.connect('pannes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pannes")
    pannes = c.fetchall()
    conn.close()
    return render_template('pannes.html', pannes=pannes, year=2025)

# -------------------------- Résoudre une panne --------------------------
@app.route('/resoudre/<int:id>', methods=['GET'])
def resoudre(id):
    return render_template('resoudre.html', id=id, year=2025)

@app.route('/regler/<int:id>', methods=['POST'])
def regler(id):
    date_heure_fin = request.form.get('date_heure_fin')

    conn = sqlite3.connect('pannes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pannes WHERE id = ?", (id,))
    panne = c.fetchone()

    if panne:
        try:
            date_heure_debut = datetime.strptime(panne[3], "%Y-%m-%dT%H:%M")
            date_heure_fin_dt = datetime.strptime(date_heure_fin, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Date invalide. Veuillez respecter le format YYYY-MM-DDTHH:MM", "danger")
            return redirect(url_for('pannes'))

        duree = date_heure_fin_dt - date_heure_debut

        c.execute('''INSERT INTO regles (image, date_heure_debut, date_heure_fin, description, duree) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (panne[1], panne[3], date_heure_fin, panne[2], str(duree)))
        c.execute("DELETE FROM pannes WHERE id = ?", (id,))
        conn.commit()
    conn.close()
    return redirect(url_for('regles'))

# -------------------------- Voir les engins réglés --------------------------
@app.route('/regles')
def regles():
    conn = sqlite3.connect('pannes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM regles")
    regles = c.fetchall()
    conn.close()
    return render_template('regles.html', regles=regles, year=2025)

# -------------------------- Supprimer un engin réglé --------------------------
@app.route('/supprimer/<int:id>', methods=['POST'])
def supprimer(id):
    conn = sqlite3.connect('pannes.db')
    c = conn.cursor()
    c.execute("DELETE FROM regles WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('regles'))

# -------------------------- Lancer l'application --------------------------
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)