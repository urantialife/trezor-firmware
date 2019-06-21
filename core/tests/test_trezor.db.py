from common import *

from trezor import io
from trezor.db import DB


class TestTrezorDb(unittest.TestCase):

    def setUp(self):
        self.sd = io.SDCard()
        self.sd.power(True)
        self.fs = io.FatFS()
        self.fs.mkfs()
        self.sd.power(False)

    def test_put_get(self):
        db = DB("test1")
        data = [-23, b"b", {"f1": 1337, "f2": b"b", "f3": "s", "f": True}, "s", False]
        db.put(b"key", data)
        self.assertEqual(db.get(b"key"), data)

    def test_put_del_get(self):
        db = DB("test2")
        db.put(b"key", b"value")
        db.delete(b"key")
        with self.assertRaises(KeyError):
            db.get(b"key")

if __name__ == '__main__':
    unittest.main()
