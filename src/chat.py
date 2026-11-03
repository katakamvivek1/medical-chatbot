"""
The chatbot "brain".

Day 1: a small rule-based placeholder so the whole app works end to end.
Day 3: this function will call the RAG pipeline instead. As long as it
keeps returning {"answer": str, "sources": list}, nothing else changes.
"""

DISCLAIMER = (
    "This chatbot gives general health information only. "
    "It is not medical advice - please consult a doctor."
)

# Tiny placeholder knowledge base (keyword -> short answer).
PLACEHOLDER_ANSWERS = {
    "hello": "Hi! I'm a medical information assistant. Ask me about a health topic.",
    "fever": "A fever is a temporary rise in body temperature, often caused by an infection.",
    "diabetes": "Diabetes is a condition where blood sugar (glucose) levels are too high.",
    "headache": "A headache is pain in the head or face, often caused by stress, dehydration or lack of sleep.",
}


def get_answer(message: str) -> dict:
    """Return an answer for the user's message.

    Args:
        message: the user's question (already validated by app.py).

    Returns:
        A dict with:
          - "answer":  text shown to the user
          - "sources": list of source names (empty today, filled on Day 3)
    """
    text = message.lower()

    for keyword, answer in PLACEHOLDER_ANSWERS.items():
        if keyword in text:
            return {"answer": f"{answer}\n\n{DISCLAIMER}", "sources": []}

    return {
        "answer": (
            "I don't know that yet - my real knowledge base arrives on Day 3. "
            f"Try asking about fever or diabetes.\n\n{DISCLAIMER}"
        ),
        "sources": [],
    }
