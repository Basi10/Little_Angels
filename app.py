from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import ssl

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow frontend requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("form_submissions.log"),
        logging.StreamHandler(),  # Also log to console
    ],
)

# MongoDB Atlas Configuration
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://little_angels_basilel:g2wBNDnHZbLHIC0b@littleanglescluster.zuhxodt.mongodb.net/?retryWrites=true&w=majority&appName=LittleAnglesCluster",
)

# Initialize MongoDB connection with SSL configuration
try:
    # Try with server API first (your current approach)
    app.logger.info("Attempting MongoDB connection with Server API...")
    client = MongoClient(
        MONGO_URI,
        server_api=ServerApi("1"),
        tlsAllowInvalidCertificates=True,  # For development/testing
        retryWrites=True,
        connectTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
    )

    # Test the connection
    client.admin.command("ping")
    app.logger.info("Successfully connected to MongoDB Atlas with Server API")

except Exception as e:
    app.logger.warning(f"Server API connection failed: {str(e)}")
    app.logger.info("Trying alternative connection method...")

    try:
        # Alternative connection without Server API
        client = MongoClient(
            MONGO_URI,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,  # Disable certificate verification for development
            connectTimeoutMS=30000,
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
        )

        # Test the connection
        client.admin.command("ping")
        app.logger.info(
            "Successfully connected to MongoDB Atlas with alternative method"
        )

    except Exception as e2:
        app.logger.error(f"All MongoDB connection attempts failed:")
        app.logger.error(f"  Server API method: {str(e)}")
        app.logger.error(f"  Alternative method: {str(e2)}")
        client = None

# Set up database and collection
if client:
    try:
        db = client["little_angels_db"]  # Database name
        collection = db["form_submissions"]  # Collection name
        app.logger.info("Database and collection initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        db = None
        collection = None
else:
    db = None
    collection = None


def save_to_mongodb(form_data):
    """Save form data to MongoDB Atlas"""
    try:
        if collection is None:
            app.logger.error("MongoDB collection not available")
            return False

        # Add timestamp to the document
        document = {
            **form_data,
            "submitted_at": datetime.utcnow(),
            "submission_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        }

        # Insert the document
        result = collection.insert_one(document)
        app.logger.info(f"Data saved to MongoDB with ID: {result.inserted_id}")
        return True

    except Exception as e:
        app.logger.error(f"Error saving to MongoDB: {str(e)}")
        return False


@app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes():
    """Respond with 'Yes' to any request on the root route"""
    return jsonify({"response": "Yes"})


@app.route("/submit", methods=["POST"])
def handle_form_submission():
    """Handle form submission from the frontend, save to MongoDB and log all data"""
    try:
        # Get JSON data from the request
        form_data = request.get_json()

        if not form_data:
            app.logger.error("No data received in form submission")
            return jsonify({"error": "No data received"}), 400

        # Check for duplicate phone numbers before saving
        if collection is not None and form_data.get("main_phone"):
            main_phone = form_data.get("main_phone")
            alt_phone = form_data.get("alt_phone")

            # Check if main phone already exists
            existing_client = collection.find_one(
                {"$or": [{"main_phone": main_phone}, {"alt_phone": main_phone}]}
            )

            if existing_client:
                app.logger.warning(
                    f"Duplicate main phone number attempted: {main_phone}"
                )
                return (
                    jsonify(
                        {
                            "error": f"Phone number +251{main_phone} is already registered to another client"
                        }
                    ),
                    400,
                )

            # Check if alternate phone already exists (if provided)
            if alt_phone:
                existing_alt_client = collection.find_one(
                    {"$or": [{"main_phone": alt_phone}, {"alt_phone": alt_phone}]}
                )

                if existing_alt_client:
                    app.logger.warning(
                        f"Duplicate alternate phone number attempted: {alt_phone}"
                    )
                    return (
                        jsonify(
                            {
                                "error": f"Alternate phone number +251{alt_phone} is already registered to another client"
                            }
                        ),
                        400,
                    )

        # Log the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to MongoDB first
        mongodb_success = save_to_mongodb(form_data)

        # Log all received data (existing functionality)
        app.logger.info("=" * 50)
        app.logger.info(f"NEW FORM SUBMISSION - {timestamp}")
        app.logger.info(f"MongoDB Save: {'SUCCESS' if mongodb_success else 'FAILED'}")
        app.logger.info("=" * 50)

        # Log personal information
        app.logger.info("PERSONAL INFORMATION:")
        app.logger.info(f"  Name: {form_data.get('user_name', 'N/A')}")
        app.logger.info(f"  Gender: {form_data.get('gender', 'N/A')}")
        app.logger.info(
            f"  Age: {form_data.get('age_years', 'N/A')} years, {form_data.get('age_months', 'N/A')} months"
        )
        app.logger.info(f"  Main Phone: +251{form_data.get('main_phone', 'N/A')}")
        app.logger.info(
            f"  Alt Phone: +251{form_data.get('alt_phone', 'N/A') if form_data.get('alt_phone') else 'N/A'}"
        )

        # Log package information
        app.logger.info("PACKAGE INFORMATION:")
        app.logger.info(f"  Package: {form_data.get('package', 'N/A')}")
        app.logger.info(f"  Choice: {form_data.get('user_choice', 'N/A')}")

        # Log interests
        interests = form_data.get("interests", [])
        app.logger.info(f"  Interests: {', '.join(interests) if interests else 'None'}")

        # Log payment information
        app.logger.info("PAYMENT INFORMATION:")
        app.logger.info(f"  Total Payment: {form_data.get('total', 'N/A')}")
        app.logger.info(f"  Initial Payment: {form_data.get('initial', 'N/A')}")
        app.logger.info(f"  Remaining Amount: {form_data.get('remaining', 'N/A')}")

        # Log complete raw data for debugging
        app.logger.info("RAW FORM DATA:")
        app.logger.info(f"  {form_data}")

        app.logger.info("=" * 50)

        # Return success response with MongoDB status
        response_data = {
            "response": "Yes",
            "message": "Form data received and logged successfully",
            "timestamp": timestamp,
            "data_received": len(form_data),
            "mongodb_saved": mongodb_success,
        }

        if not mongodb_success:
            response_data["warning"] = "Data was logged but not saved to database"

        return jsonify(response_data), 200

    except Exception as e:
        app.logger.error(f"Error processing form submission: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint that includes MongoDB status"""
    mongodb_status = "disconnected"
    connection_details = {}

    try:
        if client:
            # Try to ping the server
            result = client.admin.command("ping")
            mongodb_status = "connected"
            connection_details = {
                "ping_response": result,
                "database": "little_angels_db",
                "collection": "form_submissions",
            }
    except Exception as e:
        mongodb_status = f"error: {str(e)}"
        connection_details = {"error": str(e)}

    return jsonify(
        {
            "status": "healthy",
            "mongodb": mongodb_status,
            "connection_details": connection_details,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/submissions", methods=["GET"])
def get_submissions():
    """Get recent form submissions (for testing/admin purposes)"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get last 10 submissions, sorted by submission time
        submissions = list(
            collection.find({}, {"_id": 0}).sort("submitted_at", -1).limit(10)
        )

        return jsonify({"submissions": submissions, "count": len(submissions)})

    except Exception as e:
        app.logger.error(f"Error retrieving submissions: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/search-client", methods=["GET"])
def search_client():
    """Search for a client by phone number or name"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get search parameters from query string
        phone = request.args.get("phone", "").strip()
        name = request.args.get("name", "").strip()

        if not phone and not name:
            return (
                jsonify(
                    {"error": "Please provide either phone number or name to search"}
                ),
                400,
            )

        # Build search query
        search_query = {}

        if phone:
            # Search by phone number (main_phone or alt_phone)
            search_query = {"$or": [{"main_phone": phone}, {"alt_phone": phone}]}
        elif name:
            # Search by name (case-insensitive)
            search_query = {"user_name": {"$regex": name, "$options": "i"}}

        # Find clients matching the search criteria
        clients = list(
            collection.find(search_query, {"_id": 0}).sort("submitted_at", -1)
        )

        if not clients:
            return jsonify(
                {
                    "message": "No clients found matching your search criteria",
                    "clients": [],
                    "count": 0,
                }
            )

        return jsonify(
            {
                "message": f"Found {len(clients)} client(s)",
                "clients": clients,
                "count": len(clients),
            }
        )

    except Exception as e:
        app.logger.error(f"Error searching for client: {str(e)}")
        return jsonify({"error": f"Search error: {str(e)}"}), 500


@app.route("/all-clients", methods=["GET"])
def get_all_clients():
    """Get all registered clients"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get all clients, sorted by registration date (newest first)
        clients = list(collection.find({}, {"_id": 0}).sort("submitted_at", -1))

        return jsonify(
            {
                "message": f"Retrieved {len(clients)} client(s)",
                "clients": clients,
                "count": len(clients),
            }
        )

    except Exception as e:
        app.logger.error(f"Error retrieving all clients: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/test-connection", methods=["GET"])
def test_connection():
    """Test MongoDB connection and provide diagnostic information"""
    diagnostics = {
        "connection_string": MONGO_URI.replace(
            MONGO_URI.split("@")[0].split("//")[1], "***:***"
        ),  # Hide credentials
        "client_status": "initialized" if client else "not_initialized",
        "database_status": "available" if db else "not_available",
        "collection_status": "available" if collection else "not_available",
    }

    try:
        if client:
            # Test basic connection
            result = client.admin.command("ping")
            diagnostics["ping_result"] = result

            # Test database access
            databases = client.list_database_names()
            diagnostics["available_databases"] = databases

            # Test collection access if database exists
            if db:
                collections = db.list_collection_names()
                diagnostics["available_collections"] = collections

        return jsonify(diagnostics)

    except Exception as e:
        diagnostics["error"] = str(e)
        return jsonify(diagnostics), 500


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes_any_path(path):
    """Respond with 'Yes' to any request on any other path"""
    return jsonify({"response": "Yes"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
