import pytest
import server

class TestPhase1:
    """Tests for Phase 1 - Basic Functionality"""
    
    def test_index_page_loads(self, client):
        """Test that the index page loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
    
    def test_login_page_loads(self, client):
        """Test that the login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Connexion' in response.data
        assert b'Adresse Email' in response.data
    
    def test_points_page_loads(self, client):
        """Test that the points page loads."""
        response = client.get('/points')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
    
    def test_authentication_success(self, client, restore_data):
        """Test successful authentication."""
        valid_club = None
        for club in server.clubs:
            if club.get('email'):
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        response = client.post('/showSummary', data={'email': valid_club['email']})
        assert response.status_code == 200
        assert valid_club['email'].encode() in response.data
    
    def test_authentication_failure(self, client):
        """Test authentication failure."""
        response = client.post('/showSummary', data={'email': 'nonexistent@example.com'})
        assert response.status_code == 200
        assert b'Aucun club trouv' in response.data
    
    def test_competition_list_display(self, client, restore_data):
        """Test that competitions are displayed."""
        valid_club = None
        for club in server.clubs:
            if club.get('email'):
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        response = client.post('/showSummary', data={'email': valid_club['email']})
        assert response.status_code == 200
        assert b'Competition' in response.data or b'competition' in response.data
    
    def test_booking_page_access(self, client, restore_data):
        """Test booking page access."""
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
        assert valid_club['email'].encode() in response.data
        assert valid_comp['name'].encode() in response.data
    
    def test_booking_success(self, client, restore_data):
        """Test successful booking."""
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
        server.clubs[:] = server.loadClubs()
        server.competitions[:] = server.loadCompetitions()
        
        updated_club = next((c for c in server.clubs if c['name'] == valid_club['name']), None)
        updated_comp = next((c for c in server.competitions if c['name'] == valid_comp['name']), None)
        
        assert updated_club is not None, "Club not found after update"
        assert updated_comp is not None, "Competition not found after update"
        assert int(updated_club['points']) == initial_points - 3
        assert int(updated_comp['numberOfPlaces']) == initial_places - 3
    
    def test_booking_fails_with_insufficient_points(self, client, restore_data):
        """Test booking failure with insufficient points."""
        valid_club = None
        valid_comp = None
        
        for club in server.clubs:
            if club.get('name') == 'Power House':
                valid_club = club
                break
        
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 5:
                valid_comp = comp
                break
        
        assert valid_club is not None, "Power House club not found"
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '5'
        })
        
        assert response.status_code == 200
        assert b"Pas assez de points dans votre club (1 point par place)." in response.data
    
    def test_booking_fails_with_negative_places(self, client, restore_data):
        """Test booking failure with negative places."""
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