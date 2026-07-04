from typing import List, Dict


class ExplanationFacility:
    """Generates human-readable reasoning from the Inference Engine trace."""

    @staticmethod
    def generate_explanation(trace: List[Dict[str, str]]) -> List[str]:
        explanation = []
        for step, record in enumerate(trace, 1):
            explanation.append(f"Step {step} [Rule {record['rule_id']}]: {record['description']}")

        if not explanation:
            explanation.append("No rules were applicable based on the provided facts.")

        return explanation