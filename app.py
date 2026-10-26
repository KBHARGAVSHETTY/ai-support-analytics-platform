from flask import Flask, render_template, g, jsonify, request
import os
from database import init_db, close_db, get_tickets, get_ticket, create_ticket, update_ticket, delete_ticket
from analytics import get_ticket_statistics
from ai_assistant import get_ai_response

def create_app():
    app = Flask(__name__)
    
    # Initialize the database
    with app.app_context():
        init_db()
    
    @app.teardown_appcontext
    def teardown_db(exc=None):
        close_db(exc)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # REST API endpoints for tickets
    @app.route('/api/tickets', methods=['GET'])
    def api_get_tickets():
        tickets = get_tickets()
        return jsonify(tickets)
    
    @app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
    def api_get_ticket(ticket_id):
        ticket = get_ticket(ticket_id)
        if ticket is None:
            return jsonify({'error': 'Ticket not found'}), 404
        return jsonify(ticket)
    
    @app.route('/api/tickets', methods=['POST'])
    def api_create_ticket():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        priority = data.get('priority')
        status = data.get('status', 'Open')
        # Validate required fields
        if not title or not description or not category or not priority:
            return jsonify({'error': 'Missing required fields: title, description, category, priority'}), 400
        ticket_id = create_ticket(title, description, category, priority, status)
        return jsonify({'id': ticket_id, 'message': 'Ticket created successfully'}), 201
    
    @app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
    def api_update_ticket(ticket_id):
        ticket = get_ticket(ticket_id)
        if ticket is None:
            return jsonify({'error': 'Ticket not found'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        title = data.get('title', ticket['title'])
        description = data.get('description', ticket['description'])
        category = data.get('category', ticket['category'])
        priority = data.get('priority', ticket['priority'])
        status = data.get('status', ticket['status'])
        update_ticket(ticket_id, title, description, category, priority, status)
        return jsonify({'message': 'Ticket updated successfully'})
    
    @app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
    def api_delete_ticket(ticket_id):
        ticket = get_ticket(ticket_id)
        if ticket is None:
            return jsonify({'error': 'Ticket not found'}), 404
        delete_ticket(ticket_id)
        return jsonify({'message': 'Ticket deleted successfully'})
    
    # Analytics endpoint
    @app.route('/api/analytics', methods=['GET'])
    def api_get_analytics():
        stats = get_ticket_statistics()
        return jsonify(stats)
    
    # AI Chat endpoint
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data['message']
        if not isinstance(message, str) or not message.strip():
            return jsonify({'error': 'Invalid message'}), 400
        
        try:
            response = get_ai_response(message)
            return jsonify({'response': response})
        except Exception as e:
            # Log the error (in a real app, you'd use proper logging)
            print(f"Error in AI assistant: {e}")
            return jsonify({'response': "I'm sorry, I encountered an error while processing your request. Please try again."})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)