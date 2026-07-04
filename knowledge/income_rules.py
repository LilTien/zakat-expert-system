from knowledge.master_rules import Rule
from database.constants import ZAKAT_RATE

def get_income_rules() -> list[Rule]:
    return [
        Rule(
            id="INC_01",
            name="Calculate Net Income",
            description="IF gross income and allowed deductions are known, THEN calculate net income.",
            condition=lambda wm: wm.get_fact('gross_income') is not None and wm.get_fact('net_income') is None,
            action=lambda wm: wm.add_fact('net_income', wm.get_fact('gross_income') - wm.get_fact('deductions', 0))
        ),
        Rule(
            id="INC_02",
            name="Income Nisab Eligibility",
            description="IF net income >= nisab, THEN user is eligible for income zakat.",
            condition=lambda wm: wm.get_fact('net_income') is not None and wm.get_fact('net_income') >= wm.get_fact('nisab') and wm.get_fact('is_eligible') is None,
            action=lambda wm: wm.add_fact('is_eligible', True)
        ),
        Rule(
            id="INC_03",
            name="Income Below Nisab",
            description="IF net income < nisab, THEN user is NOT eligible for income zakat.",
            condition=lambda wm: wm.get_fact('net_income') is not None and wm.get_fact('net_income') < wm.get_fact('nisab') and wm.get_fact('is_eligible') is None,
            action=lambda wm: wm.add_fact('is_eligible', False)
        ),
        Rule(
            id="INC_04",
            name="Calculate Income Zakat Amount",
            description="IF eligible for income zakat, THEN zakat amount = net income * 2.5%.",
            condition=lambda wm: wm.get_fact('is_eligible') is True and wm.get_fact('zakat_payable') is None,
            action=lambda wm: wm.add_fact('zakat_payable', wm.get_fact('net_income') * ZAKAT_RATE)
        )
    ]