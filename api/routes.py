from flask import Blueprint, request, jsonify
from services.zakat_service import process_consultation

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/calculate/income', methods=['POST'])
def calculate_income():
    """
    Calculate Income Zakat
    Evaluates income using the unified R001-R020 rule base.
    ---
    tags:
      - Zakat Calculators
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            muslim:
              type: boolean
              example: true
            halal:
              type: boolean
              example: true
            method:
              type: string
              example: bersih
            payableBase:
              type: number
              description: Calculated assessable amount (RM)
              example: 85764.00
            nisabTestValue:
              type: number
              example: 85764.00
            NISAB_RM:
              type: number
              example: 24000.00
    responses:
      200:
        description: Calculation successful
    """
    data = request.json
    # Inject facts required by the unified rule base
    data['zakatType'] = 'pendapatan'
    data.setdefault('muslim', True)

    result = process_consultation(data)
    return jsonify(result), 200


@api_bp.route('/calculate/savings', methods=['POST'])
def calculate_savings():
    """
    Calculate Savings Zakat
    Evaluates savings using the unified R001-R020 rule base.
    ---
    tags:
      - Zakat Calculators
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            muslim:
              type: boolean
              example: true
            haul:
              type: boolean
              example: true
            payableBase:
              type: number
              example: 30000.00
            nisabTestValue:
              type: number
              example: 30000.00
            NISAB_RM:
              type: number
              example: 24000.00
    responses:
      200:
        description: Calculation successful
    """
    data = request.json
    # Inject facts required by the unified rule base
    data['zakatType'] = 'simpanan'
    data.setdefault('muslim', True)

    result = process_consultation(data)
    return jsonify(result), 200


@api_bp.route('/calculate/gold', methods=['POST'])
def calculate_gold():
    """
    Calculate Gold Zakat (Mixed Categories)
    Evaluates worn, stored, and pawned gold utilizing conflict resolution (salience).
    ---
    tags:
      - Zakat Calculators
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            muslim:
              type: boolean
              example: true
            haul:
              type: boolean
              example: true
            has_worn_item:
              type: boolean
              example: true
            worn_weight:
              type: number
              example: 900.0
            has_stored_item:
              type: boolean
              example: true
            stored_weight:
              type: number
              example: 100.0
            has_pawned_item:
              type: boolean
              example: true
            pawned_weight:
              type: number
              example: 200.0
    responses:
      200:
        description: Calculation successful
    """
    data = request.json
    # Inject facts required by the unified rule base
    data['zakatType'] = 'emas'
    data.setdefault('muslim', True)

    result = process_consultation(data)
    return jsonify(result), 200


@api_bp.route('/asnaf/screen', methods=['POST'])
def screen_asnaf():
    """
    Screen Asnaf Eligibility (Fakir/Miskin)
    Evaluates household income against Had Kifayah limits.
    ---
    tags:
      - Asnaf Screening
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            muslim:
              type: boolean
              example: true
            household_income:
              type: number
              example: 1500.00
            spouse_count:
              type: integer
              example: 1
            child_count:
              type: integer
              example: 3
    responses:
      200:
        description: Screening successful
    """
    data = request.json
    # Inject facts required by the unified rule base
    data['zakatType'] = 'asnaf'
    data.setdefault('muslim', True)

    result = process_consultation(data)
    return jsonify(result), 200