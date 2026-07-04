from knowledge.master_rules import Rule
from database.constants import ZAKAT_RATE

# Selangor specific uruf limits
URUF_WORN_GOLD = 800.0
URUF_KEPT_GOLD = 85.0

def get_gold_rules() -> list[Rule]:
    return [
        Rule(
            id="GLD_01",
            name="Worn Gold Uruf Check",
            description=f"IF worn gold exceeds uruf ({URUF_WORN_GOLD}g), THEN calculate taxable weight.",
            condition=lambda wm: wm.get_fact('gold_type') == 'worn' and wm.get_fact('gold_weight') > URUF_WORN_GOLD and wm.get_fact('taxable_weight') is None,
            action=lambda wm: wm.add_fact('taxable_weight', wm.get_fact('gold_weight') - URUF_WORN_GOLD)
        ),
        Rule(
            id="GLD_02",
            name="Kept Gold Check",
            description=f"IF kept gold >= uruf ({URUF_KEPT_GOLD}g), THEN entire weight is taxable.",
            condition=lambda wm: wm.get_fact('gold_type') == 'kept' and wm.get_fact('gold_weight') >= URUF_KEPT_GOLD and wm.get_fact('taxable_weight') is None,
            action=lambda wm: wm.add_fact('taxable_weight', wm.get_fact('gold_weight'))
        ),
        Rule(
            id="GLD_03",
            name="Gold Below Uruf",
            description="IF gold weight is below uruf, THEN not eligible for zakat.",
            condition=lambda wm: wm.get_fact('taxable_weight') is None and wm.get_fact('is_eligible') is None,
            action=lambda wm: [wm.add_fact('is_eligible', False), wm.add_fact('zakat_payable', 0.0)]
        ),
        Rule(
            id="GLD_04",
            name="Calculate Gold Zakat",
            description="IF taxable weight exists, THEN calculate zakat based on current gold price.",
            condition=lambda wm: wm.get_fact('taxable_weight') is not None and wm.get_fact('is_eligible') is None,
            action=lambda wm: [
                wm.add_fact('is_eligible', True),
                wm.add_fact('zakat_payable', wm.get_fact('taxable_weight') * wm.get_fact('gold_price') * ZAKAT_RATE)
            ]
        )
    ]