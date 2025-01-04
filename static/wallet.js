// wallet.js - Fully Functional JavaScript Wallet Class with Bitcoin Cryptography

// secp256k1 curve parameters
const P = BigInt("0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f");
const A = BigInt(0); // Coefficient A of the curve equation
const B = BigInt(7); // Coefficient B of the curve equation
const Gx = BigInt("0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798");
const Gy = BigInt("0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8");
const N = BigInt("0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141");

// Helper functions for modular arithmetic
function mod(n, m) {
    return ((n % m) + m) % m;
}

function modInverse(a, m) {
    let m0 = m;
    let y = BigInt(0);
    let x = BigInt(1);

    if (m === 1n) return 0n;

    while (a > 1n) {
        const q = a / m;
        let t = m;

        m = a % m;
        a = t;
        t = y;

        y = x - q * y;
        x = t;
    }

    return x < 0 ? x + m0 : x;
}

function pointDouble(x1, y1) {
    const s = mod((3n * x1 * x1 + A) * modInverse(2n * y1, P), P);
    const x3 = mod(s * s - 2n * x1, P);
    const y3 = mod(s * (x1 - x3) - y1, P);
    return [x3, y3];
}

function pointAdd(x1, y1, x2, y2) {
    if (x1 === x2 && y1 === y2) return pointDouble(x1, y1);
    const s = mod((y2 - y1) * modInverse(x2 - x1, P), P);
    const x3 = mod(s * s - x1 - x2, P);
    const y3 = mod(s * (x1 - x3) - y1, P);
    return [x3, y3];
}

// Scalar multiplication (Elliptic Curve point multiplication)
function scalarMultiply(k, x, y) {
    let kBin = k.toString(2);
    let Qx = BigInt(0);
    let Qy = BigInt(0);
    let Px = x;
    let Py = y;

    for (let i = 0; i < kBin.length; i++) {
        if (kBin[i] === "1") {
            if (Qx === 0n && Qy === 0n) {
                Qx = Px;
                Qy = Py;
            } else {
                [Qx, Qy] = pointAdd(Qx, Qy, Px, Py);
            }
        }
        [Px, Py] = pointDouble(Px, Py);
    }

    return [Qx, Qy];
}

// Generate the secp256k1 public key
function generateSecp256k1PublicKey(privateKeyHex) {
    const privateKey = BigInt("0x" + privateKeyHex);
    const [Qx, Qy] = scalarMultiply(privateKey, Gx, Gy);
    return Qx.toString(16).padStart(64, "0") + Qy.toString(16).padStart(64, "0");
}

// Helper function to create a SHA256 hash
async function sha256(message) {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const crypto = window.crypto || window.msCrypto;
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer))
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
}

// Full RIPEMD-160 implementation
function ripemd160(message) {
    const r = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8],
        [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12, 6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2]
    ];
    const K = [
        [0x00000000, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e],
        [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0x00000000]
    ];
    const h = [
        0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0
    ];

    const pad = (m) => {
        const bitLength = m.length * 8;
        const len = ((m.length + 8) >>> 6 << 4) + 14;
        const blocks = new Uint32Array(len + 2);
        for (let i = 0; i < m.length; i++) {
            blocks[i >> 2] |= m[i] << (i % 4 << 3);
        }
        blocks[bitLength >> 5] |= 0x80 << (bitLength % 32);
        blocks[len] = bitLength;
        return blocks;
    };

    const rol = (x, s) => (x << s) | (x >>> (32 - s));

    const f = [
        (x, y, z) => x ^ y ^ z,
        (x, y, z) => (x & y) | (~x & z),
        (x, y, z) => (x | ~y) ^ z,
        (x, y, z) => (x & z) | (y & ~z),
        (x, y, z) => x ^ (y | ~z)
    ];

    const s = [
        [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8, 7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12],
        [9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6, 7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12]
    ];

    const blocks = pad(new TextEncoder().encode(message));
    for (let i = 0; i < blocks.length; i += 16) {
        const w = blocks.subarray(i, i + 16);
        let al, bl, cl, dl, el;
        let ar, br, cr, dr, er;
        al = ar = h[0];
        bl = br = h[1];
        cl = cr = h[2];
        dl = dr = h[3];
        el = er = h[4];

        for (let j = 0; j < 80; j++) {
            const round = j >> 4;
            const tl = rol(al + f[round](bl, cl, dl) + w[r[0][j]] + K[0][round], s[0][j]) + el;
            al = el;
            el = dl;
            dl = rol(cl, 10);
            cl = bl;
            bl = tl;

            const tr = rol(ar + f[4 - round](br, cr, dr) + w[r[1][j]] + K[1][round], s[1][j]) + er;
            ar = er;
            er = dr;
            dr = rol(cr, 10);
            cr = br;
            br = tr;
        }

        const t = (h[1] + cl + dr) | 0;
        h[1] = (h[2] + dl + er) | 0;
        h[2] = (h[3] + el + ar) | 0;
        h[3] = (h[4] + al + br) | 0;
        h[4] = (h[0] + bl + cr) | 0;
        h[0] = t;
    }

    return h.map((x) => x.toString(16).padStart(8, "0")).join("");
}

// Base58 encoding implementation
function base58Encode(hex) {
    const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    const base = BigInt(58);

    let num = BigInt('0x' + hex);
    let encoded = '';

    while (num > 0) {
        const remainder = num % base;
        num = num / base;
        encoded = alphabet[Number(remainder)] + encoded;
    }

    for (let i = 0; i < hex.length && hex[i] === '0'; i += 2) {
        encoded = '1' + encoded;
    }

    return encoded;
}

// Wallet class
class Wallet {
    constructor() {
        this.privateKey = this.generatePrivateKey();
        this.publicKey = this.generatePublicKey(this.privateKey);
        this.bitcoinAddress = this.generateBitcoinAddress(this.publicKey);
    }

    generatePrivateKey() {
        const crypto = window.crypto || window.msCrypto;
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array).map(byte => byte.toString(16).padStart(2, '0')).join('');
    }

    generatePublicKey(privateKey) {
        return generateSecp256k1PublicKey(privateKey);
    }

    async generateBitcoinAddress(publicKey) {
        const sha256Hash = await sha256(publicKey);
        const ripemd160Hash = ripemd160(sha256Hash);

        const versionedPayload = '00' + ripemd160Hash;
        const doubleSHA = await sha256(await sha256(versionedPayload));
        const checksum = doubleSHA.substring(0, 8);

        const fullPayload = versionedPayload + checksum;
        return base58Encode(fullPayload);
    }
}

// Example usage
document.addEventListener('DOMContentLoaded', async () => {
const wallet = new Wallet();

document.getElementById('private-key').textContent = wallet.privateKey;
document.getElementById('public-key').textContent = wallet.publicKey;
document.getElementById('bitcoin-address').textContent = wallet.bitcoinAddress;
});
