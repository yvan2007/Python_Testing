import pytest
import server
import time

class TestPhase2:
    """Tests for Phase 2 - Public Transparency and Performance"""
    
    def test_public_points_display(self, client):
        """Test public points display with beautiful interface."""
        response = client.get('/points')
        assert response.status_code == 200
        assert b'Affichage des Points' in response.data
        assert b'Points de Tous les Clubs' in response.data
        assert b'Acc' in response.data  # Accès Public
    
    def test_public_points_table_structure(self, client):
        """Test that the public points table has correct structure."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les en-têtes de colonnes
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
        assert b'Total R' in response.data  # Total Réservations
        assert b'Statut' in response.data
        
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
    
    def test_public_points_table_transparency(self, client):
        """Test that the public points table shows transparency information."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les messages de transparence
        assert b'public' in response.data.lower() or b'accessible' in response.data.lower()
        assert b'transparence' in response.data.lower() or b'Transparence' in response.data
    
    def test_club_status_badges(self, client):
        """Test that club status badges are displayed correctly."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier la présence de badges de statut
        assert b'Active' in response.data or b'Moderate' in response.data or b'Low' in response.data
        assert b'badge' in response.data.lower() or b'bg-success' in response.data or b'bg-warning' in response.data or b'bg-danger' in response.data
    
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
        
        # Vérifier que la page d'accueil affiche les informations de transparence
        assert b'transparence' in response.data.lower() or b'clubs' in response.data.lower()
    
    def test_performance_points_page(self, client):
        """Test performance of points page loading."""
        start_time = time.time()
        response = client.get('/points')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should load in less than 2 seconds
    
    def test_performance_home_page(self, client):
        """Test performance of home page loading."""
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should load in less than 1 second
    
    def test_performance_login_page(self, client):
        """Test performance of login page loading."""
        start_time = time.time()
        response = client.get('/login')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should load in less than 1 second
    
    def test_responsive_design_elements(self, client):
        """Test that responsive design elements are present."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les éléments de design responsive
        assert b'container' in response.data
        assert b'row' in response.data
        assert b'col-' in response.data
        assert b'table-responsive' in response.data
    
    def test_bootstrap_integration(self, client):
        """Test that Bootstrap is properly integrated."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les classes Bootstrap
        assert b'card' in response.data
        assert b'shadow' in response.data
        assert b'btn' in response.data
        assert b'table' in response.data
    
    def test_css_animations(self, client):
        """Test that CSS animations are present."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier les animations CSS
        assert b'animation' in response.data or b'@keyframes' in response.data
        assert b'transition' in response.data or b'transform' in response.data
    
    def test_emoji_icons(self, client):
        """Test that emoji icons are present for better UX."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier la présence d'icônes emoji (encodées en UTF-8)
        assert b'\xf0\x9f\x93\x8a' in response.data or b'\xf0\x9f\x8f\x86' in response.data or b'\xf0\x9f\x8f\xa0' in response.data or b'\xf0\x9f\x94\x90' in response.data
    
    def test_error_handling_points_page(self, client):
        """Test error handling on points page."""
        # Test avec des données corrompues
        original_clubs = server.clubs.copy()
        server.clubs = []
        
        response = client.get('/points')
        assert response.status_code == 200  # Should still load even with no data
        
        # Restaurer les données
        server.clubs = original_clubs
    
    def test_data_consistency_points_display(self, client):
        """Test that points display is consistent with actual data."""
        response = client.get('/points')
        assert response.status_code == 200
        
        # Vérifier que le nombre de clubs affichés correspond aux données
        club_count = len(server.clubs)
        assert club_count > 0, "No clubs in data"
        
        # Compter les lignes de clubs dans la réponse
        club_rows = response.data.count(b'<tr class="club-row">')
        assert club_rows == club_count, f"Expected {club_count} club rows, found {club_rows}"
    
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
