"""
Tests d'intégration essentiels basés sur les spécifications
Module 1 et Module 2 - Tests et Validation
"""

import pytest
import time
import server

class TestIntegrationEssentiel:
    """Tests d'intégration essentiels pour le workflow complet"""
    
    def test_complete_booking_workflow(self, client, restore_data):
        """Test du workflow complet de réservation - Test critique"""
        # 1. Accéder à la page d'accueil
        response = client.get('/')
        assert response.status_code == 200
        assert b'Nom du Club' in response.data
        
        # 2. Se connecter avec un club valide
        valid_club = None
        for club in server.clubs:
            if club.get('email') and int(club.get('points', 0)) >= 3:
                valid_club = club
                break
        
        assert valid_club is not None, "No valid club found for testing"
        
        response = client.post('/showSummary', data={'email': valid_club['email']})
        assert response.status_code == 200
        assert valid_club['email'].encode() in response.data
        
        # 3. Effectuer une réservation
        valid_comp = None
        for comp in server.competitions:
            if int(comp.get('numberOfPlaces', 0)) >= 2:
                valid_comp = comp
                break
        
        assert valid_comp is not None, "No valid competition found for testing"
        
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '2'
        })
        
        assert response.status_code == 200
        assert b'R\xc3\xa9servation r\xc3\xa9ussie' in response.data
    
    def test_public_points_integration(self, client):
        """Test d'intégration avec l'affichage public des points"""
        # 1. Accéder à la page publique des points
        response = client.get('/points')
        assert response.status_code == 200
        assert b'Affichage des Points' in response.data
        
        # 2. Vérifier que les données sont cohérentes
        club_count = len(server.clubs)
        assert club_count > 0, "No clubs found"
        
        # 3. Vérifier la structure du tableau
        assert b'Nom du Club' in response.data
        assert b'Points Disponibles' in response.data
        assert b'Statut' in response.data
    
    def test_data_persistence_across_requests(self, client, restore_data):
        """Test de persistance des données entre les requêtes"""
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
        
        assert valid_club is not None, "No valid club found for testing"
        assert valid_comp is not None, "No valid competition found for testing"
        
        initial_points = int(valid_club['points'])
        
        # Effectuer une réservation
        response = client.post('/purchasePlaces', data={
            'competition': valid_comp['name'],
            'club': valid_club['name'],
            'places': '3'
        })
        
        assert response.status_code == 200
        
        # Vérifier que les données sont persistées
        server.clubs[:] = server.loadClubs()
        updated_club = next((c for c in server.clubs if c['name'] == valid_club['name']), None)
        assert updated_club is not None, "Club not found after update"
        assert int(updated_club['points']) == initial_points - 3
    
    def test_error_recovery_workflow(self, client):
        """Test de récupération après erreur"""
        # Test avec des données invalides
        response = client.post('/purchasePlaces', data={
            'competition': 'Competition Inexistante',
            'club': 'Club Inexistant',
            'places': '5'
        })
        
        assert response.status_code == 200
        assert b'Comp\xc3\xa9tition ou club non trouv\xc3\xa9' in response.data
