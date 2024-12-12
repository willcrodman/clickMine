import hashlib
import struct
import requests
import base58
import random

from wallet import Wallet

class Miner:
    def __init__(self):
        self._block_hash: str = None
        self._version: int = None
        self._previous_hash: str = None
        self._merkle_root: str = None
        self._timestamp: int = None
        self._bits: int = None
        self._target: int = None
        self._transactions: list = None
           
        self.nonce_attempt: int = None
        self.block_header: bytes = None
        self.block_hash_hex: str = None
        self.success: bool = None 
        
    @staticmethod
    def decode_bits(bits):
        exponent = bits >> 24
        mantissa = bits & 0xFFFFFF
        return mantissa * (2 ** (8 * (exponent - 3))) 
    
    @staticmethod
    def base58_to_hash160(address):
        decoded = base58.b58decode(address)
        payload, checksum = decoded[:-4], decoded[-4:]    
        return payload[1:] 
    
    @staticmethod
    def nested_sha256(data):
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()


    def test_fetch_data(self, n_transactions=None):
        # Fetch the latest block metadata via API
        latest_block_url = "https://blockchain.info/latestblock"
        latest_block_data = requests.get(latest_block_url).json()
        self._block_hash = latest_block_data['hash']

        block_data_url = f"https://blockchain.info/rawblock/{self._block_hash}"
        block_data = requests.get(block_data_url).json()
        
        self._version = block_data['ver']
        self._previous_hash = block_data['prev_block']
        self._timestamp = block_data['time']
        self._bits = block_data['bits']
        self._target = self.decode_bits(self._bits)

        if n_transactions is not None:
            self._transactions = block_data['tx'][:n_transactions]
        else:
            self._transactions = block_data['tx']

    def compute_merkle_root(self, transactions):
        # Compute the Merkle root, including the coinbase transaction
        hashes = transactions[:]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:  # If odd, duplicate the last hash
                hashes.append(hashes[-1])
            hashes = [self.nested_sha256(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
        return hashes[0].hex()

    def create_coinbase_transaction(self, address):
        address_hash = self.base58_to_hash160(address)
        coinbase_script = b"clickMine.org"
        coinbase_tx_id = b"\x00" * 32
        
        script_pubkey = b'\x76\xa9' + bytes([len(address_hash)]) + address_hash + b'\x88\xac'
        value = 50 * 10**8  
        coinbase_output = struct.pack("<Q", value) + bytes([len(script_pubkey)]) + script_pubkey

        return (
            b"\x01"  # Version
            + b"\x01"  # Input count
            + coinbase_tx_id  # Null input
            + b"\xFF\xFF\xFF\xFF"  # Index (coinbase index)
            + bytes([len(coinbase_script)]) + coinbase_script  # Input script
            + b"\xFF\xFF\xFF\xFF"  # Sequence
            + b"\x01"  # Output count
            + coinbase_output  # Transaction output
            + b"\x00\x00\x00\x00"  # Locktime
        )

    def create_block_with_coinbase(self, coinbase_tx_address):
        coinbase_tx = self.create_coinbase_transaction(coinbase_tx_address)
        transaction_hashes = [bytes.fromhex(tx['hash']) for tx in self._transactions]
        transaction_hashes.insert(0, self.nested_sha256(coinbase_tx))  # Add coinbase transaction
        self._merkle_root = self.compute_merkle_root(transaction_hashes)  

    def create_block_header(self):
        self.block_header = struct.pack(
            '<L32s32sLLL',
            self._version,
            bytes.fromhex(self._previous_hash),
            bytes.fromhex(self._merkle_root),
            self._timestamp,
            self._bits,
            self.nonce_attempt
        )
        
        self.block_hash_hex = hashlib.sha256(hashlib.sha256(self.block_header).digest()).hexdigest()

    def hash(self, nonce_attempt=None):
        self.nonce_attempt = nonce_attempt or random.randint(0, 4294967295)
        print("nonce:", self.nonce_attempt)
        self.create_block_header()
        hash_as_int = int(self.block_hash_hex, 16)
        
        if hash_as_int < self._target:
            print(f"Solved hash! Nonce: {self.nonce_attempt} | Hash: {self.block_hash_hex}")
            self.success = True
            self.test_broadcast_block()
        else:
            print(f"Unsolved hash. Nonce: {self.nonce_attempt} | Hash: {self.block_hash_hex}")
            self.success = False
            
    def test_broadcast_block(): 
        pass
        
    def get_dict(self):
        return {
            "block_hash": self._block_hash,
            "version": self._version,
            "previous_hash": self._previous_hash,
            "merkle_root": self._merkle_root,
            "timestamp": self._timestamp,
            "bits": self._bits,
            "target": self._target,
            "transactions": self._transactions,
            "nonce_attempt": self.nonce_attempt,
            "block_header": self.block_header.hex() if self.block_header else None,
            "block_hash_hex": self.block_hash_hex,
            "success": "Success" if self.success else "Unsuccess"
        }
        
if __name__ == "__main__":
    wallet = Wallet()
    wallet.generate_wallet()
    address = wallet.get_wallet()['bitcoin_address']
    
    miner = Miner()
    miner.test_fetch_data(25)
    miner.create_block_with_coinbase(address)  # Replace with your address
    miner.hash()
