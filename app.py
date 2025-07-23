from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

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


@app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes():
    """Respond with 'Yes' to any request on the root route"""
    return jsonify({"response": "Yes"})


@app.route("/submit", methods=["POST"])
def handle_form_submission():
    """Handle form submission from the frontend and log all data"""
    try:
        # Get JSON data from the request
        form_data = request.get_json()

        if not form_data:
            app.logger.error("No data received in form submission")
            return jsonify({"error": "No data received"}), 400

        # Log the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log all received data
        app.logger.info("=" * 50)
        app.logger.info(f"NEW FORM SUBMISSION - {timestamp}")
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

        # Return success response
        return (
            jsonify(
                {
                    "response": "Yes",
                    "message": "Form data received and logged successfully",
                    "timestamp": timestamp,
                    "data_received": len(form_data),
                }
            ),
            200,
        )

    except Exception as e:
        app.logger.error(f"Error processing form submission: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes_any_path(path):
    """Respond with 'Yes' to any request on any other path"""
    return jsonify({"response": "Yes"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
