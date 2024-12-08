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


### TODOs
1. Put the project in a virtual env (to get the Flask API working) 
2. create a requirements.txt file to specificity what additional packages are needed in side the evn
3. run the app server on launch of the website 