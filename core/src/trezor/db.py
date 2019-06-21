from ubinascii import hexlify

from trezor import io
from trezor.crypto import chacha20poly1305, random
from trezor.crypto.hashlib import sha256

from apps.common import cbor


class DB:
    def __init__(self, name: str):
        self.MAGIC = b"TRDB"
        self.VERSION = 1
        self.sd = io.SDCard()
        self.sd.power(True)
        self.fs = io.FatFS()
        self.fs.mount()
        try:
            self.fs.mkdir("/trezor")
        except OSError:
            pass
        self.dir = "/trezor/%s" % name
        try:
            self.fs.mkdir(self.dir)
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fs.unmount()
        self.sd.power(False)

    def _key_to_fname(self, key: bytes) -> str:
        h = hexlify(sha256(key).digest()).decode()
        fn = "%s/%s.trdb" % (self.dir, h)
        return fn

    def get(self, key: bytes) -> object:
        try:
            s = self.fs.stat(self._key_to_fname(key))
        except OSError:
            raise KeyError
        buf = bytearray(s[0])
        with self.fs.open(self._key_to_fname(key), "r") as f:
            f.read(buf)
        if buf[:4] != self.MAGIC:
            raise ValueError("Invalid magic")
        if buf[4:8] != self.VERSION.to_bytes(4, "big"):
            raise ValueError("Invalid version")
        enckey = b" " * 32  # TODO: replace with proper key
        nonce = buf[8:20]
        ctx = chacha20poly1305(enckey, nonce)
        ctx.auth(self.MAGIC)  # TODO: Is this enough?
        dec = ctx.decrypt(buf[20:-16])
        tag = ctx.finish()
        if tag != buf[-16:]:
            raise ValueError("Invalid MAC")
        data = cbor.decode(dec)
        return data

    def put(self, key: bytes, data: object) -> None:
        enckey = b" " * 32  # TODO: replace with proper key
        nonce = random.bytes(12)
        ctx = chacha20poly1305(enckey, nonce)
        ctx.auth(self.MAGIC)  # TODO: Is this enough?
        enc = ctx.encrypt(cbor.encode(data))
        tag = ctx.finish()
        with self.fs.open(self._key_to_fname(key), "w") as f:
            f.write(self.MAGIC)
            f.write(self.VERSION.to_bytes(4, "big"))
            f.write(nonce)
            f.write(enc)
            f.write(tag)

    def delete(self, key: bytes) -> None:
        self.fs.unlink(self._key_to_fname(key))
