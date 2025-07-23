# Little_Angels
Little Angels Backend Application with Form Integration

## Overview

This application includes:
1. A comprehensive signup form (`index.html`) for capturing user registration data
2. A Flask backend (`app.py`) that processes form submissions and logs all data
3. Real-time form validation and user feedback

## Features

### Frontend (index.html)
- **Personal Information**: Name, gender, age, phone numbers
- **Package Selection**: Various photography packages with pricing
- **Interests**: Multiple checkbox options (video, cards, etc.)
- **Payment Calculation**: Automatic calculation of totals and remaining amounts
- **Real-time Validation**: Phone number validation and form feedback
- **AJAX Submission**: Sends data to backend without page reload

### Backend (app.py)
- **Form Processing**: Handles POST requests to `/submit` endpoint
- **Comprehensive Logging**: Logs all form data to both console and `form_submissions.log` file
- **Error Handling**: Proper error responses and logging
- **CORS Enabled**: Allows frontend-backend communication
- **Fallback Routes**: Still responds with 'Yes' to other requests

## Setup and Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Flask backend:
   ```bash
   python app.py
   ```

3. Open `index.html` in your web browser (or serve it via a local server)

The backend will start on `http://localhost:5000`

## How to Test the Integration

1. **Start the backend**: Run `python app.py`
2. **Open the form**: Open `index.html` in your browser
3. **Fill out the form**: Enter all required information
4. **Submit**: Click the Submit button
5. **Check logs**: 
   - View real-time logs in your terminal
   - Check `form_submissions.log` file for persistent logs
   - See success/error messages on the form

## API Endpoints

- `POST /submit` - Handles form submissions and logs data
- `GET|POST|PUT|DELETE|PATCH /` - Returns `{"response": "Yes"}`
- `GET|POST|PUT|DELETE|PATCH /<any-path>` - Returns `{"response": "Yes"}`

## Logging

All form submissions are logged with:
- Timestamp
- Personal information (name, gender, age, phones)
- Package selection and choices
- Selected interests
- Payment details (total, initial, remaining)
- Complete raw form data for debugging

Logs are saved to both:
- Console output (real-time)
- `form_submissions.log` file (persistent)

## Next Steps

The backend is now ready for you to implement custom business logic:
- Database integration for storing form data
- Email notifications
- Payment processing
- Custom validation rules
- Data processing workflows

## File Structure
```
Little_Angels/
├── app.py              # Flask backend with form handling
├── index.html          # Registration form with AJAX integration
├── style.css           # Form styling
├── script.js           # Additional JavaScript (minimal)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── form_submissions.log # Auto-generated log file
``` 
