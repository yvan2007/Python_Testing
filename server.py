from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = 'something_special'

def loadClubs():
    try:
        with open('clubs.json', 'r', encoding='utf-8') as c:
            return json.load(c)['clubs']
    except FileNotFoundError:
        return [] 
        return [] 

def loadCompetitions():
    try:
        with open('competitions.json', 'r', encoding='utf-8') as comp:
            return json.load(comp)['competitions']
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

clubs = loadClubs()
competitions = loadCompetitions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email') 
    if not email:
        flash("Veuillez entrer un email.")
        return render_template('index.html')
    matching_clubs = [club for club in clubs if club.get('email') == email]  
    if not matching_clubs:
        flash("Aucun club trouvé avec cet email.")
        return render_template('index.html')
    club = matching_clubs[0] 
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    matching_club = [c for c in clubs if c['name'] == club]
    matching_comp = [c for c in competitions if c['name'] == competition]
    if not matching_club or not matching_comp:
        flash("Club ou compétition non trouvée.")
        return render_template('welcome.html', club=matching_club[0] if matching_club else {}, competitions=competitions)
    found_club = matching_club[0]
    found_comp = matching_comp[0]
    comp_date = datetime.strptime(found_comp['date'], "%Y-%m-%d %H:%M:%S")
    if comp_date < datetime(2025, 9, 29):
        flash("Cette compétition est passée.")
        return render_template('welcome.html', club=found_club, competitions=competitions)
    return render_template('booking.html', club=found_club, competition=found_comp)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)