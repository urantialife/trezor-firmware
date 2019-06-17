from trezor import wire
from trezor.crypto.hashlib import sha256
from trezor.messages import OntologyAsset
from trezor.messages.OntologySignedTransfer import OntologySignedTransfer
from trezor.messages.OntologySignTransfer import OntologySignTransfer
from trezor.utils import HashWriter

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_transfer_ong, require_confirm_transfer_ont
from .serialize import serialize_transfer, serialize_tx
from .sign import sign

from apps.common import paths


async def sign_transfer(ctx, msg: OntologySignTransfer, keychain):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)
    if msg.transaction.type == 0xD1:
        if msg.transfer.asset == OntologyAsset.ONT:
            await require_confirm_transfer_ont(
                ctx, msg.transfer.to_address, msg.transfer.amount
            )
        if msg.transfer.asset == OntologyAsset.ONG:
            await require_confirm_transfer_ong(
                ctx, msg.transfer.to_address, msg.transfer.amount
            )
    else:
        raise wire.DataError("Invalid transaction type")

    node = keychain.derive(msg.address_n, CURVE)
    hw = HashWriter(sha256())
    serialized_payload = serialize_transfer(msg.transfer)
    serialize_tx(msg.transaction, serialized_payload, hw)
    signature = await sign(hw.get_digest(), node.private_key())

    return OntologySignedTransfer(signature=signature, payload=serialized_payload)
