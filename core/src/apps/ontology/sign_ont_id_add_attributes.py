from trezor import wire
from trezor.messages.OntologyOntIdAddAttributes import OntologyOntIdAddAttributes
from trezor.messages.OntologyTransaction import OntologyTransaction

from .helpers import CURVE, validate_full_path
from .layout import require_confirm_ont_id_add_attributes
from .serialize import serialize_ont_id_add_attributes
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
    await _require_confirm(ctx, msg.transaction, msg.ont_id_add_attributes)

    node = keychain.derive(msg.address_n, CURVE)
    [raw_data, payload] = serialize_ont_id_add_attributes(
        msg.transaction, msg.ont_id_add_attributes
    )
    signature = await sign(raw_data, node.private_key())

    return OntologySignedOntIdAddAttributes(signature=signature, payload=payload)


async def _require_confirm(
    ctx, transaction: OntologyTransaction, add: OntologyOntIdAddAttributes
):
    if transaction.type == 0xD1:
        return await require_confirm_ont_id_add_attributes(
            ctx, add.ont_id, add.public_key, add.ont_id_attributes
        )

    raise wire.DataError("Invalid transaction type")
