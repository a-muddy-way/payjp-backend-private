from flask import Flask, jsonify
import payjp
import os

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test():
    try:
        payjp.api_key = os.getenv('PAYJP_SECRET_KEY', 'sk_test_933bc71b8e01aa31e9232c14')
        charge = payjp.Charge.create(
            amount=1000,
            currency='jpy',
            card='tok_visa'
        )
        return jsonify({"status": "ok", "charge_id": charge.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)
