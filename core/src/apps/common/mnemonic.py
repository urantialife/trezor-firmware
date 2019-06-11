from trezor import ui, workflow
from trezor.crypto import bip39

from apps.common import storage

if False:
    from typing import List, Tuple

TYPE_BIP39 = 0


def get() -> Tuple[bytes, int]:
    mnemonic_secret = storage.get_mnemonic_secret()
    mnemonic_type = storage.get_mnemonic_type() or TYPE_BIP39
    return mnemonic_secret, mnemonic_type


def get_seed(passphrase: str = "", progress_bar: bool = True) -> bytes:
    secret, mnemonic_type = get()
    if mnemonic_type == TYPE_BIP39:
        module = bip39
    if progress_bar:
        _start_progress()
        result = module.seed(secret.decode(), passphrase, _render_progress)
        _stop_progress()
    else:
        result = module.seed(secret.decode(), passphrase)
    return result


def process(mnemonics: List[str], mnemonic_type: int) -> bytes:
    if mnemonic_type == TYPE_BIP39:
        return mnemonics[0].encode()
    else:
        raise RuntimeError("Unknown mnemonic type")


def restore() -> str:
    secret, mnemonic_type = get()
    if mnemonic_type == TYPE_BIP39:
        return secret.decode()
    else:
        raise RuntimeError("Unknown mnemonic type")


def _start_progress() -> None:
    ui.backlight_fade(ui.BACKLIGHT_DIM)
    ui.display.clear()
    ui.header("Please wait")
    ui.display.refresh()
    ui.backlight_fade(ui.BACKLIGHT_NORMAL)


def _render_progress(progress: int, total: int) -> None:
    p = 1000 * progress // total
    ui.display.loader(p, False, 18, ui.WHITE, ui.BG)
    ui.display.refresh()


def _stop_progress() -> None:
    workflow.restartdefault()
