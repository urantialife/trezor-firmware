from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.messages import MessageType
from trezor.messages.BinanceSignedTx import BinanceSignedTx
from trezor.messages.BinanceTxRequest import BinanceTxRequest

from apps.binance import CURVE, helpers, layout
from apps.common import paths


async def sign_tx(ctx, envelope, keychain):
    # create transaction message -> sign it -> create signature/pubkey message -> serialize all
    await paths.validate_path(
        ctx, helpers.validate_full_path, keychain, envelope.address_n, CURVE
    )

    node = keychain.derive(envelope.address_n)

    tx_req = BinanceTxRequest()

    msg = await ctx.call(
        tx_req,
        MessageType.BinanceCancelMsg,
        MessageType.BinanceOrderMsg,
        MessageType.BinanceTransferMsg,
    )

    msg_json = helpers.produce_json_for_signing(envelope, msg)
    signature_bytes = generate_content_signature(msg_json.encode(), node.private_key())

    if msg.MESSAGE_WIRE_TYPE == MessageType.BinanceTransferMsg:
        for txinput in msg.inputs:
            for coin in txinput.coins:
                await layout.require_confirm_transfer(
                    ctx, txinput.address, coin.amount, coin.denom
                )
        for output in msg.outputs:
            for coin in output.coins:
                await layout.require_confirm_transfer(
                    ctx, output.address, coin.amount, coin.denom
                )
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceOrderMsg:
        await layout.require_confirm_order_side(ctx, msg.side)
        await layout.require_confirm_order_address(ctx, msg.sender)
        await layout.require_confirm_order_details(ctx, msg.quantity, msg.price)
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceCancelMsg:
        await layout.require_confirm_cancel(ctx, msg.refid)
    else:
        raise ValueError("input message unrecognized, is of type " + type(msg).__name__)

    return BinanceSignedTx(
        signature=signature_bytes, public_key=node.public_key(), json=msg_json
    )


def generate_content_signature(json: bytes, private_key: bytes) -> bytes:
    msghash = sha256(json).digest()
    return secp256k1.sign(private_key, msghash)[1:65]


def verify_content_signature(
    public_key: bytes, signature: bytes, unsigned_data: bytes
) -> bool:
    msghash = sha256(unsigned_data).digest()
    return secp256k1.verify(public_key, signature, msghash)
