import os
import hashlib
import base58
from ecdsa import SigningKey, SECP256k1
import json
class Wallet:
    def __init__(self):
        self.private_key_hex = None
        self.public_key_hex = None
        self.bitcoin_address = None
    
    def generate_wallet(self):
        # Generate a private key (32 bytes)
        private_key = os.urandom(32)
        self.private_key_hex = private_key.hex()
        
        # Generate a public key from the private key
        signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
        verifying_key = signing_key.verifying_key
        public_key = b'\x04' + verifying_key.to_string()  # Add prefix 0x04 for uncompressed key
        
        # Perform SHA-256 hashing on the public key
        sha256_pub_key = hashlib.sha256(public_key).digest()
        
        # Perform RIPEMD-160 hashing on the SHA-256 result
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_pub_key)
        public_key_hash = ripemd160.digest()
        
        # Add Bitcoin network byte (0x00 for Mainnet)
        network_byte = b'\x00' + public_key_hash
        
        # Perform double SHA-256 hashing on the extended hash
        checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
        
        # Append checksum to the extended hash
        address_bytes = network_byte + checksum
        
        # Encode the result in Base58
        self.bitcoin_address = base58.b58encode(address_bytes).decode('utf-8')
        
        # Convert public key to hex format for convenience
        self.public_key_hex = public_key.hex()

    def get_dict(self):
        return  {
            "private_key": self.private_key_hex,
            "public_key": self.public_key_hex,
            "bitcoin_address": self.bitcoin_address
        }

if __name__ == "__main__":
    wallet = Wallet()
    wallet.generate_wallet()
    
    print("Private Key:", wallet.private_key_hex)
    print("Public Key:", wallet.public_key_hex)
    print("Bitcoin Address:", wallet.bitcoin_address)
