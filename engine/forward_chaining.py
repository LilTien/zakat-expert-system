from typing import List
from engine.working_memory import WorkingMemory
from knowledge.master_rules import Rule


class InferenceEngine:
    """Implements the recognize-act cycle with Agenda and Salience resolution."""

    @staticmethod
    def run(rules: List[Rule], wm: WorkingMemory) -> None:
        fired_rules = set()

        while True:
            # 1. MATCH: Collect rules whose IF-part holds and haven't fired
            agenda = [
                rule for rule in rules
                if rule.id not in fired_rules and rule.condition(wm)
            ]

            # 2. HALT: If Agenda is empty (quiescence)
            if not agenda:
                break

            # 3. CONFLICT RESOLUTION: Highest salience wins.
            # Ties keep rule-definition order (R001 before R002).
            # Python's .sort() is stable, preserving original order for ties.
            agenda.sort(key=lambda r: r.salience, reverse=True)

            selected_rule = agenda[0]

            # 4. ACT: Run the rule's THEN-part
            selected_rule.action(wm)

            # 5. RECORD: Log the trace
            agenda_ids = [r.id for r in agenda]
            wm.record_trace(
                selected_rule.id,
                f"Fired {selected_rule.id} (Salience {selected_rule.salience}). Agenda was: {agenda_ids}. Action: {selected_rule.description}"
            )

            fired_rules.add(selected_rule.id)