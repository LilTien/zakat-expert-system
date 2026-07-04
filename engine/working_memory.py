from typing import Dict, Any, List


class WorkingMemory:
    """Stores known facts and tracks the reasoning trace."""

    def __init__(self, initial_facts: Dict[str, Any]):
        self.facts: Dict[str, Any] = initial_facts.copy()
        self.trace: List[Dict[str, str]] = []

    def add_fact(self, key: str, value: Any) -> None:
        """Adds or updates a fact in memory."""
        self.facts[key] = value

    def get_fact(self, key: str, default: Any = None) -> Any:
        """Retrieves a fact from memory."""
        return self.facts.get(key, default)

    def record_trace(self, rule_id: str, description: str) -> None:
        """Records a fired rule for the explanation facility."""
        self.trace.append({
            "rule_id": rule_id,
            "description": description
        })