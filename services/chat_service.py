from services.gemini_service import GeminiService
from services.zakat_service import process_consultation


def handle_chat_turn(user_message: str, session_facts: dict) -> dict:
    """
    Orchestrates the LLM -> KBES -> LLM pipeline.
    """
    # 1. LLM Extraction: Ask Gemini to update our facts based on what the user just said
    updated_facts = GeminiService.extract_facts(user_message, session_facts)

    # 2. KBES Reasoning: Feed the extracted facts into your Forward Chaining engine
    # (Using the process_consultation function we built previously)
    kbes_result = process_consultation(updated_facts)

    # 3. LLM Generation: Ask Gemini to formulate a conversational reply based on the KBES output
    bot_reply = GeminiService.generate_chat_response(user_message, kbes_result)

    # 4. Return the conversational reply and the updated state to the frontend
    return {
        "reply": bot_reply,
        "updated_facts": updated_facts,
        "kbes_trace": kbes_result['reasoning_trace']
    }