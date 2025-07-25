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
    """Search for a client by phone number only"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get phone parameter from query string
        phone = request.args.get("phone", "").strip()

        if not phone:
            return jsonify({"error": "Please provide a phone number to search"}), 400

        # Validate phone number format (should be 9 digits)
        if not phone.isdigit() or len(phone) != 9:
            return jsonify({"error": "Phone number must be exactly 9 digits"}), 400

        # Search by phone number (main_phone or alt_phone)
        search_query = {"$or": [{"main_phone": phone}, {"alt_phone": phone}]}

        # Find clients matching the search criteria
        clients = list(
            collection.find(search_query, {"_id": 0}).sort("submitted_at", -1)
        )

        if not clients:
            return jsonify(
                {
                    "message": f"No client found with phone number +251{phone}",
                    "clients": [],
                    "count": 0,
                }
            )

        return jsonify(
            {
                "message": f"Found {len(clients)} client(s) with phone number +251{phone}",
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


@app.route("/add-waiting-list", methods=["POST"])
def add_to_waiting_list():
    """Add a client to the waiting list"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get JSON data from the request
        waiting_data = request.get_json()

        if not waiting_data:
            app.logger.error("No data received for waiting list submission")
            return jsonify({"error": "No data received"}), 400

        # Validate required fields
        required_fields = ["name", "phone"]
        for field in required_fields:
            if not waiting_data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check for duplicate phone numbers in both collections
        phone = waiting_data.get("phone")
        alt_phone = waiting_data.get("alt_phone")

        # Check in main clients collection
        existing_client = collection.find_one(
            {"$or": [{"main_phone": phone}, {"alt_phone": phone}]}
        )

        if existing_client:
            return (
                jsonify(
                    {
                        "error": f"Phone number +251{phone} is already registered as a client"
                    }
                ),
                400,
            )

        # Check in waiting list collection
        waiting_collection = db["waiting_list"]
        existing_waiting = waiting_collection.find_one(
            {"$or": [{"phone": phone}, {"alt_phone": phone}]}
        )

        if existing_waiting:
            return (
                jsonify(
                    {
                        "error": f"Phone number +251{phone} is already on the waiting list"
                    }
                ),
                400,
            )

        # Check alternate phone if provided
        if alt_phone:
            existing_alt_client = collection.find_one(
                {"$or": [{"main_phone": alt_phone}, {"alt_phone": alt_phone}]}
            )

            if existing_alt_client:
                return (
                    jsonify(
                        {
                            "error": f"Alternate phone number +251{alt_phone} is already registered as a client"
                        }
                    ),
                    400,
                )

            existing_alt_waiting = waiting_collection.find_one(
                {"$or": [{"phone": alt_phone}, {"alt_phone": alt_phone}]}
            )

            if existing_alt_waiting:
                return (
                    jsonify(
                        {
                            "error": f"Alternate phone number +251{alt_phone} is already on the waiting list"
                        }
                    ),
                    400,
                )

        # Add timestamp and ID
        document = {
            **waiting_data,
            "submitted_at": datetime.utcnow(),
            "submission_id": str(datetime.utcnow().timestamp()).replace(".", ""),
            "status": "waiting",
        }

        # Insert into waiting list collection
        result = waiting_collection.insert_one(document)
        app.logger.info(f"Waiting list entry saved with ID: {result.inserted_id}")

        # Log the waiting list entry
        app.logger.info("=" * 50)
        app.logger.info(
            f"NEW WAITING LIST ENTRY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        app.logger.info(f"Name: {waiting_data.get('name')}")
        app.logger.info(f"Phone: +251{waiting_data.get('phone')}")
        app.logger.info(f"Alt Phone: +251{waiting_data.get('alt_phone', 'N/A')}")
        app.logger.info(f"Notes: {waiting_data.get('notes', 'None')}")
        app.logger.info("=" * 50)

        return (
            jsonify(
                {
                    "message": "Successfully added to waiting list",
                    "submission_id": document["submission_id"],
                }
            ),
            200,
        )

    except Exception as e:
        app.logger.error(f"Error adding to waiting list: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/waiting-list", methods=["GET"])
def get_waiting_list():
    """Get all clients on the waiting list"""
    try:
        if db is None:
            return jsonify({"error": "MongoDB not available"}), 503

        waiting_collection = db["waiting_list"]

        # Get all waiting list entries, sorted by submission date (newest first)
        waiting_clients = list(
            waiting_collection.find({}, {"_id": 0}).sort("submitted_at", -1)
        )

        return jsonify(
            {
                "message": f"Retrieved {len(waiting_clients)} waiting list entr{'y' if len(waiting_clients) == 1 else 'ies'}",
                "waiting_clients": waiting_clients,
                "count": len(waiting_clients),
            }
        )

    except Exception as e:
        app.logger.error(f"Error retrieving waiting list: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/update-client", methods=["PUT"])
def update_client():
    """Update an existing client's information"""
    try:
        if collection is None:
            return jsonify({"error": "MongoDB not available"}), 503

        # Get JSON data from the request
        update_data = request.get_json()

        if not update_data:
            app.logger.error("No data received for client update")
            return jsonify({"error": "No data received"}), 400

        # Get the original phone number to identify the client
        original_phone = update_data.get("original_phone")
        if not original_phone:
            return (
                jsonify({"error": "Original phone number is required for update"}),
                400,
            )

        # Find the existing client
        existing_client = collection.find_one(
            {"$or": [{"main_phone": original_phone}, {"alt_phone": original_phone}]}
        )

        if not existing_client:
            return (
                jsonify(
                    {"error": f"No client found with phone number +251{original_phone}"}
                ),
                400,
            )

        # Get the new phone numbers
        new_main_phone = update_data.get("main_phone")
        new_alt_phone = update_data.get("alt_phone")

        if not new_main_phone:
            return jsonify({"error": "Main phone number is required"}), 400

        # Validate phone number format
        if not new_main_phone.isdigit() or len(new_main_phone) != 9:
            return jsonify({"error": "Main phone number must be exactly 9 digits"}), 400

        if new_alt_phone and (not new_alt_phone.isdigit() or len(new_alt_phone) != 9):
            return (
                jsonify({"error": "Alternate phone number must be exactly 9 digits"}),
                400,
            )

        # Check for duplicates (excluding the current client)
        current_submission_id = existing_client.get("submission_id")

        # Check if new main phone is already used by another client
        duplicate_main = collection.find_one(
            {
                "$and": [
                    {"submission_id": {"$ne": current_submission_id}},
                    {
                        "$or": [
                            {"main_phone": new_main_phone},
                            {"alt_phone": new_main_phone},
                        ]
                    },
                ]
            }
        )

        if duplicate_main:
            return (
                jsonify(
                    {
                        "error": f"Phone number +251{new_main_phone} is already registered to another client"
                    }
                ),
                400,
            )

        # Check if new alt phone is already used by another client (if provided)
        if new_alt_phone:
            duplicate_alt = collection.find_one(
                {
                    "$and": [
                        {"submission_id": {"$ne": current_submission_id}},
                        {
                            "$or": [
                                {"main_phone": new_alt_phone},
                                {"alt_phone": new_alt_phone},
                            ]
                        },
                    ]
                }
            )

            if duplicate_alt:
                return (
                    jsonify(
                        {
                            "error": f"Alternate phone number +251{new_alt_phone} is already registered to another client"
                        }
                    ),
                    400,
                )

        # Prepare update data (remove original_phone as it's not part of the client data)
        client_update = {
            key: value for key, value in update_data.items() if key != "original_phone"
        }

        # Add update timestamp
        client_update["last_updated"] = datetime.utcnow()
        client_update["updated_by"] = (
            "admin"  # You could make this dynamic based on user authentication
        )

        # Update the client
        result = collection.update_one(
            {"submission_id": current_submission_id}, {"$set": client_update}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Client not found for update"}), 404

        if result.modified_count == 0:
            return jsonify({"message": "No changes were made to the client data"}), 200

        # Log the update
        app.logger.info("=" * 50)
        app.logger.info(
            f"CLIENT UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        app.logger.info(f"Submission ID: {current_submission_id}")
        app.logger.info(f"Original Phone: +251{original_phone}")
        app.logger.info(f"New Main Phone: +251{new_main_phone}")
        app.logger.info(f"Updated Fields: {list(client_update.keys())}")
        app.logger.info("=" * 50)

        return (
            jsonify(
                {
                    "message": "Client information updated successfully",
                    "updated_fields": list(client_update.keys()),
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                }
            ),
            200,
        )

    except Exception as e:
        app.logger.error(f"Error updating client: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


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
