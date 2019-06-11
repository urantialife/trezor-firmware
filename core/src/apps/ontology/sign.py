from trezor.crypto.curve import nist256p1
from trezor.crypto.hashlib import sha256


async def sign(raw_data: bytes, private_key: bytes) -> bytes:
    """
    Creates signature for data
    """
    data_hash = sha256(sha256(sha256(raw_data).digest()).digest()).digest()

    signature = nist256p1.sign(private_key, data_hash, False)
    signature = b"\x01" + signature[1:65]  # first byte of transaction is 0x01
    return signature
