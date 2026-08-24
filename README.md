# IT Helpdesk Ticket Management System

A Flask-based web application for creating, tracking, filtering, and resolving IT support tickets. It is designed as a small but complete full-stack project that demonstrates application development, validation, testing, debugging, documentation, and deployment readiness.

## Features

- Employee ticket creation with name, email, category, priority, and description.
- Support dashboard with totals for all tickets, open tickets, in-progress tickets, resolved tickets, and high/critical tickets.
- Search by ticket ID, employee name, or email.
- Filters for category, priority, and status.
- Ticket detail page for updating status, priority, and resolution notes.
- REST API for create, fetch, update, and delete operations.
- Input validation and structured error responses.
- Pytest coverage for success cases, invalid input, missing body, invalid JSON, fetch, update, invalid status, and invalid ticket IDs.

## Architecture

```text
User
  |
  v
Frontend: HTML + CSS + JavaScript
  |
  | HTTP/JSON
  v
Flask Backend: Routes + Validation + Business Logic
  |
  | PyMongo
  v
MongoDB Atlas: tickets collection
```

For tests, the app uses an in-memory repository so the test suite can run without a live MongoDB connection.

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: MongoDB, PyMongo
- Testing: Pytest
- Deployment: Render + MongoDB Atlas

## Project Structure

```text
.
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── routes/
│   ├── __init__.py
│   └── ticket_routes.py
├── services/
│   ├── __init__.py
│   └── ticket_service.py
├── utils/
│   ├── __init__.py
│   └── validators.py
├── templates/
│   ├── index.html
│   ├── create_ticket.html
│   └── ticket.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── tests/test_tickets.py
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/tickets` | Create a ticket |
| `GET` | `/api/tickets` | Fetch all tickets with optional search/filter query parameters |
| `GET` | `/api/tickets/<ticket_id>` | Fetch one ticket |
| `PUT` | `/api/tickets/<ticket_id>` | Update ticket status, priority, or resolution |
| `DELETE` | `/api/tickets/<ticket_id>` | Delete a ticket |

## Database Schema

```json
{
  "_id": "IT-1001",
  "name": "Rishabh Shukla",
  "email": "rishabh@gmail.com",
  "category": "Network",
  "priority": "High",
  "description": "Unable to connect to campus Wi-Fi",
  "status": "Open",
  "resolution": "",
  "created_at": "2026-08-24T12:30:00+00:00",
  "updated_at": "2026-08-24T12:30:00+00:00"
}
```

## Validation

- Name: required, minimum 2 characters.
- Email: required, basic email format.
- Category: Hardware, Software, Network, Account, or Other.
- Priority: Low, Medium, High, or Critical.
- Status: Open, In Progress, or Resolved.
- Description: required, minimum 10 characters.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open `http://127.0.0.1:5000`.

## Environment Variables

Create a `.env` file locally. Do not commit real credentials.

```text
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>/<database>
DB_NAME=it_helpdesk
FLASK_DEBUG=false
```

For local UI testing without MongoDB, set:

```text
USE_IN_MEMORY_DB=true
```

## Testing and Debugging

Run:

```bash
pytest -v
```

The tests verify valid ticket creation, missing fields, invalid email, invalid priority, invalid category, missing request body, invalid JSON, fetching tickets, search/filter behavior, ticket updates, invalid status, invalid ticket IDs, and updates for missing tickets.

## Deployment

Render configuration:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables: `MONGO_URI`, `DB_NAME`, and `FLASK_DEBUG=false`

Use MongoDB Atlas for the production database and keep credentials in Render environment variables.

## Future Improvements

- Add authentication for employees and support staff.
- Add ticket assignment to support agents.
- Add comments and ticket history.
- Add CSV export for reporting.
- Add screenshots after deployment.
