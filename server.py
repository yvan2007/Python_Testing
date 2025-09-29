import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'something_special'

def loadClubs():
    try:
        with open('clubs.json', 'r', encoding='utf-8') as c:
            return json.load(c)['clubs']
    except Exception:
        return []

def loadCompetitions():
    try:
        with open('competitions.json', 'r', encoding='utf-8') as comps:
            return json.load(comps)['competitions']
    except Exception:
        return []

def saveClubs(clubs):
    with open('clubs.json', 'w', encoding='utf-8') as f:
        json.dump({'clubs': clubs}, f, indent=4)

def saveCompetitions(competitions):
    with open('competitions.json', 'w', encoding='utf-8') as f:
        json.dump({'competitions': competitions}, f, indent=4)

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
    matching_club = [c for c in clubs if c.get('name') == club]
    matching_comp = [c for c in competitions if c.get('name') == competition]
    if not matching_club or not matching_comp:
        flash("Club ou compétition non trouvé.")
        return render_template('welcome.html', club=matching_club[0] if matching_club else {}, competitions=competitions)
    found_club = matching_club[0]
    found_comp = matching_comp[0]
    try:
        comp_date = datetime.strptime(found_comp['date'], "%Y-%m-%d %H:%M:%S")
        if comp_date < datetime.now():
            flash("Cette compétition est passée et ne peut pas être réservée.")
            return render_template('welcome.html', club=found_club, competitions=competitions)
    except ValueError:
        flash("Format de date invalide.")
        return render_template('welcome.html', club=found_club, competitions=competitions)
    return render_template('booking.html', club=found_club, competition=found_comp)

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')
    places_required = int(request.form.get('places', 0))
    matching_comp = [c for c in competitions if c.get('name') == competition_name]
    matching_club = [c for c in clubs if c.get('name') == club_name]
    if not matching_comp or not matching_club:
        flash("Compétition ou club non trouvé.")
        return render_template('welcome.html', club=matching_club[0] if matching_club else {}, competitions=competitions)
    competition = matching_comp[0]
    club = matching_club[0]
    available_places = int(competition['numberOfPlaces'])
    club_points = int(club['points'])
    if places_required <= 0:
        flash("Le nombre de places doit être positif.")
    elif places_required > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places par compétition.")
    elif places_required > available_places:
        flash("Pas assez de places disponibles.")
    elif places_required > club_points:
        flash("Pas assez de points dans votre club (1 point par place).")
    else:
        competition['numberOfPlaces'] = str(available_places - places_required)
        club['points'] = str(club_points - places_required)
        saveCompetitions(competitions)
        saveClubs(clubs)
        flash(f"Réservation réussie pour {places_required} places ! Points restants: {club['points']}")
        return render_template('welcome.html', club=club, competitions=competitions)
    return render_template('booking.html', club=club, competition=competition)

@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)