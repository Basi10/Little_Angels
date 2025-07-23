from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow frontend requests


@app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes():
    """Respond with 'Yes' to any request on the root route"""
    return jsonify({"response": "Yes"})


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def respond_yes_any_path(path):
    """Respond with 'Yes' to any request on any path"""
    return jsonify({"response": "Yes"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
