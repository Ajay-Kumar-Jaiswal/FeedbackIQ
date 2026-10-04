import json
import logging
import re
from config import Config

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = {
    "Security", "Payment/Transaction", "Account", "Support",
    "Bug", "Delivery", "Product", "Other"
}
ALLOWED_SENTIMENTS = {"Positive", "Negative", "Neutral"}
ALLOWED_PRIORITIES = {"High", "Medium", "Low"}

GEMINI_ANALYSIS_PROMPT = """You are an expert customer feedback intelligence analyst.
Analyze the complete customer feedback and return ONLY a valid, structured JSON object matching this exact schema:
{{
  "sentiment": "Positive" | "Negative" | "Neutral",
  "category": "Security" | "Payment/Transaction" | "Account" | "Support" | "Bug" | "Delivery" | "Product" | "Other",
  "priority": "High" | "Medium" | "Low",
  "summary": "concise 1-sentence analytical summary"
}}

Classification Guidelines:
1. SENTIMENT (Evaluate the overall meaning, NOT isolated words):
- Positive: Genuine praise, satisfaction, appreciation, smooth operation, or problems that were successfully resolved.
  * Absence of issues (e.g., 'haven't experienced any problems', 'zero issues') MUST be classified as Positive.
  * Issue resolved well (e.g., 'had an issue, but support resolved it quickly') MUST be classified as Positive.
- Negative: Complaints, failures, frustration, poor service, unresolved issues, or constructive criticism.
  * Mixed feedback where a serious bug, payment failure, or poor communication is noted (e.g., 'app is easy to use, but payments failed') MUST be classified as Negative because the problem outweighs the praise.
  * Constructive criticism (e.g., 'service was useful, but communication was poor') MUST be classified as Negative.
- Neutral: Purely factual/informational statements with no clear positive satisfaction or negative grievance.

2. CATEGORY (Select the PRIMARY subject of the feedback):
- Security: Unauthorized access, credential compromise, suspicious logins, data privacy issues.
- Payment/Transaction: Billing, deductions, charges, refunds, pricing errors, checkout failures.
- Account: Profile setup, password reset, login credentials, authentication, locked out of account.
- Support: Customer service quality, helpdesk interactions, communication, response times, staff.
- Bug: Software errors, crashes, freezes, visual glitches, upload failures, broken features.
- Delivery: Physical shipping, couriers, package tracking, delivery delays.
- Product: Usability, navigation, layout, interface, design, speed, performance, feature requests.
- Other: General feedback that does not fit any of the above categories. Never default unrelated feedback to Payment/Transaction.

3. PRIORITY (Based on impact and urgency):
- High: Financial loss, unauthorized access, security incidents, inability to access account, repeated functional crashes.
- Medium: Support delays, delivery delays, ordinary bugs, noticeable usability friction, communication issues.
- Low: General praise/compliments, minor suggestions, cosmetic items, non-urgent comments.

4. SUMMARY (Synthesize the COMPLETE feedback):
- Formulate a single, objective, analytical sentence (approximately 15–30 words) summarizing the primary experience/problem/praise along with key supporting details and any suggested improvements.
- CRITICAL: Do NOT merely copy, quote, or rephrase only the first sentence or opening thesis statement. You MUST synthesize the underlying concrete facts and causes from the entire feedback.
- Format as exactly 1 complete sentence ending with a period.

Customer Feedback:
"{feedback_text}"
"""

def extract_json_payload(raw_text: str) -> str:
    cleaned = (raw_text or "").strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx > start_idx:
        return cleaned[start_idx:end_idx + 1]
    return cleaned

def is_first_sentence_copy(summary: str, original_text: str) -> bool:
    orig_clean = original_text.strip()
    sentences = [s.strip() for s in re.findall(r'[^.!?\n]+[.!?]?', orig_clean) if s.strip()]
    if len(sentences) <= 1:
        return False

    first_s = re.sub(r'[.!?]+$', '', sentences[0]).strip().lower()
    sum_s = re.sub(r'[.!?]+$', '', summary).strip().lower()

    if sum_s == first_s:
        return True

    # Generic opening thesis sentences
    generic_openers = [
        "i was not satisfied", "i am not satisfied", "i had a very good experience",
        "i had a good experience", "i had a bad experience", "overall my experience"
    ]
    return any(sum_s.startswith(g) for g in generic_openers)

def validate_gemini_response(data: dict, original_text: str) -> dict:
    if not isinstance(data, dict):
        return None

    raw_sentiment = str(data.get("sentiment", "")).strip().capitalize()
    raw_category = str(data.get("category", "")).strip()
    raw_priority = str(data.get("priority", "")).strip().capitalize()
    raw_summary = str(data.get("summary", "")).strip()

    # Validate sentiment
    if raw_sentiment not in ALLOWED_SENTIMENTS:
        return None

    # Validate category (case-insensitive normalization)
    matched_category = None
    for cat in ALLOWED_CATEGORIES:
        if cat.lower() == raw_category.lower():
            matched_category = cat
            break
    if not matched_category:
        return None

    # Validate priority
    if raw_priority not in ALLOWED_PRIORITIES:
        return None

    # Validate summary: must be non-empty, single sentence, and not merely copying the first sentence
    if not raw_summary or len(raw_summary) < 10:
        return None

    if is_first_sentence_copy(raw_summary, original_text):
        return None

    # Ensure period at end
    if not raw_summary.endswith((".", "!", "?")):
        raw_summary += "."

    return {
        "sentiment": raw_sentiment,
        "category": matched_category,
        "priority": raw_priority,
        "summary": raw_summary
    }

def analyze_with_gemini(text: str) -> dict:
    """Primary analyzer using the official Google Gemini SDK."""
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = GEMINI_ANALYSIS_PROMPT.format(feedback_text=text)

        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=config
        )

        raw_text = None
        if hasattr(response, "text") and response.text:
            raw_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]
            raw_text = "".join(text_parts)

        if not raw_text:
            logger.warning("Gemini returned empty content.")
            return None

        json_str = extract_json_payload(raw_text)
        data = json.loads(json_str)
        validated = validate_gemini_response(data, text)
        if not validated:
            logger.warning("Gemini response failed structural/semantic validation.")
            return None

        return validated
    except Exception as ex:
        # Never log API key or secret data
        logger.warning("Gemini API call or parsing failed: %s", str(ex))
        return None
