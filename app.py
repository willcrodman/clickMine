from flask import Flask, jsonify, request, send_from_directory, session
from datetime import datetime, timedelta
import uuid
from flask_apscheduler import APScheduler

from wallet import Wallet
from miner import Miner

app = Flask(__name__, static_folder='static')
app.secret_key = 'clickmine-password'

session_miners, session_wallets, session_timestamps = {}, {}, {}

SESSION_TIMEOUT = timedelta(minutes=15)
CLEANUP_INTERVAL = timedelta(hours=24)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@app.before_request
def initialize_session():
    if request.path == '/':
            
        session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']

        wallet = Wallet()
        wallet.generate_wallet()
        miner = Miner()
        miner.test_fetch_data()
        miner.create_block_with_coinbase(wallet.bitcoin_address)

        session_wallets[session_id] = wallet
        session_miners[session_id] = miner
        session_timestamps[session_id] = datetime.now()

def clear_stale_sessions():
    now = datetime.now()

    expired_sessions = [
        session_id for session_id, last_activity in session_timestamps.items()
        if now - last_activity > SESSION_TIMEOUT
    ]

    for session_id in expired_sessions:
        del session_miners[session_id]
        del session_wallets[session_id]
        del session_timestamps[session_id]

scheduler.add_job(
    id='clear_stale_sessions',
    func=clear_stale_sessions,
    trigger='interval',
    hours=24
)

@app.route('/app/hash', methods=['GET'])
def hash_block():
    session_id = session['session_id']
    miner = session_miners[session_id]
    miner.hash()
    return jsonify(miner.get_dict())

@app.route('/app/block_data', methods=['GET'])
def block_data():
    session_id = session['session_id']
    miner = session_miners[session_id]
    return jsonify(miner.get_dict())

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index(path):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
