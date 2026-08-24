from copy import deepcopy
from datetime import datetime, timezone

from pymongo import MongoClient, DESCENDING, ReturnDocument


def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class MongoTicketRepository:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.collection = self.client[db_name][collection_name]

    def next_ticket_id(self):
        last = self.collection.find_one(sort=[("_id", DESCENDING)])
        if not last:
            return "IT-1001"
        try:
            return f"IT-{int(last['_id'].split('-')[1]) + 1}"
        except (KeyError, IndexError, ValueError):
            return "IT-1001"

    def insert(self, ticket):
        self.collection.insert_one(ticket)
        return ticket

    def find_all(self):
        return list(self.collection.find().sort("created_at", DESCENDING))

    def find_by_id(self, ticket_id):
        return self.collection.find_one({"_id": ticket_id})

    def update(self, ticket_id, updates):
        result = self.collection.find_one_and_update(
            {"_id": ticket_id}, {"$set": updates}, return_document=ReturnDocument.AFTER
        )
        return result

    def delete(self, ticket_id):
        return self.collection.delete_one({"_id": ticket_id}).deleted_count == 1


class InMemoryTicketRepository:
    def __init__(self):
        self.tickets = {}
        self.counter = 1000

    def next_ticket_id(self):
        self.counter += 1
        return f"IT-{self.counter}"

    def insert(self, ticket):
        self.tickets[ticket["_id"]] = deepcopy(ticket)
        return deepcopy(ticket)

    def find_all(self):
        return sorted((deepcopy(t) for t in self.tickets.values()), key=lambda t: t["created_at"], reverse=True)

    def find_by_id(self, ticket_id):
        ticket = self.tickets.get(ticket_id)
        return deepcopy(ticket) if ticket else None

    def update(self, ticket_id, updates):
        if ticket_id not in self.tickets:
            return None
        self.tickets[ticket_id].update(deepcopy(updates))
        return deepcopy(self.tickets[ticket_id])

    def delete(self, ticket_id):
        return self.tickets.pop(ticket_id, None) is not None


class TicketService:
    def __init__(self, repository):
        self.repository = repository

    def create_ticket(self, data):
        now = utc_now_iso()
        ticket = {
            "_id": self.repository.next_ticket_id(),
            "name": data["name"].strip(),
            "email": data["email"].strip(),
            "category": data["category"],
            "priority": data["priority"],
            "description": data["description"].strip(),
            "status": "Open",
            "resolution": "",
            "created_at": now,
            "updated_at": now,
        }
        return self.repository.insert(ticket)

    def list_tickets(self, search=None, category=None, priority=None, status=None):
        tickets = self.repository.find_all()
        if search:
            term = search.lower()
            tickets = [t for t in tickets if term in t["_id"].lower() or term in t["name"].lower() or term in t["email"].lower()]
        if category:
            tickets = [t for t in tickets if t["category"] == category]
        if priority:
            tickets = [t for t in tickets if t["priority"] == priority]
        if status:
            tickets = [t for t in tickets if t["status"] == status]
        return tickets

    def get_ticket(self, ticket_id):
        return self.repository.find_by_id(ticket_id)

    def update_ticket(self, ticket_id, data):
        updates = {key: value.strip() if isinstance(value, str) else value for key, value in data.items() if key in {"status", "priority", "resolution"}}
        updates["updated_at"] = utc_now_iso()
        return self.repository.update(ticket_id, updates)

    def delete_ticket(self, ticket_id):
        return self.repository.delete(ticket_id)
