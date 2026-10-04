import unittest
import json
from unittest.mock import patch, MagicMock
from config import Config
from app import create_app
from models import db
from services.local_analyzer import analyze_locally
from services.gemini_analyzer import validate_gemini_response, is_first_sentence_copy
from services.analysis_service import analyze_feedback

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET = "test-jwt-secret-key-123456789012345"
    GEMINI_API_KEY = ""  # Tests run in local mode by default

class FeedbackIqTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(self, name, email, password):
        return self.client.post('/api/auth/register', data=json.dumps({
            'name': name,
            'email': email,
            'password': password
        }), content_type='application/json')

    def login_user(self, email, password):
        return self.client.post('/api/auth/login', data=json.dumps({
            'email': email,
            'password': password
        }), content_type='application/json')

    def test_auth_flow(self):
        reg = self.register_user("Alice", "alice@example.com", "password123")
        self.assertEqual(reg.status_code, 201)
        token = reg.get_json()["token"]

        login = self.login_user("alice@example.com", "password123")
        self.assertEqual(login.status_code, 200)

        me = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.get_json()["email"], "alice@example.com")

    # ==========================================
    # LOCAL MODE ANALYSIS TESTS (13 Scenarios)
    # ==========================================

    def test_1_clearly_positive(self):
        text = "The application is fast, reliable, and very easy to use."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Positive")
        self.assertEqual(res["category"], "Product")
        self.assertEqual(res["priority"], "Low")
        self.assertTrue(len(res["summary"].split()) >= 6)

    def test_2_clearly_negative(self):
        text = "The application crashes frequently and payments keep failing."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertIn(res["category"], ["Payment/Transaction", "Bug"])
        self.assertEqual(res["priority"], "High")

    def test_3_neutral(self):
        text = "I have been using the application for two months mainly to check my balance."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Neutral")
        self.assertEqual(res["priority"], "Low")

    def test_4_negation_without_problems(self):
        text = "I haven't experienced any problems with the payment process."
        res = analyze_locally(text)
        self.assertNotEqual(res["sentiment"], "Negative")
        self.assertIn(res["sentiment"], ["Positive", "Neutral"])
        self.assertEqual(res["category"], "Payment/Transaction")
        self.assertEqual(res["priority"], "Low")

    def test_5_mixed_feedback_complaint_outweighs(self):
        text = "The application is easy to use, but payments failed several times and I was charged incorrectly."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Payment/Transaction")
        self.assertEqual(res["priority"], "High")

    def test_6_constructive_criticism(self):
        text = "The service was useful, but communication was poor. More regular updates would improve the experience."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Support")
        self.assertIn(res["priority"], ["Medium", "Low"])
        self.assertIn("communication", res["summary"].lower())

    def test_7_positive_outcome_despite_negative_words(self):
        text = "I had an issue with my account, but support resolved it quickly and professionally."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Positive")
        self.assertEqual(res["category"], "Support")
        self.assertEqual(res["priority"], "Low")
        self.assertIn("resolved", res["summary"].lower())

    def test_8_payment_problem(self):
        text = "Money was deducted from my account but the payment failed to process."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Payment/Transaction")
        self.assertEqual(res["priority"], "High")

    def test_9_support_problem(self):
        text = "The support team took three days to respond to my urgent inquiry."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Support")
        self.assertEqual(res["priority"], "Medium")

    def test_10_security_problem(self):
        text = "Someone accessed my account from an unknown device in another city without my authorization."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Security")
        self.assertEqual(res["priority"], "High")

    def test_11_technical_problem(self):
        text = "The app crashes whenever I upload a photo to my profile."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["category"], "Bug")

    def test_12_long_paragraph(self):
        text = ("I have been an active user for over a year and generally appreciate the features provided by the platform. "
                "However, recently the mobile response time has degraded significantly, and navigation between menus has become sluggish. "
                "Additionally, several data sync attempts failed yesterday without any error message. I hope the engineering team can address these performance regressions soon.")
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertIn(res["category"], ["Product", "Bug"])
        # Ensure summary synthesizes the primary complaint rather than copying sentence 1
        self.assertFalse(res["summary"].startswith("I have been an active user"))

    def test_13_positive_containing_negative_words(self):
        text = "I was worried the transfer would fail or face delays, but it went through without any error."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Positive")
        self.assertEqual(res["category"], "Payment/Transaction")
        self.assertEqual(res["priority"], "Low")

    def test_14_negative_containing_positive_words(self):
        text = "The interface looks beautiful and clean, but the app is completely broken and crashes every time."
        res = analyze_locally(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["priority"], "High")

    # ==========================================
    # GEMINI VALIDATION & FALLBACK TESTS
    # ==========================================

    def test_gemini_validation_rejects_first_sentence_copy(self):
        orig_text = ("I was not satisfied with my experience. The checkout page threw an error and charged my card twice. "
                     "Customer support has not refunded my payment yet.")
        bad_gemini_data = {
            "sentiment": "Negative",
            "category": "Payment/Transaction",
            "priority": "High",
            "summary": "I was not satisfied with my experience."
        }
        # First-sentence copy must be rejected by validator
        validated = validate_gemini_response(bad_gemini_data, orig_text)
        self.assertIsNone(validated)

    def test_gemini_validation_accepts_good_response(self):
        orig_text = ("I was not satisfied with my experience. The checkout page threw an error and charged my card twice. "
                     "Customer support has not refunded my payment yet.")
        good_gemini_data = {
            "sentiment": "Negative",
            "category": "Payment/Transaction",
            "priority": "High",
            "summary": "Customer was charged twice due to checkout errors and has not received a refund from support."
        }
        validated = validate_gemini_response(good_gemini_data, orig_text)
        self.assertIsNotNone(validated)
        self.assertEqual(validated["sentiment"], "Negative")
        self.assertEqual(validated["category"], "Payment/Transaction")
        self.assertEqual(validated["priority"], "High")

    @patch('services.analysis_service.Config.GEMINI_API_KEY', 'fake-api-key')
    @patch('services.analysis_service.analyze_with_gemini')
    def test_analysis_service_fallback_on_gemini_error(self, mock_gemini):
        # When Gemini raises an exception or returns None, it falls back to local analyzer
        mock_gemini.side_effect = Exception("API rate limit exceeded")
        res = analyze_feedback("The application crashes frequently and payments keep failing.")
        self.assertEqual(res["mode"], "LOCAL")
        self.assertEqual(res["sentiment"], "Negative")

    @patch('services.analysis_service.Config.GEMINI_API_KEY', 'fake-api-key')
    @patch('services.analysis_service.analyze_with_gemini')
    def test_analysis_service_uses_gemini_when_valid(self, mock_gemini):
        mock_gemini.return_value = {
            "sentiment": "Positive",
            "category": "Product",
            "priority": "Low",
            "summary": "Customer praised the platform for its fast speed and clean design."
        }
        res = analyze_feedback("The app is fast and beautifully designed.")
        self.assertEqual(res["mode"], "GEMINI")
        self.assertEqual(res["sentiment"], "Positive")

if __name__ == '__main__':
    unittest.main()
