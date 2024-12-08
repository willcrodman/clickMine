from flask import Flask, jsonify, request
from miner import Miner  # Import your Miner class
from wallet import Wallet

app = Flask(__name__)
miner = Miner()
wallet = Wallet()

# Note to self: GET vs. POST will varry by the direction of info
@app.route('/app/hash', methods=['GET'])
def hash_block():
    result = miner.hash()
    return jsonify({"status": "success!" if result else "No luck :(",
                    "hash": miner.block_hash_hex,
                    "nonce": miner.nonce_attempt})
    
@app.route('/app/generate_wallet', methods=['GET'])
def generate_wallet():
    wallet.generate_wallet() 
    return jsonify(wallet.get_wallet())  

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)