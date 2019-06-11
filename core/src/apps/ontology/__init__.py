from trezor import wire
from trezor.messages import MessageType

from apps.common import HARDENED

CURVE = "nist256p1"


def boot():
    ns = [
        [CURVE, HARDENED | 44, HARDENED | 1024],
        [CURVE, HARDENED | 44, HARDENED | 888],
    ]
    wire.add(MessageType.OntologyGetPublicKey, __name__, "get_public_key", ns)
    wire.add(MessageType.OntologyGetAddress, __name__, "get_address", ns)
    wire.add(MessageType.OntologySignTransfer, __name__, "sign_transfer", ns)
    wire.add(MessageType.OntologySignWithdrawOng, __name__, "sign_withdraw_ong", ns)
    wire.add(
        MessageType.OntologySignOntIdRegister, __name__, "sign_ont_id_register", ns
    )
    wire.add(
        MessageType.OntologySignOntIdAddAttributes,
        __name__,
        "sign_ont_id_add_attributes",
        ns,
    )
