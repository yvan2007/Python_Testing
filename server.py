import json
from flask import Flask, render_template, request, redirect, flash, url_for, session
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

def markPastCompetitions(competitions):
    """Mark past competitions and return updated list"""
    current_time = datetime.now()
    for comp in competitions:
        try:
            comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
            comp['is_past'] = comp_date < current_time
        except ValueError:
            comp['is_past'] = False
    return competitions

clubs = loadClubs()
competitions = markPastCompetitions(loadCompetitions())

@app.route('/')
def index():
    clubs = loadClubs()
    return render_template('index.html', clubs=clubs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        club = next((c for c in clubs if c['email'] == email), None)
        if club:
            session['club'] = club
            return redirect(url_for('showSummary'))
        else:
            flash('Email not found')
    return render_template('login.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    clubs = loadClubs()
    competitions = markPastCompetitions(loadCompetitions())
    
    email = request.form.get('email')
    if not email:
        flash("Veuillez entrer un email.")
        return render_template('index.html', clubs=clubs)
    
    matching_clubs = [club for club in clubs if club.get('email') == email]
    if not matching_clubs:
        flash("Aucun club trouvé avec cet email.")
        return render_template('index.html', clubs=clubs)
    
    club = matching_clubs[0]
    # Sauvegarder l'email du club dans la session
    session['club_email'] = email
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/summary')
def summary():
    """Affiche le résumé du club connecté"""
    clubs = loadClubs()
    competitions = markPastCompetitions(loadCompetitions())
    
    # Récupérer le club depuis la session ou utiliser un club par défaut
    club_email = session.get('club_email')
    if club_email:
        matching_clubs = [club for club in clubs if club.get('email') == club_email]
        if matching_clubs:
            club = matching_clubs[0]
            return render_template('welcome.html', club=club, competitions=competitions)
    
    # Si pas de club en session, rediriger vers la page d'accueil
    return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    clubs = loadClubs()
    competitions = markPastCompetitions(loadCompetitions())
    
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
    clubs = loadClubs()
    competitions = markPastCompetitions(loadCompetitions())
    
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
        
        # Ajouter la réservation à l'historique du club
        if 'bookings' not in club:
            club['bookings'] = []
        
        from datetime import datetime
        booking = {
            'competition': competition_name,
            'places': places_required,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        club['bookings'].append(booking)
        
        saveCompetitions(competitions)
        saveClubs(clubs)
        flash(f"Réservation réussie pour {places_required} places ! Points restants: {club['points']}")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    return render_template('booking.html', club=club, competition=competition)

@app.route('/points')
def points():
    clubs = loadClubs()
    return render_template('points.html', clubs=clubs)

@app.route('/logout')
def logout():
    session.pop('club', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)