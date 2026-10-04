import logging
from config import Config
from services.gemini_analyzer import analyze_with_gemini
from services.local_analyzer import analyze_locally

logger = logging.getLogger(__name__)

def analyze_feedback(text: str) -> dict:
    """
    Unified feedback intelligence analyzer.
    - Uses Gemini API (MODE 1) when GEMINI_API_KEY is configured and valid.
    - Automatically falls back to high-fidelity LocalAnalyzer (MODE 2) if Gemini is unavailable,
      times out, or returns invalid schema/empty results.
    """
    clean_text = (text or "").strip()
    if not clean_text:
        return {
            "sentiment": "Neutral",
            "category": "Other",
            "priority": "Low",
            "summary": "No feedback content provided.",
            "mode": "LOCAL"
        }

    # MODE 1: Gemini API primary analysis
    if Config.GEMINI_API_KEY:
        try:
            gemini_result = analyze_with_gemini(clean_text)
            if gemini_result:
                gemini_result["mode"] = "GEMINI"
                return gemini_result
            logger.info("Gemini analysis was unviable or failed validation. Falling back to Local Analyzer.")
        except Exception as ex:
            logger.warning("Gemini execution failed (%s). Falling back to Local Analyzer.", str(ex))

    # MODE 2: Layered Local Semantic Analysis
    local_result = analyze_locally(clean_text)
    local_result["mode"] = "LOCAL"
    return local_result
