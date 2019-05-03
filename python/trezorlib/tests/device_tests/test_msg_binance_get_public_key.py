import pytest

from trezorlib import binance, debuglink
from trezorlib.tools import parse_path

from .common import TrezorTest

BINANCE_PATH = parse_path("m/44h/714h/0h/0/0")


@pytest.mark.binance
@pytest.mark.skip_t1  # T1 support is not planned
class TestMsgBinanceGetPublicKey(TrezorTest):
    def test_binance_get_public_key(self):
        debuglink.load_device_by_mnemonic(
            self.client,
            mnemonic="offer caution gift cross surge pretty orange during eye soldier popular holiday mention east eight office fashion ill parrot vault rent devote earth cousin",
            pin="",
            passphrase_protection=False,
            label="test",
            language="english",
        )
        sig = binance.get_public_key(self.client, BINANCE_PATH)
        assert (
            sig.hex()
            == "029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e"
        )
