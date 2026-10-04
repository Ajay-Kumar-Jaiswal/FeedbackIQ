from models import db
from models.feedback import Feedback
from services.analysis_service import analyze_feedback

def create_feedback(user, text: str) -> dict:
    clean_text = (text or "").strip()
    if not clean_text:
        raise ValueError("Feedback text cannot be empty")

    # Step 1: Save initial feedback record to database
    feedback = Feedback(user_id=user.id, text=clean_text)
    db.session.add(feedback)
    db.session.commit()

    # Step 2: Analyze feedback (Gemini or Local fallback)
    ai_result = analyze_feedback(clean_text)

    # Step 3: Validate and update feedback with AI results
    feedback.sentiment = ai_result.get("sentiment", "Neutral")
    feedback.category = ai_result.get("category", "Other")
    feedback.priority = ai_result.get("priority", "Medium")
    feedback.summary = ai_result.get("summary", "")
    db.session.commit()

    # Step 4: Return result to client (including mode metadata)
    res = feedback.to_dict()
    res["mode"] = ai_result.get("mode", "LOCAL")
    return res

def get_feedbacks(user, category=None, sentiment=None, priority=None, search=None) -> list:
    query = Feedback.query.filter_by(user_id=user.id)

    if category and category.strip():
        query = query.filter(Feedback.category == category.strip())
    if sentiment and sentiment.strip():
        query = query.filter(Feedback.sentiment == sentiment.strip())
    if priority and priority.strip():
        query = query.filter(Feedback.priority == priority.strip())
    if search and search.strip():
        query = query.filter(Feedback.text.ilike(f"%{search.strip()}%"))

    query = query.order_by(Feedback.created_at.desc())
    return [item.to_dict() for item in query.all()]

def get_feedback_by_id(user, feedback_id: int):
    feedback = Feedback.query.filter_by(id=feedback_id, user_id=user.id).first()
    return feedback.to_dict() if feedback else None

def delete_feedback(user, feedback_id: int) -> bool:
    feedback = Feedback.query.filter_by(id=feedback_id, user_id=user.id).first()
    if not feedback:
        return False
    db.session.delete(feedback)
    db.session.commit()
    return True
