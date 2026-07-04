from knowledge.master_rules import Rule
from database.constants import ZAKAT_RATE

def get_savings_rules() -> list[Rule]:
    return [
        Rule(
            id="SAV_01",
            name="Haul Check",
            description="IF savings have not completed 1 year (Haul), THEN not eligible.",
            condition=lambda wm: wm.get_fact('haul_completed') is False and wm.get_fact('is_eligible') is None,
            action=lambda wm: wm.add_fact('is_eligible', False)
        ),
        Rule(
            id="SAV_02",
            name="Savings Nisab Eligibility",
            description="IF lowest balance over 1 year >= nisab, THEN user is eligible.",
            condition=lambda wm: wm.get_fact('haul_completed') is True and wm.get_fact('lowest_balance') >= wm.get_fact('nisab') and wm.get_fact('is_eligible') is None,
            action=lambda wm: wm.add_fact('is_eligible', True)
        ),
        Rule(
            id="SAV_03",
            name="Calculate Savings Zakat",
            description="IF eligible, THEN zakat amount = lowest balance * 2.5%.",
            condition=lambda wm: wm.get_fact('is_eligible') is True and wm.get_fact('zakat_payable') is None,
            action=lambda wm: wm.add_fact('zakat_payable', wm.get_fact('lowest_balance') * ZAKAT_RATE)
        )
    ]