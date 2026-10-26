import sqlite3
import os
from flask import g

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'support_tickets.db')

def get_db():
    """Get database connection."""
    if 'db' not in g:
        # Determine if DATABASE is a URI
        uri = DATABASE.startswith('file:') or '://' in DATABASE
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES,
            uri=uri
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with tables and sample data."""
    db = get_db()
    schema_path = os.path.join(basedir, 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())
    # Insert sample data only if the table is empty
    cursor = db.execute('SELECT COUNT(*) FROM tickets')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_tickets = [
            ('Login issue', 'Cannot login to the application', 'Authentication', 'High', 'Open'),
            ('Payment failed', 'Payment gateway timeout', 'Billing', 'Medium', 'Open'),
            ('Feature request', 'Add dark mode to the UI', 'UI/UX', 'Low', 'Open'),
            ('Password reset', 'Email not received for password reset', 'Authentication', 'High', 'Resolved'),
            ('Dashboard loading slow', 'Dashboard takes more than 5 seconds to load', 'Performance', 'Medium', 'Open')
        ]
        db.executemany(
            'INSERT INTO tickets (title, description, category, priority, status) VALUES (?, ?, ?, ?, ?)',
            sample_tickets
        )
    db.commit()

def get_tickets():
    """Return all tickets as a list of dictionaries."""
    db = get_db()
    tickets = db.execute('SELECT * FROM tickets ORDER BY created_at DESC').fetchall()
    return [dict(ticket) for ticket in tickets]

def get_ticket(ticket_id):
    """Return a ticket by id as a dictionary, or None if not found."""
    db = get_db()
    ticket = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    return dict(ticket) if ticket else None

def create_ticket(title, description, category, priority, status='Open'):
    """Create a new ticket and return the new ticket's id."""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO tickets (title, description, category, priority, status) VALUES (?, ?, ?, ?, ?)',
        (title, description, category, priority, status)
    )
    db.commit()
    return cursor.lastrowid

def update_ticket(ticket_id, title, description, category, priority, status):
    """Update an existing ticket."""
    db = get_db()
    db.execute(
        '''UPDATE tickets 
           SET title = ?, description = ?, category = ?, priority = ?, status = ?
           WHERE id = ?''',
        (title, description, category, priority, status, ticket_id)
    )
    db.commit()

def delete_ticket(ticket_id):
    """Delete a ticket by id."""
    db = get_db()
    db.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
    db.commit()