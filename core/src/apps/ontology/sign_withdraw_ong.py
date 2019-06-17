from trezor import wire
from trezor.crypto.hashlib import sha256
from trezor.messages.OntologySignedWithdrawOng import OntologySignedWithdrawOng
from trezor.messages.OntologySignWithdrawOng import OntologySignWithdrawOng
from trezor.utils import HashWriter

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_withdraw_ong
from .serialize import serialize_tx, serialize_withdraw_ong
from .sign import sign

from apps.common import paths


async def sign_withdraw_ong(ctx, msg: OntologySignWithdrawOng, keychain):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)
    if msg.transaction.type == 0xD1:
        await require_confirm_withdraw_ong(ctx, msg.withdraw_ong.amount)
    else:
        raise wire.DataError("Invalid transaction type")

    node = keychain.derive(msg.address_n, CURVE)
    hw = HashWriter(sha256())
    serialized_payload = serialize_withdraw_ong(msg.withdraw_ong)
    serialize_tx(msg.transaction, serialized_payload, hw)
    signature = await sign(hw.get_digest(), node.private_key())

    return OntologySignedWithdrawOng(signature=signature, payload=serialized_payload)
