from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import requests

class RPC:
    def __init__(self, rpc_user, rpc_password, rpc_host='127.0.0.1', rpc_port=8332):
        self.rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")

    # Fetch all transactions currently in the mempool.
    def fetch_mempool_transactions(self):
        try:
            return self.rpc_connection.getrawmempool()
        except JSONRPCException as e:
            print(f"Error fetching mempool transactions: {e}")
            return []

    # Fetch metadata for the latest block.
    def fetch_latest_block_metadata(self):
        try:
            latest_block_hash = self.rpc_connection.getbestblockhash()
            latest_block = self.rpc_connection.getblock(latest_block_hash)
            return {
                "block_hash": latest_block["hash"],
                "version": latest_block["version"],
                "previous_hash": latest_block["previousblockhash"],
                "merkle_root": latest_block["merkleroot"],
                "timestamp": latest_block["time"],
                "bits": int(latest_block["bits"], 16)
            }
        except JSONRPCException as e:
            print(f"Error fetching block metadata: {e}")
            return {}

    # Collect mempool transactions and block metadata, then return all required data.
    def collect_data(self):
        mempool_txids = self.fetch_mempool_transactions()
        latest_block_data = self.fetch_latest_block_metadata()

        return {
            "mempool_txids": mempool_txids,
            **latest_block_data
        }

if __name__ == "__main__":
    collector = RPC("clickmine", "clickminepassword")
    data = collector.collect_data()
    print(f"Collected Data: {data}")
