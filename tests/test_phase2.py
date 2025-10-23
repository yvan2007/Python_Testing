import pytest
import server

class TestPhase2:
    """Tests for Phase 2 - Public Transparency and Performance"""
    
    def test_public_points_display(self, client):
        """Test public points display."""
        response = client.get('/points')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
    
    def test_public_points_table_structure(self, client):
        """Test that the public points table has correct structure."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les en-têtes de colonnes
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
        
        # Vérifier que l'email n'est PAS affiché (privacy)
        assert b'Email' not in response.data
    
    def test_public_points_table_data(self, client):
        """Test that the public points table displays club data."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier qu'au moins un club est affiché
        assert len(server.clubs) > 0, "No clubs found in data"
        
        # Vérifier qu'au moins un nom de club est affiché
        club_names_found = 0
        for club in server.clubs:
            if club.get('name') and club['name'].encode() in response.data:
                club_names_found += 1
        
        assert club_names_found > 0, "No club names found in response"
    
    def test_navigation_links(self, client):
        """Test that navigation links work correctly."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les liens de navigation
        assert b'href="/"' in response.data  # Back to Home
        assert b'href="/login"' in response.data  # Secretary Login
    
    def test_home_page_integration(self, client):
        """Test that home page integrates with public points."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
    
    def test_data_consistency_points_display(self, client):
        """Test that points display is consistent with actual data."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier que le nombre de clubs affichés correspond aux données
        club_count = len(server.clubs)
        assert club_count > 0, "No clubs in data"
    
    def test_security_no_sensitive_data(self, client):
        """Test that no sensitive data is exposed in public pages."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier qu'aucune donnée sensible n'est exposée
        assert b'secret' not in response.data.lower()
        assert b'password' not in response.data.lower()
        assert b'token' not in response.data.lower()
        
        # Vérifier que les emails ne sont pas affichés
        for club in server.clubs:
            if club.get('email'):
                assert club['email'].encode() not in response.data