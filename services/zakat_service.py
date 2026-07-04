from engine.working_memory import WorkingMemory
from engine.forward_chaining import InferenceEngine
from services.explanation import ExplanationFacility
from knowledge.zakat_rules import get_all_rules
import json


def process_consultation(user_facts: dict) -> dict:
    """
    Orchestrates the KBES pipeline using the unified rule base.
    This replaces the individual module processors (process_income, process_gold, etc.)
    because the rules now handle the type routing dynamically.
    """
    # 1. Initialize Working Memory
    wm = WorkingMemory(user_facts)

    # 2. Load the unified rule base (R001 - R020)
    rules = get_all_rules()

    # 3. Run Inference Engine (Recognize-Act Cycle)
    InferenceEngine.run(rules, wm)

    # 4. Generate Explanation from the trace
    explanation = ExplanationFacility.generate_explanation(wm.trace)

    # 5. Construct Result
    return {
        "conclusion": wm.get_fact('conclusion'),
        "reason": wm.get_fact('reason'),
        "payable_amount": wm.get_fact('payableAmount', 0.0),
        "final_facts": wm.facts,
        "reasoning_trace": explanation
    }


# ==========================================
# TEST BLOCK: Mixed Gold Conflict Resolution
# ==========================================
if __name__ == "__main__":
    # These are the exact F001-F041 facts required to trigger the mixed gold trace
    initial_facts = {
        "muslim": True,
        "zakatType": "emas",
        "haul": True,
        "has_worn_item": True,
        "worn_weight": 900.0,
        "has_stored_item": True,
        "stored_weight": 100.0,
        "has_pawned_item": True,
        "pawned_weight": 200.0,
        "rate": 0.025
    }

    print("--- STARTING KBES CONSULTATION (MIXED GOLD TEST) ---")
    result = process_consultation(initial_facts)

    print("\n--- FINAL CONCLUSION ---")
    print(f"Status: {result['conclusion']}")
    print(f"Payable Amount: RM {result['payable_amount']}")

    print("\n--- REASONING TRACE (Notice the Agenda & Salience) ---")
    for step in result['reasoning_trace']:
        print(step)