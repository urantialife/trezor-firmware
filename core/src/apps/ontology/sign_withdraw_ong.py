from trezor import wire
from trezor.messages.OntologySignedWithdrawOng import OntologySignedWithdrawOng
from trezor.messages.OntologySignWithdrawOng import OntologySignWithdrawOng
from trezor.messages.OntologyTransaction import OntologyTransaction
from trezor.messages.OntologyWithdrawOng import OntologyWithdrawOng

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_withdraw_ong
from .serialize import serialize_withdraw_ong
from .sign import sign

from apps.common import paths


async def sign_withdraw_ong(ctx, msg: OntologySignWithdrawOng, keychain):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)
    if msg.transaction.type == 0xD1:
        await require_confirm_withdraw_ong(ctx, msg.withdraw_ong.amount)
    else:
        raise wire.DataError("Invalid transaction type")

    node = keychain.derive(msg.address_n, CURVE)
    [raw_data, payload] = serialize_withdraw_ong(msg.transaction, msg.withdraw_ong)
    signature = await sign(raw_data, node.private_key())

    return OntologySignedWithdrawOng(signature=signature, payload=payload)
