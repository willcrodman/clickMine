import hashlib
import struct
import requests

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
    miner = Miner()
    #miner.fetch_block_data() 
    miner.fetch_test_block_data()
    miner.create_block_header(NONCE_ATTEMPT)
    
    if miner.hash(): 
        print(f"Solved hash. Nonce: {miner.nonce_attempt} | Hash: {miner.block_hash_hex}")
    else:
        print(f"Unsolved hash. Nonce: {miner.nonce_attempt} | Hash: {miner.block_hash_hex}")
