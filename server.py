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
            competitions = json.load(comps)['competitions']
            # Convertir numberOfPlaces en entier
            for comp in competitions:
                comp['numberOfPlaces'] = int(comp['numberOfPlaces'])
            return competitions
    except Exception:
        return []

def saveClubs(clubs):
    with open('clubs.json', 'w', encoding='utf-8') as f:
        json.dump({'clubs': clubs}, f, indent=4)

def saveCompetitions(competitions):
    with open('competitions.json', 'w', encoding='utf-8') as f:
        # Convertir numberOfPlaces en chaîne pour sauvegarder
        for comp in competitions:
            comp['numberOfPlaces'] = str(comp['numberOfPlaces'])
        json.dump({'competitions': competitions}, f, indent=4)

# Recharger les données globales après modification
def reloadData():
    global clubs, competitions
    clubs = loadClubs()
    competitions = markPastCompetitions(loadCompetitions())

def markPastCompetitions(competitions):
    current_time = datetime.now()
    for comp in competitions:
        comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        comp['is_past'] = comp_date < current_time
    return competitions

clubs = loadClubs()
competitions = markPastCompetitions(loadCompetitions())

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
    matching_club = next((c for c in clubs if c.get('name') == club), None)
    matching_comp = next((c for c in competitions if c.get('name') == competition), None)
    if not matching_club or not matching_comp:
        flash("Club ou compétition non trouvé.")
        return render_template('welcome.html', club=matching_club or {}, competitions=competitions)
    found_club = matching_club
    found_comp = matching_comp
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
    global clubs, competitions
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')
    places_required = int(request.form.get('places', 0))
    matching_comp = next((c for c in competitions if c.get('name') == competition_name), None)
    matching_club = next((c for c in clubs if c.get('name') == club_name), None)
    if not matching_comp or not matching_club:
        flash("Compétition ou club non trouvé.")
        return render_template('welcome.html', club=matching_club or {}, competitions=competitions)
    competition = matching_comp
    club = matching_club
    available_places = competition['numberOfPlaces']  # Déjà un entier
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
        booking_record = {
            'competition': competition_name,
            'places': places_required,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if 'bookings' not in club:
            club['bookings'] = []
        club['bookings'].append(booking_record)
        competition['numberOfPlaces'] -= places_required  # Soustraction directe avec entiers
        club['points'] = str(int(club['points']) - places_required)
        saveCompetitions(competitions)
        saveClubs(clubs)
        reloadData()
        updated_club = next((c for c in clubs if c.get('name') == club_name), None)
        flash(f"Réservation réussie pour {places_required} places ! Points restants: {updated_club['points']}")
        return render_template('welcome.html', club=updated_club, competitions=competitions)
    return render_template('booking.html', club=club, competition=competition)

@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)