# Little_Angels
Little Angels Backend Application with Form Integration & MongoDB Atlas

## Overview

This application includes:
1. A comprehensive signup form (`index.html`) for capturing user registration data
2. A Flask backend (`app.py`) that processes form submissions and stores data in MongoDB Atlas
3. Real-time form validation and user feedback
4. **NEW:** MongoDB Atlas integration for persistent data storage

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
- **MongoDB Integration**: Saves all form data to MongoDB Atlas cloud database
- **Comprehensive Logging**: Logs all form data to both console and `form_submissions.log` file
- **Error Handling**: Proper error responses and logging with database status
- **Health Monitoring**: Check application and database status
- **Data Retrieval**: API endpoint to view recent submissions
- **CORS Enabled**: Allows frontend-backend communication
- **Fallback Routes**: Still responds with 'Yes' to other requests

## Database Structure

Form submissions are stored in MongoDB Atlas with the following structure:
```json
{
  "user_name": "John Doe",
  "gender": "male",
  "age_years": "25",
  "age_months": "6",
  "main_phone": "912345678",
  "alt_phone": "987654321",
  "package": "diamond",
  "user_choice": "option1",
  "interests": ["video", "thank_you_card"],
  "total": "39000",
  "initial": "15000",
  "remaining": "24000",
  "submitted_at": "2024-01-15T14:30:25.123Z",
  "submission_id": "1705326625123"
}
```

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

The backend will start on `http://localhost:5000` and automatically connect to MongoDB Atlas.

## How to Test the Integration

1. **Start the backend**: Run `python app.py`
2. **Check MongoDB connection**: Visit `http://localhost:5000/health`
3. **Open the form**: Open `index.html` in your browser
4. **Fill out the form**: Enter all required information
5. **Submit**: Click the Submit button
6. **Verify storage**: Check logs and visit `http://localhost:5000/submissions` to see stored data

## API Endpoints

- `POST /submit` - Handles form submissions, saves to MongoDB and logs data
- `GET /health` - Health check with MongoDB connection status
- `GET /submissions` - Returns recent form submissions (last 10)
- `GET|POST|PUT|DELETE|PATCH /` - Returns `{"response": "Yes"}`
- `GET|POST|PUT|DELETE|PATCH /<any-path>` - Returns `{"response": "Yes"}`

### Example API Responses

**Health Check:**
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "timestamp": "2024-01-15T14:30:25.123Z"
}
```

**Form Submission Success:**
```json
{
  "response": "Yes",
  "message": "Form data received and logged successfully",
  "timestamp": "2024-01-15 14:30:25",
  "data_received": 10,
  "mongodb_saved": true
}
```

## MongoDB Atlas Configuration

The application connects to MongoDB Atlas using:
- **Database**: `little_angels_db`
- **Collection**: `form_submissions`
- **Connection**: Automatic retry and connection pooling
- **Security**: Environment variable for production deployment

## Logging

All form submissions are logged with:
- Timestamp and submission ID
- Personal information (name, gender, age, phones)
- Package selection and choices
- Selected interests
- Payment details (total, initial, remaining)
- **NEW:** MongoDB save status (SUCCESS/FAILED)
- Complete raw form data for debugging

Logs are saved to both:
- Console output (real-time)
- `form_submissions.log` file (persistent)

## Production Deployment

### Environment Variables
For production deployment, set:
- `MONGO_URI`: Your MongoDB Atlas connection string
- `FLASK_ENV`: `production`
- `LOG_LEVEL`: `INFO`

### Render Deployment
The `render.yaml` file includes MongoDB configuration. For manual deployment:
1. Add `MONGO_URI` environment variable in Render dashboard
2. Deploy normally - MongoDB connection is automatic

## Data Management

### Backup Considerations
- MongoDB Atlas provides automatic backups
- Form data includes timestamp for chronological sorting
- Unique submission IDs for tracking

### Scaling
- MongoDB Atlas handles scaling automatically
- Connection pooling handles multiple concurrent requests
- Consider indexing on `submitted_at` for large datasets

## Next Steps

The backend is now ready for advanced business logic:
- **✅ Database storage** - Form data persisted in MongoDB Atlas
- Email notifications using stored data
- Payment processing integration
- Customer management dashboard
- Analytics and reporting
- Data export functionality

## File Structure
```
Little_Angels/
├── app.py                    # Flask backend with MongoDB integration
├── index.html                # Development version of registration form
├── index-production.html     # Production version with correct backend URL
├── style.css                 # Form styling
├── script.js                 # Additional JavaScript (minimal)
├── requirements.txt          # Python dependencies (includes pymongo)
├── render.yaml              # Render deployment config with MongoDB
├── DEPLOYMENT.md            # Deployment guide
├── README.md                # This file
└── form_submissions.log     # Auto-generated log file
```

## Troubleshooting

### MongoDB Issues
- **Connection errors**: Check MongoDB Atlas network access and credentials
- **Write errors**: Verify database permissions and connection string
- **Timeout issues**: Check network connectivity and Atlas cluster status

### Application Issues
- Visit `/health` endpoint to check overall system status
- MongoDB connection status is displayed in health check
- Check logs for detailed error information

## Testing Commands

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test form submission (with sample data)
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"user_name":"Test User","gender":"male","age_years":"25","main_phone":"912345678","package":"diamond","total":"39000"}'

# Check recent submissions
curl http://localhost:5000/submissions
```

Your Little Angels application is now a complete, production-ready system with persistent data storage! 🎉📊 
