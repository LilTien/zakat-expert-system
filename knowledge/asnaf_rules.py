from knowledge.master_rules import Rule

def get_asnaf_rules() -> list[Rule]:
    return [
        Rule(
            id="ASN_01",
            name="Calculate Had Kifayah",
            description="IF dependents are known, THEN calculate total Had Kifayah.",
            condition=lambda wm: wm.get_fact('had_kifayah_total') is None,
            action=lambda wm: wm.add_fact('had_kifayah_total',
                wm.get_fact('base_adult') +
                (wm.get_fact('spouse_count', 0) * wm.get_fact('hk_spouse')) +
                (wm.get_fact('child_count', 0) * wm.get_fact('hk_child'))
            )
        ),
        Rule(
            id="ASN_02",
            name="Determine Fakir Status",
            description="IF household income < 50% of Had Kifayah, THEN status is Fakir.",
            condition=lambda wm: wm.get_fact('had_kifayah_total') is not None and wm.get_fact('household_income') < (wm.get_fact('had_kifayah_total') * 0.5) and wm.get_fact('asnaf_status') is None,
            action=lambda wm: wm.add_fact('asnaf_status', 'Fakir')
        ),
        Rule(
            id="ASN_03",
            name="Determine Miskin Status",
            description="IF household income < Had Kifayah but >= 50%, THEN status is Miskin.",
            condition=lambda wm: wm.get_fact('had_kifayah_total') is not None and (wm.get_fact('had_kifayah_total') * 0.5) <= wm.get_fact('household_income') < wm.get_fact('had_kifayah_total') and wm.get_fact('asnaf_status') is None,
            action=lambda wm: wm.add_fact('asnaf_status', 'Miskin')
        ),
        Rule(
            id="ASN_04",
            name="Not Asnaf",
            description="IF household income >= Had Kifayah, THEN not eligible as Asnaf.",
            condition=lambda wm: wm.get_fact('had_kifayah_total') is not None and wm.get_fact('household_income') >= wm.get_fact('had_kifayah_total') and wm.get_fact('asnaf_status') is None,
            action=lambda wm: wm.add_fact('asnaf_status', 'Not Eligible')
        )
    ]