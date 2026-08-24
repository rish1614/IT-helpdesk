from flask import Flask, jsonify, render_template, request
from pymongo.errors import PyMongoError

from config import Config
from routes.ticket_routes import ticket_bp
from services.ticket_service import MongoTicketRepository, InMemoryTicketRepository, TicketService


def create_app(testing=False, repository=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TESTING"] = testing

    if repository is None:
        if testing or app.config.get("USE_IN_MEMORY_DB"):
            repository = InMemoryTicketRepository()
        else:
            repository = MongoTicketRepository(
                app.config["MONGO_URI"],
                app.config["DB_NAME"],
                app.config["TICKETS_COLLECTION"],
            )

    app.ticket_service = TicketService(repository)
    app.register_blueprint(ticket_bp)

    @app.route("/")
    def dashboard():
        return render_template("index.html")

    @app.route("/tickets/new")
    def create_ticket_page():
        return render_template("create_ticket.html")

    @app.route("/tickets/<ticket_id>")
    def ticket_detail_page(ticket_id):
        return render_template("ticket.html", ticket_id=ticket_id)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(PyMongoError)
    def database_error(error):
        app.logger.exception("Database error: %s", error)
        return jsonify({"error": "Database failure", "message": "Could not complete the database operation."}), 503

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("Unexpected error: %s", error)
        return jsonify({"error": "Internal server error", "message": "Something went wrong."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
