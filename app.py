from flask import Flask, jsonify, request
from miner import Miner  # Import your Miner class
from wallet import Wallet

app = Flask(__name__)
miner = Miner()
wallet = Wallet()

@app.route('/api/hash', methods=['POST'])
def hash_block():
    result = miner.hash()
    return jsonify({"status": "success" if result else "failure",
                    "hash": miner.block_hash_hex,
                    "nonce": miner.nonce_attempt})
    
@app.route('/api/generate_wallet', methods=['POST'])
def generate_wallet():
    wallet.generate_wallet() 
    return jsonify(wallet.get_wallet())  

if __name__ == '__main__':
    app.run(debug=True)
