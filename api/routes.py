from flask import Blueprint, request, jsonify
from services.zakat_service import process_consultation, process_asnaf_standard

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/calculate/income', methods=['POST'])
def calculate_income():
    """
    Calculate Income Zakat
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
            muslim: { type: boolean, example: true }
            halal: { type: boolean, example: true }
            method: { type: string, example: bersih }
            incGaji: { type: number, example: 50000.00 }
            incBebas: { type: number, example: 10000.00 }
            incSewa: { type: number, example: 0.0 }
            incBeri: { type: number, example: 0.0 }
            hkDewasaKerja: { type: integer, example: 0 }
            hkDewasaTak: { type: integer, example: 1 }
            hkIpt: { type: integer, example: 0 }
            hkAnak7_17: { type: integer, example: 2 }
            hkAnak6: { type: integer, example: 0 }
            hkOku: { type: integer, example: 0 }
            hkKronik: { type: integer, example: 0 }
            hkJagaan: { type: integer, example: 0 }
            kwsp: { type: number, example: 5500.00 }
            th: { type: number, example: 0.0 }
    responses:
      200: { description: Calculation successful }
    """
    data = request.json
    data['zakatType'] = 'pendapatan'
    data.setdefault('muslim', True)
    return jsonify(process_consultation(data)), 200


@api_bp.route('/calculate/savings', methods=['POST'])
def calculate_savings():
    """
    Calculate Savings Zakat
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
            muslim: { type: boolean, example: true }
            haul: { type: boolean, example: true }
            accounts:
              type: array
              items:
                type: object
                properties:
                  type: { type: string, example: simpanan_biasa }
                  baki: { type: number, example: 30000.00 }
                  faedah: { type: number, example: 500.00 }
    responses:
      200: { description: Calculation successful }
    """
    data = request.json
    data['zakatType'] = 'simpanan'
    data.setdefault('muslim', True)
    return jsonify(process_consultation(data)), 200


@api_bp.route('/calculate/gold', methods=['POST'])
def calculate_gold():
    """
    Calculate Gold Zakat
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
            muslim: { type: boolean, example: true }
            haul: { type: boolean, example: true }
            goldItems:
              type: array
              items:
                type: object
                properties:
                  kat: { type: string, enum: [worn, stored, pawned], example: worn }
                  berat: { type: number, example: 900.0 }
                  karat: { type: integer, example: 916 }
                  pinjaman: { type: number, example: 0.0 }
                  upah: { type: number, example: 0.0 }
    responses:
      200: { description: Calculation successful }
    """
    data = request.json
    data['zakatType'] = 'emas'
    data.setdefault('muslim', True)

    # Mapper: Translate documentation's goldItems[] array into the flat variables the Rule Base expects
    for item in data.get('goldItems', []):
        if item.get('kat') == 'worn':
            data['has_worn_item'] = True
            data['worn_weight'] = item.get('berat', 0)
            data['worn_karat'] = item.get('karat', 999)
        elif item.get('kat') == 'stored':
            data['has_stored_item'] = True
            data['stored_weight'] = item.get('berat', 0)
            data['stored_karat'] = item.get('karat', 999)
        elif item.get('kat') == 'pawned':
            data['has_pawned_item'] = True
            data['pawned_weight'] = item.get('berat', 0)
            data['pawned_karat'] = item.get('karat', 999)
            data['pawned_loan'] = item.get('pinjaman', 0)
            data['pawned_fee'] = item.get('upah', 0)

    return jsonify(process_consultation(data)), 200


@api_bp.route('/calculate/asb', methods=['POST'])
def calculate_asb():
    """
    Calculate ASB Zakat
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
            muslim: { type: boolean, example: true }
            haul: { type: boolean, example: true }
            kaedah: { type: string, enum: [tradisional, mustaghallat], example: mustaghallat }
            asbNilai: { type: number, example: 100000.00 }
            asbDiv: { type: number, example: 5000.00 }
    responses:
      200: { description: Calculation successful }
    """
    data = request.json
    data['zakatType'] = 'asb'
    data.setdefault('muslim', True)
    return jsonify(process_consultation(data)), 200


@api_bp.route('/asnaf/screen', methods=['POST'])
def screen_asnaf():
    """
    Screen Asnaf Eligibility (Decoupled from Rule Base)
    ---
    tags:
      - Asnaf Screening
    """
    data = request.json
    return jsonify(process_asnaf_standard(data)), 200