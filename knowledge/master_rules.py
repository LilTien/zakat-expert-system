from dataclasses import dataclass
from typing import Callable, Any
from engine.working_memory import WorkingMemory


@dataclass
class Rule:
    """Represents a production rule matching the ezakat.html JS spec."""
    id: str
    salience: int  # Added to support Conflict Resolution
    name: str
    description: str
    condition: Callable[[WorkingMemory], bool]
    action: Callable[[WorkingMemory], None]

    def __post_init__(self):
        if not self.id.startswith('R'):
            raise ValueError("Rule ID must follow the R001 format.")