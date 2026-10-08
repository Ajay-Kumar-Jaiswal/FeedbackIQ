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
