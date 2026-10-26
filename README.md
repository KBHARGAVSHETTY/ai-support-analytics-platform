# AI-Powered Support & Analytics Platform

A simple web application for managing customer support tickets with basic analytics and an AI assistant.

## Features

- Create, view, update, and delete support tickets
- View ticket statistics and charts
- AI support assistant (with fallback when no API key is available)

## Technology Stack

- Python 3.x
- Flask
- SQLite
- HTML/CSS/JavaScript
- Pandas (for analytics)
- Chart.js (for charts)
- pytest (for testing)

## Setup

1. Clone or download this repository
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser to `http://localhost:5000`

## Project Structure

- `app.py` - Main Flask application
- `database.py` - Database operations
- `analytics.py` - Data analysis functions
- `ai_assistant.py` - AI support logic
- `templates/index.html` - Main dashboard page
- `static/style.css` - Custom styles
- `static/script.js` - Frontend JavaScript
- `tests/` - Unit tests

## Database

The application uses SQLite database (`support_tickets.db`) which is created automatically on first run. Sample data is inserted when the database is empty.

## API Endpoints

- `GET /api/tickets` - Retrieve all tickets
- `GET /api/tickets/<id>` - Retrieve a specific ticket
- `POST /api/tickets` - Create a new ticket
- `PUT /api/tickets/<id>` - Update a ticket
- `DELETE /api/tickets/<id>` - Delete a ticket
- `GET /api/analytics` - Get ticket statistics
- `POST /api/chat` - AI chat endpoint

## Testing

Run tests with:
```bash
pytest
```

