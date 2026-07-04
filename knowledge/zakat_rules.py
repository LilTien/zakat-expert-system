from knowledge.master_rules import Rule

def get_all_rules() -> list[Rule]:
    """
    Returns the complete R001-R020 rule base.
    Every rule condition checks that 'conclusion' is NOT set yet.
    """
    return [
        # --- ELIGIBILITY / SHORT-CIRCUIT (Salience 95-100) ---
        Rule(
            id="R001", salience=100, name="Syarat Wajib: Islam (True)",
            description="User is Muslim -> Eligible",
            condition=lambda wm: wm.get_fact('muslim') is True and wm.get_fact('conclusion') is None and wm.get_fact('eligible') is None,
            action=lambda wm: wm.add_fact('eligible', True)
        ),
        Rule(
            id="R002", salience=100, name="Syarat Wajib: Islam (False)",
            description="Not Muslim -> TIDAK",
            condition=lambda wm: wm.get_fact('muslim') is False and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Bukan Islam')]
        ),
        Rule(
            id="R004", salience=95, name="Syarat Wajib: Haul",
            description="Property did not complete Haul -> TIDAK",
            condition=lambda wm: wm.get_fact('zakatType') in ['simpanan', 'emas', 'asb'] and wm.get_fact('haul') is False and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Belum cukup haul')]
        ),

        # --- GOLD CATEGORY (Salience 82-84) ---
        Rule(
            id="R008", salience=84, name="Gold Worn",
            description="Worn gold value - Uruf (800g)",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact('haul') is True and wm.get_fact('has_worn_item') is True and wm.get_fact('goldWornZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldWornZ', wm.get_fact('worn_weight', 0) - 800) # simplified math
        ),
        Rule(
            id="R009", salience=83, name="Gold Stored",
            description="Stored gold value (if >= 85g)",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact('haul') is True and wm.get_fact('has_stored_item') is True and wm.get_fact('goldStoredZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldStoredZ', wm.get_fact('stored_weight', 0))
        ),
        Rule(
            id="R010", salience=82, name="Gold Pawned",
            description="Pawned gold value",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact('haul') is True and wm.get_fact('has_pawned_item') is True and wm.get_fact('goldPawnedZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldPawnedZ', wm.get_fact('pawned_weight', 0))
        ),

        # --- GOLD COMBINE (Salience 75) ---
        Rule(
            id="R011", salience=75, name="Combine Gold",
            description="Sum all gold values",
            condition=lambda wm: wm.get_fact('conclusion') is None and (wm.get_fact('goldWornZ') is not None or wm.get_fact('goldStoredZ') is not None or wm.get_fact('goldPawnedZ') is not None) and wm.get_fact('payableBase') is None,
            action=lambda wm: [
                wm.add_fact('basis', 'gold'),
                wm.add_fact('payableBase', max(0, wm.get_fact('goldWornZ', 0)) + wm.get_fact('goldStoredZ', 0) + wm.get_fact('goldPawnedZ', 0))
            ]
        ),

        # --- NISAB DECISION (Salience 60) ---
        Rule(
            id="R016", salience=60, name="Gold Nisab Satisfied",
            description="Payable base > 0 -> Nisab Satisfied",
            condition=lambda wm: wm.get_fact('basis') == 'gold' and wm.get_fact('payableBase', 0) > 0 and wm.get_fact('nisabSatisfied') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('nisabSatisfied', True)
        ),
        Rule(
            id="R017", salience=60, name="Gold Nisab Failed",
            description="Payable base <= 0 -> TIDAK",
            condition=lambda wm: wm.get_fact('basis') == 'gold' and wm.get_fact('payableBase', 0) <= 0 and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Bawah uruf / nisab')]
        ),

        # --- OBLIGATION (Salience 50) ---
        Rule(
            id="R018", salience=50, name="Zakat Obligatory",
            description="Eligible and Nisab satisfied -> Obligatory",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('nisabSatisfied') is True and wm.get_fact('zakatObligatory') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('zakatObligatory', True)
        ),

        # --- PAYABLE (Salience 40) ---
        Rule(
            id="R019", salience=40, name="Calculate Payable",
            description="Calculate amount and declare WAJIB",
            condition=lambda wm: wm.get_fact('zakatObligatory') is True and wm.get_fact('payableAmount') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: [
                wm.add_fact('payableAmount', wm.get_fact('payableBase') * wm.get_fact('rate', 0.025)),
                wm.add_fact('conclusion', 'WAJIB')
            ]
        )
    ]