# Little_Angels
Little Angels Backend Application

## Simple Backend that Responds with 'Yes'

This is a simple Flask backend application that responds with 'Yes' to any request from the frontend.

## Setup and Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000` and will respond with `{"response": "Yes"}` to any request on any path with any HTTP method (GET, POST, PUT, DELETE, PATCH).

## Features

- Responds with 'Yes' to all requests
- CORS enabled for frontend communication
- Accepts all HTTP methods
- Works on any path/route
- JSON response format

## Example Usage

You can test the backend with curl:
```bash
curl http://localhost:5000/
curl -X POST http://localhost:5000/any-path
curl -X PUT http://localhost:5000/another-path
```

All requests will return: `{"response": "Yes"}` 
