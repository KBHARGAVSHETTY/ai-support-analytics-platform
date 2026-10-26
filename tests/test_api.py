import sys
import os
import sqlite3
import tempfile
import time
import shutil
# Add the project root to the sys.path so we can import app and database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app import create_app
import database  # Import the module to monkey-patch DATABASE

@pytest.fixture
def client():
    # Create a temporary directory for the database file
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, 'test.db')
        original_database = database.DATABASE
        database.DATABASE = db_path

        app = create_app()
        app.config['TESTING'] = True
        app.config['DEBUG'] = False

        # Initialize the database
        with app.app_context():
            database.init_db()

        with app.test_client() as client:
            yield client

    finally:
        # Close the database connection to avoid file lock on Windows.
        with app.app_context():
            database.close_db()
        # Try to delete the database file, retrying if locked.
        for _ in range(5):
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
                break
            except PermissionError:
                time.sleep(0.2)
        # Remove the temporary directory.
        shutil.rmtree(tmpdir, ignore_errors=True)
        # Restore the original DATABASE
        database.DATABASE = original_database

def test_get_tickets_empty(client):
    # First, delete all tickets to start with a clean state
    with sqlite3.connect(database.DATABASE) as conn:
        conn.execute('DELETE FROM tickets')
        conn.commit()

    response = client.get('/api/tickets')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_ticket(client):
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'Test Ticket',
                               'description': 'Test Description',
                               'category': 'Test',
                               'priority': 'High'
                           }),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['message'] == 'Ticket created successfully'

    # Verify the ticket exists
    response = client.get(f'/api/tickets/{data["id"]}')
    assert response.status_code == 200
    ticket = json.loads(response.data)
    assert ticket['title'] == 'Test Ticket'
    assert ticket['description'] == 'Test Description'
    assert ticket['category'] == 'Test'
    assert ticket['priority'] == 'High'
    assert ticket['status'] == 'Open'  # Default status

def test_get_ticket(client):
    # First create a ticket
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'Another Ticket',
                               'description': 'Another Description',
                               'category': 'Bug',
                               'priority': 'Medium'
                           }),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    ticket_id = data['id']

    # Get the ticket
    response = client.get(f'/api/tickets/{ticket_id}')
    assert response.status_code == 200
    ticket = json.loads(response.data)
    assert ticket['id'] == ticket_id
    assert ticket['title'] == 'Another Ticket'

    # Test non-existent ticket
    response = client.get('/api/tickets/99999')
    assert response.status_code == 404

def test_update_ticket(client):
    # Create a ticket
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'Original Title',
                               'description': 'Original Description',
                               'category': 'Category',
                               'priority': 'Low'
                           }),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    ticket_id = data['id']

    # Update the ticket
    response = client.put(f'/api/tickets/{ticket_id}',
                          data=json.dumps({
                              'title': 'Updated Title',
                              'description': 'Updated Description',
                              'category': 'Updated Category',
                              'priority': 'High',
                              'status': 'Resolved'
                          }),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Ticket updated successfully'

    # Verify the update
    response = client.get(f'/api/tickets/{ticket_id}')
    assert response.status_code == 200
    ticket = json.loads(response.data)
    assert ticket['title'] == 'Updated Title'
    assert ticket['description'] == 'Updated Description'
    assert ticket['category'] == 'Updated Category'
    assert ticket['priority'] == 'High'
    assert ticket['status'] == 'Resolved'

def test_delete_ticket(client):
    # Create a ticket
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'To Delete',
                               'description': 'Will be deleted',
                               'category': 'Test',
                               'priority': 'Low'
                           }),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    ticket_id = data['id']

    # Delete the ticket
    response = client.delete(f'/api/tickets/{ticket_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Ticket deleted successfully'

    # Verify deletion
    response = client.get(f'/api/tickets/{ticket_id}')
    assert response.status_code == 404

def test_validation_missing_fields(client):
    # Missing title
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'description': 'No title',
                               'category': 'Test',
                               'priority': 'Low'
                           }),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

    # Missing description
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'No description',
                               'category': 'Test',
                               'priority': 'Low'
                           }),
                           content_type='application/json')
    assert response.status_code == 400

    # Missing category
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'No category',
                               'description': 'Some desc',
                               'priority': 'Low'
                           }),
                           content_type='application/json')
    assert response.status_code == 400

    # Missing priority
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'No priority',
                               'description': 'Some desc',
                               'category': 'Test'
                           }),
                           content_type='application/json')
    assert response.status_code == 400

def test_analytics_endpoint(client):
    # First, delete all tickets to start with a clean state
    with sqlite3.connect(database.DATABASE) as conn:
        conn.execute('DELETE FROM tickets')
        conn.commit()

    # Test analytics with no tickets
    response = client.get('/api/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Check that all expected keys are present
    expected_keys = ['total_tickets', 'open_tickets', 'resolved_tickets', 'high_priority_tickets', 'tickets_by_category', 'tickets_by_priority']
    for key in expected_keys:
        assert key in data
    # With no tickets, all counts should be zero and dicts empty
    assert data['total_tickets'] == 0
    assert data['open_tickets'] == 0
    assert data['resolved_tickets'] == 0
    assert data['high_priority_tickets'] == 0
    assert data['tickets_by_category'] == {}
    assert data['tickets_by_priority'] == {}

    # Create a ticket and check analytics update
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'Analytic Test',
                               'description': 'Test for analytics',
                               'category': 'Test',
                               'priority': 'High',
                               'status': 'Open'
                           }),
                           content_type='application/json')
    assert response.status_code == 201

    response = client.get('/api/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_tickets'] == 1
    assert data['open_tickets'] == 1
    assert data['resolved_tickets'] == 0
    assert data['high_priority_tickets'] == 1
    assert data['tickets_by_category'] == {'Test': 1}
    assert data['tickets_by_priority'] == {'High': 1}

    # Create another ticket with different category and priority
    response = client.post('/api/tickets',
                           data=json.dumps({
                               'title': 'Analytic Test 2',
                               'description': 'Second test',
                               'category': 'Bug',
                               'priority': 'Medium',
                               'status': 'Resolved'
                           }),
                           content_type='application/json')
    assert response.status_code == 201

    response = client.get('/api/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_tickets'] == 2
    assert data['open_tickets'] == 1
    assert data['resolved_tickets'] == 1
    assert data['high_priority_tickets'] == 1
    assert data['tickets_by_category'] == {'Test': 1, 'Bug': 1}
    assert data['tickets_by_priority'] == {'High': 1, 'Medium': 1}

def test_chat_endpoint(client):
    # Test chat with no API key (should use fallback)
    response = client.post('/api/chat',
                           data=json.dumps({
                               'message': 'Hello'
                           }),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert isinstance(data['response'], str)
    assert len(data['response']) > 0

    # Test chat with a login question
    response = client.post('/api/chat',
                           data=json.dumps({
                               'message': 'How do I login?'
                           }),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    # Should contain login-related information
    assert 'login' in data['response'].lower() or 'password' in data['response'].lower()

    # Test chat with a statistics question
    response = client.post('/api/chat',
                           data=json.dumps({
                               'message': 'How many tickets are there?'
                           }),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    # Should mention ticket counts
    assert 'ticket' in data['response'].lower()

    # Test chat with invalid input (no message)
    response = client.post('/api/chat',
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

    # Test chat with empty message
    response = client.post('/api/chat',
                           data=json.dumps({
                               'message': ''
                           }),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data