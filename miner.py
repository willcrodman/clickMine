import hashlib
import struct
import requests
import base58
 
class Miner:
    def __init__(self):
        self._block_hash: str = None
        self._version: int = None
        self._previous_hash: str = None
        self._merkle_root: str = None
        self._timestamp: int = None
        self._bits: int = None
        self._target: int = None
        
        self.nonce_attempt: int = None
        self.block_header: bytes = None
        self.block_hash_hex: str = None   
        
    @staticmethod
    def decode_bits(bits):
        exponent = bits >> 24
        mantissa = bits & 0xFFFFFF
        return mantissa * (2 ** (8 * (exponent - 3))) 
    
    @staticmethod
    def base58_to_hash160(address):
        decoded = base58.b58decode(address)
        payload, checksum = decoded[:-4], decoded[-4:]    
        hash_twice = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
        network_byte = payload[0]
        return payload[1:]

    def sha256_data(self, data):
        # Translating SHA-256 hash calculation
        self.block_hash_hex = hashlib.sha256(hashlib.sha256(data).digest()).hexdigest()

    def create_block_header(self, nonce_attempt):
        self.nonce_attempt = nonce_attempt
        self.block_header = struct.pack(
            '<L32s32sLLL',
            self._version,
            bytes.fromhex(self._previous_hash),
            bytes.fromhex(self._merkle_root),
            self._timestamp,
            self._bits,
            nonce_attempt
        )
        
        # Call sha256_data after constructing block header
        self.sha256_data(self.block_header)

    # TODO: generate the merkle root (and prob other things) using Bitcoin Core's getrawmempool RPC, rather then getting them from API 
    def fetch_block_data(self):
        # Fetch last block PoW hash data via API
        url = "https://blockchain.info/latestblock" 
        response = requests.get(url)
        latest_block_data = response.json()
        self._block_hash = latest_block_data['hash']
        
        # Fetch last block metadata via API
        block_data = requests.get(f"https://blockchain.info/rawblock/{self._block_hash}").json()
        self._version = block_data['ver']
        self._previous_hash = block_data['prev_block']
        self._merkle_root = block_data['mrkl_root']
        self._timestamp = block_data['time']
        self._bits = block_data['bits']
        self._target = self.decode_bits(self._bits)
        
    def fetch_test_block_data(self):
        self._block_hash = "0000000000000000000c6ebd768d48ed96d4f1d8b5f7d8c2fcbf3d161cb2370d"
        self._version = 536870912
        self._previous_hash = "0000000000000000000c6ebd768d48ed96d4f1d8b5f7d8c2fcbf3d161cb2370d"
        self._merkle_root = "aafee9f0c5457b8e6e96d4c7257882c6e2b6d8a5cde2f4f30a8d010634577ad6"
        self._timestamp = 1632443035
        self._bits = 0x19015f53  
        self._target = self.decode_bits(self._bits)

    def hash(self):
        print(f"Hashing block with difficulty: {self._bits} (target: {self._target})")
        hash_as_int = int(self.block_hash_hex, 16)
        
        # Check if the hash meets the minimum target 
        if hash_as_int < self._target:
            print(f"Solved hash. Nonce: {self.nonce_attempt} | Hash: {self.block_hash_hex}")
            return True
        else:
            print(f"Unsolved hash. Nonce: {self.nonce_attempt} | Hash: {self.block_hash_hex}")
            return False 
        
    def create_coinbase_transaction(self, address):
        address = self.base58_to_hash160(address) # address must be converted to hash160    
        coinbase_script = b"clickMine.org"  # Arbitrary script for coinbase input
        coinbase_tx_id = b"\x00" * 32  # Coinbase has no input (null transaction ID)
        
        # Create the output script (P2PKH: Pay-to-PubKey-Hash)
        script_pubkey = b'\x76\xa9' + bytes([len(address)]) + address + b'\x88\xac'
        value = 50 * 10**8  # 50 BTC in satoshis
        coinbase_output = struct.pack("<Q", value) + bytes([len(script_pubkey)]) + script_pubkey

        # Assemble coinbase transaction
        coinbase_tx = (
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
        return coinbase_tx
    
    def create_block_with_coinbase(self, address):
        coinbase_tx = self.create_coinbase_transaction(address)
        self._merkle_root = hashlib.sha256(hashlib.sha256(coinbase_tx).digest()).hexdigest()  # Merkle root with one transaction
        
        if self.nonce_attempt:
            self.create_block_header(self.nonce_attempt)
        else:
            self.create_block_header(0)
            
    def submit_block_to_node(self):
        # TODO: block_hash_hex will be send to a core bitcoin node account via API
        pass  
        
    def get_data(self):
        return {
            "block_hash": self._block_hash,
            "version": self._version,
            "previous_hash": self._previous_hash,
            "merkle_root": self._merkle_root,
            "timestamp": self._timestamp,
            "bits": self._bits,
            "target": self._target,
            "nonce_attempt": self.nonce_attempt,
            "block_header": self.block_header.hex() if self.block_header else None,
            "block_hash_hex": self.block_hash_hex
        }

if __name__ == "__main__":
    NONCE_ATTEMPT = 12345
    ADDRESS = "1EcFVyggEmZuL3mjmfGQ7wDwryhEGA2Y4u"
    miner = Miner()
    #miner.fetch_block_data() 
    miner.fetch_test_block_data()
    miner.create_block_header(NONCE_ATTEMPT)
    
    if miner.hash(): 
        print(f"Solved hash. Nonce: {miner.nonce_attempt} | Hash: {miner.block_hash_hex}")
    else:
        print(f"Unsolved hash. Nonce: {miner.nonce_attempt} | Hash: {miner.block_hash_hex}")
