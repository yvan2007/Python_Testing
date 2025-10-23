import pytest
import json
import os
import tempfile
from unittest.mock import patch
import server

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client

@pytest.fixture
def backup_data():
    """Backup original data before tests."""
    original_clubs = server.clubs.copy()
    original_competitions = server.competitions.copy()
    yield
    server.clubs[:] = original_clubs
    server.competitions[:] = original_competitions
    # Sauvegarder les données dans les fichiers JSON
    server.saveClubs(server.clubs)
    server.saveCompetitions(server.competitions)

@pytest.fixture
def restore_data(backup_data):
    """Restore data after each test."""
    # Recharger les données depuis les fichiers JSON
    server.clubs[:] = server.loadClubs()
    server.competitions[:] = server.loadCompetitions()

@pytest.fixture
def test_club():
    """Provide a test club for testing."""
    return {
        'name': 'Test Club',
        'email': 'test@example.com',
        'points': '10'
    }

@pytest.fixture
def test_competition():
    """Provide a test competition for testing."""
    return {
        'name': 'Test Competition',
        'date': '2024-12-31 10:00:00',
        'numberOfPlaces': '25'
    }
