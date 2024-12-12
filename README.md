# clickMine.org

### good article on proof of work
https://michaelnielsen.org/ddi/how-the-bitcoin-protocol-actually-works/
stopping point: " With the time-ordering now understood, let’s return to think about what happens if a dishonest party tries to double spend."

### basic rpc commands
startv1: bitcoind -rpcuser=clickmine -rpcpassword=clickminepassword -daemon
startv2: bitcoind -daemon
stop: bitcoin-cli stop
test/print info: bitcoin-cli getblockchaininfo
list mempool: bitcoin-cli getrawmempool
get latest block: bitcoin-cli getblock $(bitcoin-cli getbestblockhash)

### launch API server
python3 app.py

### Start and end virtual environment
source venv/bin/activate
exit

### Install third party packages
pip install -r requirements.txt

### Build the docker image
docker build -t clickmine-image .

### Run docker container
docker run -d -p 8080:5000 clickmine-image 