from flask import Flask, jsonify, request, send_from_directory

from wallet import Wallet
from miner import Miner

app = Flask(__name__, static_folder='static')

wallet = Wallet()
wallet.generate_wallet() 

miner = Miner()
miner.test_fetch_data(25)
miner.create_block_with_coinbase(wallet.bitcoin_address)

# Note to self: GET vs. POST will varry by the direction of info
@app.route('/app/hash', methods=['GET'])
def hash_block():
    result = miner.hash()
    return jsonify(miner.get_dict())
    
@app.route('/app/generate_wallet', methods=['GET'])
def generate_wallet():
    return jsonify(wallet.get_dict())

@app.route('/app/block_data', methods=['GET'])
def block_data():
    return jsonify(miner.get_dict())

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index(path):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)