from flask import Flask, jsonify, request

from wallet import Wallet
from miner import Miner

app = Flask(__name__)

wallet = Wallet()
wallet.generate_wallet() 
address = wallet.get_wallet()['bitcoin_address']

miner = Miner()
miner.fetch_test_data(25)
miner.create_block_with_coinbase(address)

# Note to self: GET vs. POST will varry by the direction of info
@app.route('/app/hash', methods=['GET'])
def hash_block():
    result = miner.hash()
    return jsonify({"status": "success!" if result else "No luck :(",
                    "hash": miner.block_hash_hex,
                    "nonce": miner.nonce_attempt})
    
@app.route('/app/generate_wallet', methods=['GET'])
def generate_wallet():
    return jsonify(wallet.get_wallet())  

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)