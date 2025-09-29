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


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)