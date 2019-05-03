import pytest

from trezorlib import debuglink
from trezorlib.binance import get_address
from trezorlib.tools import parse_path

from .common import TrezorTest


@pytest.mark.binance
@pytest.mark.skip_t1  # T1 support is not planned
class TestMsgBinanceGetAddress(TrezorTest):
    def test_binance_get_address(self):
        # data from https://github.com/binance-chain/javascript-sdk/blob/master/__tests__/crypto.test.js#L50
        debuglink.load_device_by_mnemonic(
            self.client,
            mnemonic="offer caution gift cross surge pretty orange during eye soldier popular holiday mention east eight office fashion ill parrot vault rent devote earth cousin",
            pin="",
            passphrase_protection=False,
            label="test",
            language="english",
        )
        address = get_address(self.client, parse_path("m/44'/714'/0'/0/0"))
        assert address == "tbnb1hgm0p7khfk85zpz5v0j8wnej3a90w709zzlffd"
        address = get_address(self.client, parse_path("m/44'/714'/0'/0/1"))
        assert address == "tbnb1egswqkszzfc2uq78zjslc6u2uky4pw46gq25tu"
