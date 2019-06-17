from trezor import wire
from trezor.crypto.hashlib import sha256
from trezor.utils import HashWriter

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_ont_id_add_attributes
from .serialize import serialize_ont_id_add_attributes, serialize_tx
from .sign import sign

from apps.common import paths

from trezor.messages.OntologySignedOntIdAddAttributes import (  # isort:skip
    OntologySignedOntIdAddAttributes,
)
from trezor.messages.OntologySignOntIdAddAttributes import (  # isort:skip
    OntologySignOntIdAddAttributes,
)


async def sign_ont_id_add_attributes(
    ctx, msg: OntologySignOntIdAddAttributes, keychain
):
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)
    if msg.transaction.type == 0xD1:
        await require_confirm_ont_id_add_attributes(
            ctx,
            msg.ont_id_add_attributes.ont_id,
            msg.ont_id_add_attributes.public_key,
            msg.ont_id_add_attributes.ont_id_attributes,
        )
    else:
        raise wire.DataError("Invalid transaction type")

    node = keychain.derive(msg.address_n, CURVE)
    hw = HashWriter(sha256())
    serialized_payload = serialize_ont_id_add_attributes(msg.ont_id_add_attributes)
    serialize_tx(msg.transaction, serialized_payload, hw)
    signature = await sign(hw.get_digest(), node.private_key())

    return OntologySignedOntIdAddAttributes(
        signature=signature, payload=serialized_payload
    )
