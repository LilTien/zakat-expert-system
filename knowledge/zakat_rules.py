from knowledge.master_rules import Rule


# --- HELPER FUNCTIONS FOR COMPLEX ACTIONS ---
def _assess_pendapatan(wm):
    """Helper for R006: Calculates gross/net income for Pendapatan."""
    gross = (wm.get_fact('incGaji', 0) + wm.get_fact('incBebas', 0) +
             wm.get_fact('incSewa', 0) + wm.get_fact('incBeri', 0))

    deductions = 0
    if wm.get_fact('method') == 'bersih':
        # Assumes you pass 'had_kifayah' and 'kwsp' into WM from your API/Constants
        deductions = wm.get_fact('had_kifayah', 0) + wm.get_fact('kwsp', 0)

    assessable = max(0, gross - deductions)

    wm.add_fact('assessableAmount', assessable)
    wm.add_fact('nisabTestValue', assessable)
    wm.add_fact('payableBase', assessable)
    wm.add_fact('rate', 0.025)
    wm.add_fact('basis', 'rm')


def _assess_simpanan(wm):
    """Helper for R007: Sums all savings accounts."""
    accounts = wm.get_fact('accounts', [])
    total_baki = sum(float(acc.get('baki', 0)) for acc in accounts)

    wm.add_fact('nisabTestValue', total_baki)
    wm.add_fact('payableBase', total_baki)
    wm.add_fact('rate', 0.025)
    wm.add_fact('basis', 'rm')


def _calculate_payable(wm):
    """Helper for R019: Calculates final RM payable amount."""
    base = wm.get_fact('payableBase', 0)
    rate = wm.get_fact('rate', 0.025)

    if wm.get_fact('basis') == 'gold':
        # If gold, base is in grams. Convert to RM using the 24k price we fixed earlier.
        price = wm.get_fact('gold_price_per_gram_24k', 320.0)
        payable_amount = base * price * rate
    else:
        payable_amount = base * rate

    wm.add_fact('payableAmount', payable_amount)
    wm.add_fact('conclusion', 'WAJIB')


def get_all_rules() -> list[Rule]:
    """
    Returns the complete R001-R020 rule base.
    Every rule condition checks that 'conclusion' is NOT set yet.
    """
    return [
        # =====================================================================
        # BAND 1: ELIGIBILITY / SHORT-CIRCUIT (Salience 95-100)
        # =====================================================================
        Rule(
            id="R001", salience=100, name="Syarat Wajib: Islam (True)",
            description="User is Muslim -> Eligible",
            condition=lambda wm: wm.get_fact('muslim') is True and wm.get_fact('conclusion') is None and wm.get_fact(
                'eligible') is None,
            action=lambda wm: wm.add_fact('eligible', True)
        ),
        Rule(
            id="R002", salience=100, name="Syarat Wajib: Islam (False)",
            description="Not Muslim -> TIDAK",
            condition=lambda wm: wm.get_fact('muslim') is False and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Bukan Islam')]
        ),
        Rule(
            id="R003", salience=95, name="Syarat Wajib: Halal",
            description="Income source is Haram -> TIDAK",
            condition=lambda wm: wm.get_fact('zakatType') == 'pendapatan' and wm.get_fact(
                'halal') is False and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Harta haram')]
        ),
        Rule(
            id="R004", salience=95, name="Syarat Wajib: Haul",
            description="Property did not complete Haul -> TIDAK",
            condition=lambda wm: wm.get_fact('zakatType') in ['simpanan', 'emas', 'asb'] and wm.get_fact(
                'haul') is False and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Belum cukup haul')]
        ),

        # =====================================================================
        # BAND 2: GOLD CATEGORY (Salience 82-84)
        # =====================================================================
        Rule(
            id="R008", salience=84, name="Gold Worn",
            description="Worn gold value - Uruf (800g)",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact(
                'haul') is True and wm.get_fact('has_worn_item') is True and wm.get_fact(
                'goldWornZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldWornZ', max(0, wm.get_fact('worn_weight', 0) - 800))
        ),
        Rule(
            id="R009", salience=83, name="Gold Stored",
            description="Stored gold value (if >= 85g)",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact(
                'haul') is True and wm.get_fact('has_stored_item') is True and wm.get_fact(
                'goldStoredZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldStoredZ', wm.get_fact('stored_weight', 0) if wm.get_fact('stored_weight',
                                                                                                        0) >= 85 else 0)
        ),
        Rule(
            id="R010", salience=82, name="Gold Pawned",
            description="Pawned gold value",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'emas' and wm.get_fact(
                'haul') is True and wm.get_fact('has_pawned_item') is True and wm.get_fact(
                'goldPawnedZ') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('goldPawnedZ', wm.get_fact('pawned_weight', 0))
        ),

        # =====================================================================
        # BAND 3: TYPE ASSESSMENT (Salience 70-80)
        # =====================================================================
        Rule(
            id="R005", salience=80, name="Income Admissible",
            description="Eligible and Halal -> Income Admissible",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact(
                'zakatType') == 'pendapatan' and wm.get_fact('halal') is True and wm.get_fact(
                'incomeAdmissible') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('incomeAdmissible', True)
        ),
        Rule(
            id="R006", salience=70, name="Assess Pendapatan",
            description="Calculate Income Zakat base",
            condition=lambda wm: wm.get_fact('incomeAdmissible') is True and wm.get_fact(
                'payableBase') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: _assess_pendapatan(wm)
        ),
        Rule(
            id="R007", salience=80, name="Assess Simpanan",
            description="Sum all savings accounts",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact(
                'zakatType') == 'simpanan' and wm.get_fact('haul') is True and wm.get_fact(
                'payableBase') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: _assess_simpanan(wm)
        ),
        Rule(
            id="R012", salience=80, name="Assess ASB Tradisional",
            description="Tradisional: base is total value, rate 2.5%",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'asb' and wm.get_fact(
                'haul') is True and wm.get_fact('kaedah') == 'tradisional' and wm.get_fact(
                'payableBase') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: [
                wm.add_fact('nisabTestValue', wm.get_fact('asbNilai', 0)),
                wm.add_fact('payableBase', wm.get_fact('asbNilai', 0)),
                wm.add_fact('rate', 0.025),
                wm.add_fact('basis', 'rm')
            ]
        ),
        Rule(
            id="R013", salience=80, name="Assess ASB Mustaghallat",
            description="Mustaghallat: base is dividend only, rate 2.57%",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact('zakatType') == 'asb' and wm.get_fact(
                'haul') is True and wm.get_fact('kaedah') == 'mustaghallat' and wm.get_fact(
                'payableBase') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: [
                wm.add_fact('nisabTestValue', wm.get_fact('asbNilai', 0)),
                wm.add_fact('payableBase', wm.get_fact('asbDiv', 0)),
                wm.add_fact('rate', 0.0257),
                wm.add_fact('basis', 'rm')
            ]
        ),

        # =====================================================================
        # BAND 4: GOLD COMBINE (Salience 75)
        # =====================================================================
        Rule(
            id="R011", salience=75, name="Combine Gold",
            description="Sum all gold gram values",
            condition=lambda wm: wm.get_fact('conclusion') is None and (
                        wm.get_fact('goldWornZ') is not None or wm.get_fact('goldStoredZ') is not None or wm.get_fact(
                    'goldPawnedZ') is not None) and wm.get_fact('payableBase') is None,
            action=lambda wm: [
                wm.add_fact('basis', 'gold'),
                wm.add_fact('payableBase',
                            wm.get_fact('goldWornZ', 0) + wm.get_fact('goldStoredZ', 0) + wm.get_fact('goldPawnedZ', 0))
            ]
        ),

        # =====================================================================
        # BAND 5: NISAB DECISION (Salience 60)
        # =====================================================================
        Rule(
            id="R014", salience=60, name="RM Nisab Satisfied",
            description="Test value >= RM Nisab -> Satisfied",
            condition=lambda wm: wm.get_fact('basis') == 'rm' and wm.get_fact('nisabTestValue', 0) >= wm.get_fact(
                'nisab_value', 24000.0) and wm.get_fact('nisabSatisfied') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('nisabSatisfied', True)
        ),
        Rule(
            id="R015", salience=60, name="RM Nisab Failed",
            description="Test value < RM Nisab -> TIDAK",
            condition=lambda wm: wm.get_fact('basis') == 'rm' and wm.get_fact('nisabTestValue', 0) < wm.get_fact(
                'nisab_value', 24000.0) and wm.get_fact('conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Bawah nisab')]
        ),
        Rule(
            id="R016", salience=60, name="Gold Nisab Satisfied",
            description="Payable gold weight > 0 -> Satisfied",
            condition=lambda wm: wm.get_fact('basis') == 'gold' and wm.get_fact('payableBase', 0) > 0 and wm.get_fact(
                'nisabSatisfied') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: wm.add_fact('nisabSatisfied', True)
        ),
        Rule(
            id="R017", salience=60, name="Gold Nisab Failed",
            description="Payable gold weight <= 0 -> TIDAK",
            condition=lambda wm: wm.get_fact('basis') == 'gold' and wm.get_fact('payableBase', 0) <= 0 and wm.get_fact(
                'conclusion') is None,
            action=lambda wm: [wm.add_fact('conclusion', 'TIDAK'), wm.add_fact('reason', 'Bawah uruf / nisab')]
        ),

        # =====================================================================
        # BAND 6: OBLIGATION & PAYABLE (Salience 30-50)
        # =====================================================================
        Rule(
            id="R018", salience=50, name="Zakat Obligatory",
            description="Eligible and Nisab satisfied -> Obligatory",
            condition=lambda wm: wm.get_fact('eligible') is True and wm.get_fact(
                'nisabSatisfied') is True and wm.get_fact('zakatObligatory') is None and wm.get_fact(
                'conclusion') is None,
            action=lambda wm: wm.add_fact('zakatObligatory', True)
        ),
        Rule(
            id="R019", salience=40, name="Calculate Payable",
            description="Calculate final RM amount and declare WAJIB",
            condition=lambda wm: wm.get_fact('zakatObligatory') is True and wm.get_fact(
                'payableAmount') is None and wm.get_fact('conclusion') is None,
            action=lambda wm: _calculate_payable(wm)
        ),
        Rule(
            id="R020", salience=30, name="Calculate Monthly",
            description="Income Zakat payable / 12",
            condition=lambda wm: wm.get_fact('zakatType') == 'pendapatan' and wm.get_fact(
                'conclusion') == 'WAJIB' and wm.get_fact('monthly') is None,
            action=lambda wm: wm.add_fact('monthly', wm.get_fact('payableAmount', 0) / 12)
        )
    ]