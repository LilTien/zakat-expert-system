import os
import json
from google import genai
from google.genai import types


class GeminiService:
    """Handles communication with the Gemini API using the new google-genai SDK."""

    @staticmethod
    def get_client():
        """Initialize the client dynamically to ensure environment variables are loaded."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment.")
        return genai.Client(api_key=api_key)

    @staticmethod
    def extract_facts(user_message: str, current_facts: dict) -> dict:
        """Analyzes the chat and extracts Zakat facts into a JSON object."""
        client = GeminiService.get_client()

        prompt = f"""
        You are a data extraction assistant for a Zakat Selangor Expert System.
        Extract any relevant facts from the user's message
        Current known facts: {json.dumps(current_facts)}
        User's latest message: "{user_message}
        Extract using ONLY these exact JSON keys if mentioned:
        - 'muslim' (boolean)
        - 'zakatType' ("pendapatan", "simpanan", "emas", or "asb")
        - 'haul' (boolean)
        - 'halal' (boolean
        If Income (pendapatan):
        - 'incGaji' (salary), 'incBebas' (freelance), 'kwsp' (EPF deductions
        If Gold (emas):
        - 'has_worn_item' (boolean), 'worn_weight' (number in grams)
        - 'has_stored_item' (boolean), 'stored_weight' (number in grams
        If ASB:
        - 'kaedah' ("tradisional" or "mustaghallat"), 'asbNilai' (total value), 'asbDiv' (dividend amount
        Return ONLY a JSON object merging the current facts with the newly extracted facts. 
        Do not include markdown blocks or any other text.
        """

        try:
            # Enforce JSON output using the new SDK configuration
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Extraction Error: {e}")
            return current_facts

    @staticmethod
    def generate_chat_response(user_message: str, kbes_result: dict) -> str:
        """Formulates a conversational response based on the Expert System's output."""
        client = GeminiService.get_client()

        prompt = f"""
        You are a helpful and polite Zakat Assistant for Lembaga Zakat Selangor.
        A user has sent this message: "{user_message}"

        The backend Knowledge-Based Expert System (KBES) has evaluated the facts and returned this data:
        Conclusion: {kbes_result.get('conclusion')}
        Reason: {kbes_result.get('reason')}
        Payable Amount: RM {kbes_result.get('payable_amount')}
        Current Facts: {json.dumps(kbes_result.get('final_facts'))}

        Instructions:
        1. If the Conclusion is 'None', it means the Expert System needs more information. Ask the user politely for the missing facts (e.g., "Are you calculating for income, savings, or gold?").
        2. If the Conclusion is 'WAJIB', inform them of the payable amount warmly.
        3. If the Conclusion is 'TIDAK', explain the reason why they do not need to pay.
        4. Keep your response brief, natural, and conversational in Malay or English depending on the user's language.
        """

        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Generation Error: {e}")
            return "I am sorry, I encountered an error processing your request."