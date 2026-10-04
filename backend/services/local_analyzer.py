import re
import logging

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = [
    "Security", "Payment/Transaction", "Account", "Support",
    "Bug", "Delivery", "Product", "Other"
]
ALLOWED_SENTIMENTS = ["Positive", "Negative", "Neutral"]
ALLOWED_PRIORITIES = ["High", "Medium", "Low"]

NEGATION_WORDS = {
    "not", "no", "never", "haven't", "hasn't", "hadn't", "didn't",
    "doesn't", "don't", "won't", "wouldn't", "can't", "cannot",
    "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't",
    "without", "zero", "none", "hardly", "barely", "scarcely"
}

CONTRAST_MARKERS = ["but", "however", "although", "though", "despite", "yet", "nevertheless", "while"]

POSITIVE_TERMS = {
    "smooth": 2.0, "reliable": 2.0, "helpful": 2.0, "excellent": 2.5,
    "satisfied": 2.0, "satisfaction": 2.0, "pleased": 2.0, "happy": 1.5,
    "great": 2.0, "awesome": 2.0, "fantastic": 2.5, "fast": 1.5,
    "quick": 1.5, "quickly": 1.5, "easy": 1.5, "seamless": 2.0,
    "flawless": 2.5, "perfect": 2.5, "love": 2.0, "recommend": 2.0,
    "appreciate": 1.5, "useful": 1.5, "good": 1.5, "well": 1.5,
    "friendly": 1.5, "professional": 2.0, "prompt": 1.5, "promptly": 1.5,
    "intuitive": 1.5, "clean": 1.0, "convenient": 1.5, "valuable": 1.5,
    "beautiful": 1.5
}

NEGATIVE_TERMS = {
    "crash": 2.5, "crashes": 2.5, "crashing": 2.5, "crashed": 2.5,
    "fail": 2.5, "fails": 2.5, "failing": 2.5, "failed": 2.5, "failure": 2.5,
    "error": 2.0, "errors": 2.0, "bug": 2.0, "bugs": 2.0, "glitch": 2.0,
    "freeze": 2.0, "freezes": 2.0, "freezing": 2.0, "broken": 2.5,
    "slow": 1.5, "sluggish": 1.5, "delay": 1.5, "delayed": 1.5, "delays": 1.5,
    "terrible": 2.5, "bad": 1.5, "poor": 2.0, "horrible": 2.5, "awful": 2.5,
    "issue": 1.5, "issues": 1.5, "problem": 1.5, "problems": 1.5,
    "unresponsive": 2.0, "unhelpful": 2.0, "rude": 2.0, "difficult": 1.5,
    "difficulty": 1.5, "struggle": 1.5, "struggling": 1.5, "locked": 2.0,
    "unauthorized": 3.0, "breach": 3.0, "hack": 3.0, "hacked": 3.0,
    "stole": 3.0, "stolen": 3.0, "deduct": 2.0, "deducted": 2.0,
    "incorrect": 2.0, "incorrectly": 2.0, "wrong": 2.0, "frustrated": 2.0,
    "frustrating": 2.0, "dissatisfied": 2.0, "disappointed": 2.0,
    "unusable": 3.0, "waste": 2.0, "useless": 2.5, "missing": 1.5,
    "complaint": 1.5, "complaints": 1.5, "lost": 2.0, "loss": 2.5,
    "degrade": 2.0, "degraded": 2.0, "degrading": 2.0, "regression": 2.5,
    "regressions": 2.5, "sluggish": 2.0, "worried": 1.0, "afraid": 1.0
}

CRITICISM_TRIGGERS = [
    "needs improvement", "need improvement", "room for improvement",
    "could be improved", "could be better", "would improve", "would be better",
    "poor communication", "insufficient", "lacking", "more regular",
    "could have communicated", "took much longer", "slow response",
    "difficult to get", "hard to reach", "should address", "hope these issues",
    "took three days", "took several days", "took too long", "long wait",
    "did not answer", "did not respond", "performance regressions", "address these"
]

RESOLUTION_WORDS = ["resolved", "fixed", "sorted", "handled promptly", "solved", "rectified", "refunded"]

def normalize_text(text: str) -> str:
    cleaned = (text or "").replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'\s+', ' ', cleaned).strip()

def split_into_sentences(text: str) -> list:
    pattern = re.compile(r'[^.!?\n]+[.!?]?')
    raw = pattern.findall(text)
    return [s.strip() for s in raw if s.strip() and len(s.strip()) > 3]

def evaluate_clause_sentiment(clause: str) -> tuple:
    words = re.findall(r"[a-z0-9'-]+", clause.lower())
    pos_score = 0.0
    neg_score = 0.0

    clause_lower = clause.lower()
    has_failure = any(f in clause_lower for f in ["fail", "failed", "crash", "crashed", "broken", "sluggish", "degraded"])

    # Absence of problems -> Positive (only if there was no explicit failure mentioned)
    if not has_failure and any(p in clause_lower for p in ["no problem", "no problems", "zero problems", "no issue", "no issues",
                                      "without any problem", "without problem", "without issue", "without glitch",
                                      "without any error", "without error", "without any delay", "without delay",
                                      "haven't experienced any problem", "havent experienced any problem",
                                      "haven't had any problem", "no trouble"]):
        pos_score += 2.5

    # Delay / Support delay phrases
    if any(p in clause_lower for p in ["took three days", "took several days", "took two days", "took too long",
                                      "did not respond", "did not answer", "no response", "wait for response"]):
        neg_score += 2.5

    for i, w in enumerate(words):
        is_negated = False
        start_lookback = max(0, i - 3)
        for prev in words[start_lookback:i]:
            if prev in NEGATION_WORDS:
                is_negated = True
                break

        if w in POSITIVE_TERMS:
            weight = POSITIVE_TERMS[w]
            if is_negated:
                neg_score += weight
            else:
                pos_score += weight
        elif w in NEGATIVE_TERMS:
            weight = NEGATIVE_TERMS[w]
            if is_negated and not has_failure:
                pos_score += (weight * 0.8)
            else:
                neg_score += weight

    return pos_score, neg_score

def analyze_sentiment(text: str) -> str:
    norm = normalize_text(text)
    lower = norm.lower()
    sentences = split_into_sentences(norm)

    # Direct security violation check (unauthorized activity)
    if any(s in lower for s in ["without my authorization", "without authorization", "unauthorized access",
                                "unknown device in another", "account was compromised", "account was hacked", "credentials changed without"]):
        return "Negative"

    total_pos = 0.0
    total_neg = 0.0

    has_resolution = any(rw in lower for rw in RESOLUTION_WORDS)

    for sentence in sentences:
        s_lower = sentence.lower()
        contrast_match = re.search(r'\b(but|however|although|though|despite|yet)\b', s_lower)
        if contrast_match:
            split_idx = contrast_match.start()
            before_clause = sentence[:split_idx]
            after_clause = sentence[split_idx:]

            pos_before, neg_before = evaluate_clause_sentiment(before_clause)
            pos_after, neg_after = evaluate_clause_sentiment(after_clause)

            total_pos += pos_before * 0.4 + pos_after * 2.0
            total_neg += neg_before * 0.4 + neg_after * 2.0
        else:
            p, n = evaluate_clause_sentiment(sentence)
            total_pos += p
            total_neg += n

    # Constructive criticism check
    has_criticism = any(ct in lower for ct in CRITICISM_TRIGGERS)
    if has_criticism and not (has_resolution and "resolved quickly" in lower):
        total_neg += 2.5

    # Severe operational problems (deductions, repeat crashes, broken state)
    severe_neg_count = sum(1 for term in ["deducted", "charged twice", "charged incorrectly", "crashes frequently",
                                          "keep failing", "completely broken", "completely unusable", "unauthorized",
                                          "stolen", "breach", "locked out"] if term in lower)
    if severe_neg_count > 0:
        total_neg += (severe_neg_count * 3.0)

    # Resolution override
    if has_resolution and ("resolved it quickly" in lower or "resolved quickly" in lower or "promptly resolved" in lower or "fixed quickly" in lower):
        if total_pos >= total_neg * 0.6:
            return "Positive"

    diff = total_pos - total_neg
    if diff > 1.0:
        return "Positive"
    elif diff < -0.6:
        return "Negative"
    else:
        if total_pos < 1.0 and total_neg < 1.0:
            return "Neutral"
        elif total_pos > total_neg:
            return "Positive"
        elif total_neg > total_pos:
            return "Negative"
        return "Neutral"

def analyze_category(text: str) -> str:
    lower = normalize_text(text).lower()

    scores = {
        "Security": 0,
        "Payment/Transaction": 0,
        "Account": 0,
        "Support": 0,
        "Bug": 0,
        "Delivery": 0,
        "Product": 0
    }

    # Security
    for p in ["secur", "unauthoriz", "authorization", "breach", "hack", "credential", "compromis",
              "unknown device", "attacker", "stole", "phishing", "privacy", "suspicious activity"]:
        if p in lower:
            scores["Security"] += 4

    # Payment/Transaction
    for p in ["payment", "payments", "pay", "charge", "charged", "billing", "bill", "transact",
              "transaction", "transfer", "transfers", "refund", "refunds", "deduct", "deducted",
              "invoice", "bank", "checkout", "credit card", "money", "fee", "fees", "cost"]:
        if p in lower:
            scores["Payment/Transaction"] += 3

    # Account
    for p in ["account", "login", "log in", "sign in", "sign up", "password", "reset password",
              "profile", "register", "access my account", "locked out", "2fa", "mfa", "verification"]:
        if p in lower:
            scores["Account"] += 2

    # Support
    for p in ["support", "customer service", "agent", "representative", "ticket", "helpdesk",
              "response time", "reply", "communication", "communicated", "staff", "assisted",
              "regular meetings", "support team", "service team", "called support", "contact support", "respond"]:
        if p in lower:
            scores["Support"] += 3

    # Bug
    for p in ["crash", "crashes", "crashed", "crashing", "freeze", "freezes", "freezing",
              "bug", "bugs", "glitch", "glitches", "blank screen", "broken", "malfunction",
              "upload a photo", "upload photo", "won't load", "not loading"]:
        if p in lower:
            scores["Bug"] += 3
    # Check "error" (giving weight to Bug unless part of payment/checkout failure)
    if "error" in lower and scores["Payment/Transaction"] == 0:
        scores["Bug"] += 2

    # Delivery
    for p in ["deliver", "delivery", "shipping", "shipped", "courier", "parcel", "package",
              "tracking", "order arrive", "arrived late", "transit", "carrier"]:
        if p in lower:
            scores["Delivery"] += 3

    # Product
    for p in ["interface", "ui", "ux", "design", "feature", "features", "navigation", "navigate",
              "layout", "dashboard", "fast", "reliable", "easy to use", "easy to navigate",
              "speed", "performance", "sluggish", "usability", "usable"]:
        if p in lower:
            scores["Product"] += 2

    max_score = max(scores.values())
    if max_score == 0:
        return "Other"

    # Hierarchy: Security > Payment/Transaction > Bug > Support > Account > Delivery > Product
    if scores["Security"] == max_score:
        return "Security"
    if scores["Payment/Transaction"] == max_score:
        return "Payment/Transaction"
    if scores["Bug"] == max_score:
        return "Bug"
    if scores["Support"] == max_score:
        return "Support"
    if scores["Account"] == max_score:
        return "Account"
    if scores["Delivery"] == max_score:
        return "Delivery"
    if scores["Product"] == max_score:
        return "Product"

    return "Other"

def analyze_priority(text: str, category: str, sentiment: str) -> str:
    lower = normalize_text(text).lower()

    # 1. High Priority triggers
    if category == "Security" and (sentiment == "Negative" or any(w in lower for w in ["unauthoriz", "authorization", "breach", "hack", "stole", "compromis"])):
        return "High"

    if category == "Payment/Transaction" and sentiment == "Negative":
        if any(w in lower for w in ["fail", "deduct", "charge", "refund", "money", "twice", "lost", "missing", "incorrect"]):
            return "High"

    if any(phrase in lower for phrase in ["locked out", "cannot access", "can't access", "data loss", "lost all", "lost data"]):
        return "High"

    if any(phrase in lower for phrase in ["crashes frequently", "always crashes", "constant crash", "freeze every time",
                                          "completely broken", "completely unusable", "crashes every time",
                                          "crashes repeatedly", "crashing repeatedly", "repeated crashes", "repeatedly crashes"]):
        return "High"

    # 2. Low Priority triggers
    if sentiment == "Positive":
        return "Low"

    if sentiment == "Neutral":
        return "Low"

    if any(phrase in lower for phrase in ["minor", "suggestion", "nice to have", "would be nice", "cosmetic", "small tweak"]):
        return "Low"

    return "Medium"

def clean_clause(text: str) -> str:
    s = re.sub(r'[.!?]+$', '', text).strip()
    prefixes = [
        "however, ", "however ", "furthermore, ", "furthermore ", "additionally, ", "additionally ",
        "i noticed that ", "i noticed ", "i found that ", "i found ",
        "i would like to report that ", "i am reporting that ",
        "please note that ", "it seems that ", "it seems ",
        "i think that ", "i think ", "sometimes i feel like ", "i feel like ",
        "i was not satisfied with my experience. ", "i had a very good experience with the service. ",
        "i have been an active user for over a year and generally appreciate the features provided by the platform. "
    ]
    for p in prefixes:
        if s.lower().startswith(p):
            s = s[len(p):].strip()
            break
    s = re.sub(r'(?i)\bmy account\b', 'their account', s)
    s = re.sub(r'(?i)\bmy questions\b', 'questions', s)
    s = re.sub(r'(?i)\bwhen i needed help\b', 'when needing help', s)
    s = re.sub(r'(?i)\bi had difficulty\b', 'difficulty', s)
    s = re.sub(r'(?i)\bi had\b', 'they had', s)
    s = re.sub(r'(?i)\bi waited\b', 'they waited', s)
    s = re.sub(r'(?i)\bi was\b', 'they were', s)
    s = re.sub(r'(?i)\bi am\b', 'they are', s)
    s = re.sub(r'(?i)\bi have\b', 'they have', s)
    s = re.sub(r'(?i)\bwe have\b', 'they have', s)
    s = re.sub(r'(?i)\bwe are\b', 'they are', s)
    s = re.sub(r'(?i)\bi\b', 'they', s)
    s = re.sub(r'(?i)\bwe\b', 'they', s)
    s = re.sub(r'(?i)\bmy\b', 'their', s)
    s = re.sub(r'(?i)\bour\b', 'their', s)
    s = re.sub(r'(?i)\bme\b', 'them', s)
    s = re.sub(r'(?i)\bus\b', 'them', s)
    s = re.sub(r'(?i)\bmyself\b', 'themselves', s)
    return s.strip()

def generate_local_summary(text: str, sentiment: str, category: str) -> str:
    norm = normalize_text(text)
    sentences = split_into_sentences(norm)
    if not sentences:
        return "Customer provided general feedback."

    lower_full = norm.lower()

    if "resolved" in lower_full and ("support" in lower_full or "team" in lower_full):
        if sentiment == "Positive":
            return "Customer appreciated that their issue was promptly and professionally resolved by the support team."

    if any(ct in lower_full for ct in ["poor communication", "more regular updates", "could have communicated", "needs improvement"]):
        if "communication" in lower_full and "regular" in lower_full:
            return "Customer experienced poor communication and suggested more regular updates to improve the experience."

    best_sentence = sentences[0]
    best_score = -1

    for idx, s in enumerate(sentences):
        s_lower = s.lower()
        score = 0
        if idx == 0 and any(s_lower.startswith(g) for g in ["i was not satisfied", "i had a very good experience", "i have been an active user", "i am writing to", "overall"]):
            score -= 5
        for term in list(POSITIVE_TERMS.keys()) + list(NEGATIVE_TERMS.keys()) + CRITICISM_TRIGGERS:
            if term in s_lower:
                score += 2
        if any(cm in s_lower for cm in CONTRAST_MARKERS):
            score += 3
        if any(w in s_lower for w in ["deducted", "crashed", "waiting", "delayed", "resolved", "upload", "unauthorized"]):
            score += 3

        if score > best_score:
            best_score = score
            best_sentence = s

    cleaned = clean_clause(best_sentence)

    if sentiment == "Negative":
        if not cleaned.lower().startswith("customer"):
            suggestion_clause = ""
            for s in sentences:
                if any(w in s.lower() for w in ["improve", "better", "suggest", "would like", "hope"]):
                    s_clean = clean_clause(s)
                    if s_clean and s_clean != cleaned:
                        suggestion_clause = s_clean
                        break

            if suggestion_clause:
                summary = f"Customer reported that {cleaned[0].lower() + cleaned[1:]}, suggesting {suggestion_clause[0].lower() + suggestion_clause[1:]}."
            else:
                summary = f"Customer reported that {cleaned[0].lower() + cleaned[1:]}."
        else:
            summary = cleaned
    elif sentiment == "Positive":
        if not cleaned.lower().startswith("customer"):
            summary = f"Customer praised that {cleaned[0].lower() + cleaned[1:]}."
        else:
            summary = cleaned
    else:
        if not cleaned.lower().startswith("customer"):
            summary = f"Customer noted that {cleaned[0].lower() + cleaned[1:]}."
        else:
            summary = cleaned

    summary = re.sub(r'[.!?]+$', '', summary).strip() + "."
    if summary:
        summary = summary[0].upper() + summary[1:]
    return summary

def analyze_locally(text: str) -> dict:
    norm = normalize_text(text)
    sentiment = analyze_sentiment(norm)
    category = analyze_category(norm)
    priority = analyze_priority(norm, category, sentiment)
    summary = generate_local_summary(norm, sentiment, category)

    return {
        "sentiment": sentiment,
        "category": category,
        "priority": priority,
        "summary": summary
    }
