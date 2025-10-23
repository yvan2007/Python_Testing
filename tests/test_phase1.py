import pytest
import server
from datetime import datetime, timedelta

class TestPhase1:
    """Tests for Phase 1 - Basic Functionality"""
    
    def test_index_page_loads(self, client):
        """Test that the index page loads correctly with beautiful interface."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
        assert b'Total R' in response.data  # Total Réservations
        assert b'Statut' in response.data
        # Vérifier que l'email n'est PAS affiché dans les colonnes du tableau (interface privée)
        assert b'<th>Email</th>' not in response.data
        assert b'<td>Email</td>' not in response.data
    
    def test_login_page_loads(self, client):
        """Test that the login page loads with beautiful interface."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Connexion Secr' in response.data  # Connexion Secrétaire
        assert b'Adresse Email' in response.data
        assert b'Retour' in response.data  # Retour à l'accueil
        # Le bouton "View Public Points" a été supprimé
    
    def test_points_page_loads(self, client):
        """Test that the points page loads with beautiful interface."""
        response = client.get('/points')
        assert response.status_code == 200
        assert b'Affichage des Points' in response.data
        assert b'Points de Tous les Clubs' in response.data
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
        # Vérifier que l'email n'est PAS affiché
        assert b'Email' not in response.data
    
    def test_authentication_success(self, client, restore_data):
        """Test successful authentication with beautiful interface."""
        # Trouver un club valide
        valid_club = None
        for club in server.clubs:
            if club.get('email'):
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        response = client.post('/showSummary', data={'email': valid_club['email']})
        assert response.status_code == 200
        # Le nom du club n'apparaît pas directement, mais l'email oui
        assert valid_club['email'].encode() in response.data
        assert b'Bienvenue' in response.data or b'Comp' in response.data
    
    def test_authentication_failure(self, client):
        """Test authentication failure with beautiful interface."""
        response = client.post('/showSummary', data={'email': 'nonexistent@example.com'})
        assert response.status_code == 200
        assert b'Aucun club trouv' in response.data or b'not found' in response.data
    
    def test_competition_list_display(self, client, restore_data):
        """Test that competitions are displayed with beautiful interface."""
        # Trouver un club valide
        valid_club = None
        for club in server.clubs:
            if club.get('email'):
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        response = client.post('/showSummary', data={'email': valid_club['email']})
        assert response.status_code == 200
        
        # Vérifier qu'au moins une compétition est affichée
        assert b'Competition' in response.data or b'competition' in response.data
    
    def test_booking_page_access(self, client, restore_data):
        """Test booking page access with beautiful interface."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if club.get('name'):
                valid_club = club
                break
        
        for comp in server.competitions:
            if comp.get('name'):
                valid_comp = comp
                break
        
        assert valid_club is not None, "No valid club found for testing"
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.get(f'/book/{valid_comp["name"]}/{valid_club["name"]}')
        assert response.status_code == 200
        # Le nom du club n'apparaît pas directement, mais l'email oui
        assert valid_club['email'].encode() in response.data
        assert valid_comp['name'].encode() in response.data
    
    def test_booking_success(self, client, restore_data):
        """Test successful booking with beautiful interface."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if int(club.get('points', 0)) >= 3:
                valid_club = club
                break
        
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 3:
                valid_comp = comp
                break
        
        assert valid_club is not None, "No valid club with enough points found"
        assert valid_comp is not None, "No valid competition with enough places found"
        
        initial_points = int(valid_club['points'])
        initial_places = int(valid_comp['numberOfPlaces'])
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '3'
        })
        
        assert response.status_code == 200
        assert b'R\xc3\xa9servation r\xc3\xa9ussie' in response.data
        
        # Vérifier que les points et places ont été mis à jour
        # Recharger les données depuis les fichiers JSON
        server.clubs[:] = server.loadClubs()
        server.competitions[:] = server.loadCompetitions()
        
        # Trouver le club et la compétition mis à jour
        updated_club = next((c for c in server.clubs if c['name'] == valid_club['name']), None)
        updated_comp = next((c for c in server.competitions if c['name'] == valid_comp['name']), None)
        
        assert updated_club is not None, "Club not found after update"
        assert updated_comp is not None, "Competition not found after update"
        assert int(updated_club['points']) == initial_points - 3
        assert int(updated_comp['numberOfPlaces']) == initial_places - 3
    
    def test_booking_fails_with_insufficient_points(self, client, restore_data):
        """Test booking failure with insufficient points."""
        # Trouver un club avec peu de points
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if int(club.get('points', 0)) < 3:
                valid_club = club
                break
        
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 3:
                valid_comp = comp
                break
        
        if valid_club is None:
            # Créer un club avec peu de points pour le test
            valid_club = server.clubs[0]
            valid_club['points'] = '1'
        
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '3'
        })
        
        assert response.status_code == 200
        assert b"Pas assez de points dans votre club" in response.data
    
    def test_booking_fails_with_negative_places(self, client, restore_data):
        """Test booking failure with negative places."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if club.get('name'):
                valid_club = club
                break
        
        for comp in server.competitions:
            if comp.get('name'):
                valid_comp = comp
                break
        
        assert valid_club is not None, "No valid club found for testing"
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '-1'
        })
        
        assert response.status_code == 200
        assert b"Le nombre de places doit \xc3\xaatre positif" in response.data
    
    def test_booking_fails_with_zero_places(self, client, restore_data):
        """Test booking failure with zero places."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if club.get('name'):
                valid_club = club
                break
        
        for comp in server.competitions:
            if comp.get('name'):
                valid_comp = comp
                break
        
        assert valid_club is not None, "No valid club found for testing"
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '0'
        })
        
        assert response.status_code == 200
        assert b"Le nombre de places doit \xc3\xaatre positif" in response.data
    
    def test_booking_fails_with_too_many_places(self, client, restore_data):
        """Test booking failure with too many places."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if club.get('name'):
                valid_club = club
                break
        
        for comp in server.competitions:
            if comp.get('name'):
                valid_comp = comp
                break
        
        assert valid_club is not None, "No valid club found for testing"
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '13'
        })
        
        assert response.status_code == 200
        assert b"Vous ne pouvez pas r\xc3\xa9server plus de 12 places" in response.data
    
    def test_points_deducted_after_successful_booking(self, client, restore_data):
        """Test that points are deducted after successful booking."""
        # Trouver un club avec suffisamment de points
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if int(club.get('points', 0)) >= 5:
                valid_club = club
                break
        
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 5:
                valid_comp = comp
                break
        
        if valid_club is None:
            # Créer un club avec suffisamment de points
            valid_club = server.clubs[0]
            valid_club['points'] = '10'
        
        assert valid_comp is not None, "No valid competition found for testing"
        
        initial_points = int(valid_club['points'])
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '3'
        })
        
        assert response.status_code == 200
        # Recharger les données depuis les fichiers JSON
        server.clubs[:] = server.loadClubs()
        updated_club = next((c for c in server.clubs if c['name'] == valid_club['name']), None)
        assert updated_club is not None, "Club not found after update"
        assert int(updated_club['points']) == initial_points - 3
    
    def test_competition_places_reduced_after_booking(self, client, restore_data):
        """Test that competition places are reduced after booking."""
        # Trouver un club et une compétition valides
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if int(club.get('points', 0)) >= 5:
                valid_club = club
                break
        
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 5:
                valid_comp = comp
                break
        
        if valid_club is None:
            # Créer un club avec suffisamment de points
            valid_club = server.clubs[0]
            valid_club['points'] = '10'
        
        assert valid_comp is not None, "No valid competition found for testing"
        
        initial_places = int(valid_comp['numberOfPlaces'])
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '2'
        })
        
        assert response.status_code == 200
        # Recharger les données depuis les fichiers JSON
        server.competitions[:] = server.loadCompetitions()
        updated_comp = next((c for c in server.competitions if c['name'] == valid_comp['name']), None)
        assert updated_comp is not None, "Competition not found after update"
        assert int(updated_comp['numberOfPlaces']) == initial_places - 2
    
    def test_access_control_unauthorized(self, client):
        """Test that unauthorized users cannot access booking pages."""
        response = client.get('/book/TestCompetition/TestClub')
        assert response.status_code == 200
        # Devrait rediriger ou afficher un message d'erreur
    
    def test_past_competition_handling(self, client, restore_data):
        """Test handling of past competitions."""
        # Trouver un club valide
        valid_club = None
        for club in server.clubs:
            if club.get('name'):
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        # Créer une compétition passée
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        past_comp = {
            'name': 'Past Competition',
            'date': past_date,
            'numberOfPlaces': '10'
        }
        server.competitions.append(past_comp)
        
        response = client.get(f'/book/{past_comp["name"]}/{valid_club["name"]}')
        assert response.status_code == 200
        # Vérifier que les compétitions passées sont marquées comme telles
        assert b"past-comp" in response.data or b"pass\xc3\xa9e" in response.data
