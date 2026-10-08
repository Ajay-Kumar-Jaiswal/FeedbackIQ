# FeedbackIQ — AI Customer Feedback Analyzer

FeedbackIQ is an AI-powered customer feedback analysis application that analyzes
customer feedback and returns structured insights such as sentiment, category,
priority, and summary.

The application combines a Flask backend, React frontend, MySQL database,
JWT authentication, and Gemini API integration.

## ✨ Features

- AI-powered sentiment analysis
- Feedback category classification
- Priority detection
- Automatic feedback summarization
- JWT-based authentication
- Secure password handling
- Structured validation of AI-generated responses
- Fallback handling when AI responses are invalid or unavailable
- React-based user interface
- MySQL persistence for feedback and analysis results

## 🤖 AI Processing

FeedbackIQ uses Gemini to analyze customer feedback and generate structured
responses.

The application validates AI responses before storing or returning them.

Validation includes:

- Allowed sentiment and category labels
- Priority validation
- Summary validation
- Handling invalid or unexpected AI responses
- Fallback analysis when Gemini processing fails

This prevents invalid AI-generated data from directly reaching the application.

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- REST APIs
- JWT Authentication
- Bcrypt

### Frontend
- React
- JavaScript
- HTML
- CSS

### AI
- Gemini API
- Prompt Design
- LLM Response Validation

### Database & Testing
- MySQL
- Pytest
- Mocked AI responses

## 🏗️ Architecture

```text
React Frontend
      │
      ▼
Flask REST API
      │
      ├── Authentication & Authorization
      │
      ├── Feedback Processing
      │
      ├── Gemini AI Integration
      │
      └── Response Validation & Fallback
      │
      ▼
MySQL Database

## 🔒 Authentication & Security

FeedbackIQ uses JWT-based authentication to protect API endpoints.

Security features include:

- JWT authentication
- Bcrypt password hashing
- Protected API routes
- Input validation
- Validation of AI-generated responses

---

## 🚀 Setup & Usage

### Prerequisites

- Python 3.10+
- Node.js and npm
- MySQL
- Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/feedbackiq.git
cd feedbackiq
```

### 2. Configure Backend

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure your environment variables:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/feedbackiq
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key
```

> **Note:** Do not commit `.env` or API keys to GitHub.

### 3. Create the Database

Open MySQL and run:

```sql
CREATE DATABASE feedbackiq;
```

### 4. Start the Backend

```bash
python app.py
```

The backend runs at:

```text
http://localhost:5000
```

### 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm start
```

The frontend runs at:

```text
http://localhost:3000
```

---

## 🧪 Testing

Run the backend test suite using:

```bash
pytest -v
```

Tests cover areas including:

- Authentication
- AI response validation
- Gemini failure handling
- Sentiment analysis
- Mixed-sentiment feedback
- Negation cases
- Security-related validation

AI API calls can be mocked during testing to verify application behavior
without depending on live Gemini responses.

---

## 📌 Future Improvements

- Feedback analytics dashboard
- Batch feedback processing
- Export analyzed feedback
- Historical sentiment trends
- Additional AI providers
- Improved feedback categorization

---

## 📄 License

This project is licensed under the MIT License.
