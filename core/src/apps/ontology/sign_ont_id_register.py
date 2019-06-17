from trezor import wire
from trezor.crypto.hashlib import sha256
from trezor.messages.OntologySignedOntIdRegister import OntologySignedOntIdRegister
from trezor.messages.OntologySignOntIdRegister import OntologySignOntIdRegister
from trezor.utils import HashWriter

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_ont_id_register
from .serialize import serialize_ont_id_register, serialize_tx
from .sign import sign

from apps.common import paths


async def sign_ont_id_register(ctx, msg: OntologySignOntIdRegister, keychain):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)
    if msg.transaction.type == 0xD1:
        await require_confirm_ont_id_register(
            ctx, msg.ont_id_register.ont_id, msg.ont_id_register.public_key
        )
    else:
        raise wire.DataError("Invalid transaction type")

    node = keychain.derive(msg.address_n, CURVE)
    hw = HashWriter(sha256())
    serialized_payload = serialize_ont_id_register(msg.ont_id_register)
    serialize_tx(msg.transaction, serialized_payload, hw)
    signature = await sign(hw.get_digest(), node.private_key())

    return OntologySignedOntIdRegister(signature=signature, payload=serialized_payload)
