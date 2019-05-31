from trezor.crypto.curve import nist256p1
from trezor.messages.OntologyGetPublicKey import OntologyGetPublicKey
from trezor.messages.OntologyPublicKey import OntologyPublicKey

from .helpers import CURVE, validate_full_path

from apps.common import layout, seed

async def get_public_key(ctx, msg: OntologyGetPublicKey, keychain):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)

    node = keychain.derive(msg.address_n)
    seckey = node.private_key()
    public_key = nist256p1.publickey(seckey, True)

    if msg.show_display:
        await layout.show_pubkey(ctx, public_key)

    return OntologyPublicKey(public_key=public_key)
