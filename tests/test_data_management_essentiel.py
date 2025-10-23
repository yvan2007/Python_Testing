"""
Tests de gestion des données essentiels basés sur les spécifications
Module 1 et Module 2 - Tests et Validation
"""

import pytest
import server

class TestDataManagementEssentiel:
    """Tests essentiels de gestion des données"""
    
    def test_load_clubs_function(self):
        """Test du chargement des clubs - Test critique"""
        clubs = server.loadClubs()
        assert isinstance(clubs, list), "Clubs should be a list"
        assert len(clubs) > 0, "Should have at least one club"
        
        # Vérifier la structure des données
        for club in clubs:
            assert 'name' in club, "Club should have a name"
            assert 'email' in club, "Club should have an email"
            assert 'points' in club, "Club should have points"
    
    def test_load_competitions_function(self):
        """Test du chargement des compétitions - Test critique"""
        competitions = server.loadCompetitions()
        assert isinstance(competitions, list), "Competitions should be a list"
        assert len(competitions) > 0, "Should have at least one competition"
        
        # Vérifier la structure des données
        for comp in competitions:
            assert 'name' in comp, "Competition should have a name"
            assert 'date' in comp, "Competition should have a date"
            assert 'numberOfPlaces' in comp, "Competition should have numberOfPlaces"
    
    def test_save_clubs_function(self):
        """Test de la sauvegarde des clubs - Test critique"""
        original_clubs = server.loadClubs()
        
        # Modifier temporairement les données
        test_club = {'name': 'Test Club', 'email': 'test@example.com', 'points': '10'}
        server.clubs.append(test_club)
        
        # Sauvegarder
        server.saveClubs(server.clubs)
        
        # Recharger et vérifier
        reloaded_clubs = server.loadClubs()
        assert len(reloaded_clubs) == len(original_clubs) + 1
        
        # Restaurer les données originales
        server.clubs[:] = original_clubs
        server.saveClubs(server.clubs)
    
    def test_save_competitions_function(self):
        """Test de la sauvegarde des compétitions - Test critique"""
        original_competitions = server.loadCompetitions()
        
        # Modifier temporairement les données
        test_comp = {'name': 'Test Competition', 'date': '2024-12-31 10:00:00', 'numberOfPlaces': '25'}
        server.competitions.append(test_comp)
        
        # Sauvegarder
        server.saveCompetitions(server.competitions)
        
        # Recharger et vérifier
        reloaded_competitions = server.loadCompetitions()
        assert len(reloaded_competitions) == len(original_competitions) + 1
        
        # Restaurer les données originales
        server.competitions[:] = original_competitions
        server.saveCompetitions(server.competitions)
    
    def test_data_validation_structure(self):
        """Test de validation de la structure des données"""
        clubs = server.loadClubs()
        competitions = server.loadCompetitions()
        
        # Vérifier que les données sont valides
        assert len(clubs) > 0, "Should have clubs data"
        assert len(competitions) > 0, "Should have competitions data"
        
        # Vérifier la cohérence des données
        for club in clubs:
            assert isinstance(club.get('points', ''), str), "Points should be string"
            assert club.get('points', '').isdigit(), "Points should be numeric"
    
    def test_data_persistence_across_sessions(self):
        """Test de persistance des données entre les sessions"""
        # Charger les données
        clubs1 = server.loadClubs()
        competitions1 = server.loadCompetitions()
        
        # Simuler un redémarrage en rechargeant
        server.clubs[:] = server.loadClubs()
        server.competitions[:] = server.loadCompetitions()
        
        clubs2 = server.loadClubs()
        competitions2 = server.loadCompetitions()
        
        # Vérifier que les données sont identiques
        assert len(clubs1) == len(clubs2), "Clubs data should be consistent"
        assert len(competitions1) == len(competitions2), "Competitions data should be consistent"