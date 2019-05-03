from micropython import const

from trezor.crypto import bech32
from trezor.crypto.hashlib import ripemd160, sha256
from trezor.messages import MessageType
from trezor.messages.BinanceCancelMsg import BinanceCancelMsg
from trezor.messages.BinanceOrderMsg import BinanceOrderMsg
from trezor.messages.BinanceSignTx import BinanceSignTx
from trezor.messages.BinanceTransferMsg import BinanceTransferMsg

from apps.common import HARDENED

ENVELOPE_BLUEPRINT = '{{"account_number":"{account_number}","chain_id":"{chain_id}","data":null,"memo":"{memo}","msgs":[{msgs}],"sequence":"{sequence}","source":"{source}"}}'
MSG_TRANSFER_BLUEPRINT = '{{"inputs":[{inputs}],"outputs":[{outputs}]}}'
MSG_NEWORDER_BLUEPRINT = '{{"id":"{id}","ordertype":{ordertype},"price":{price},"quantity":{quantity},"sender":"{sender}","side":{side},"symbol":"{symbol}","timeinforce":{timeinforce}}}'
MSG_CANCEL_BLUEPRINT = '{{"refid":"{refid}","sender":"{sender}","symbol":"{symbol}"}}'
INPUT_OUTPUT_BLUEPRINT = '{{"address":"{address}","coins":[{coins}]}}'
COIN_BLUEPRINT = '{{"amount":"{amount}","denom":"{denom}"}}'

DIVISIBILITY = const(
    18
)  # 1*10^18 Jagers equal 1 BNB https://www.binance.vision/glossary/jager


def produce_json_for_signing(envelope: BinanceSignTx, msg) -> str:
    if msg.MESSAGE_WIRE_TYPE == MessageType.BinanceTransferMsg:
        json_msg = produce_transfer_json(msg)
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceOrderMsg:
        json_msg = produce_neworder_json(msg)
    elif msg.MESSAGE_WIRE_TYPE == MessageType.BinanceCancelMsg:
        json_msg = produce_cancel_json(msg)
    else:
        raise ValueError("input message unrecognized, is of type " + type(msg).__name__)

    if envelope.source is None or envelope.source <= 0:
        source = 0
    else:
        source = envelope.source

    return ENVELOPE_BLUEPRINT.format(
        account_number=envelope.account_number,
        chain_id=envelope.chain_id,
        memo=envelope.memo,
        msgs=json_msg,
        sequence=envelope.sequence,
        source=source,
    )


def produce_transfer_json(msg: BinanceTransferMsg) -> str:
    inputs = ""
    for count, txinput in enumerate(msg.inputs, 1):
        coins = ""
        for coincount, coin in enumerate(txinput.coins, 1):
            coin_json = COIN_BLUEPRINT.format(amount=coin.amount, denom=coin.denom)
            coins = coins + coin_json
            if coincount < len(txinput.coins):
                coins = coins + ","
        input_json = INPUT_OUTPUT_BLUEPRINT.format(address=txinput.address, coins=coins)
        inputs = inputs + input_json
        if count < len(msg.inputs):
            inputs = inputs + ","

    outputs = ""
    for count, txoutput in enumerate(msg.outputs, 1):
        coins = ""
        for coincount, coin in enumerate(txoutput.coins, 1):
            coin_json = COIN_BLUEPRINT.format(amount=coin.amount, denom=coin.denom)
            coins = coins + coin_json
            if coincount < len(txoutput.coins):
                coins = coins + ","
        output_json = INPUT_OUTPUT_BLUEPRINT.format(
            address=txoutput.address, coins=coins
        )
        outputs = outputs + output_json
        if count < len(msg.outputs):
            outputs = outputs + ","

    return MSG_TRANSFER_BLUEPRINT.format(inputs=inputs, outputs=outputs)


def produce_neworder_json(msg: BinanceOrderMsg) -> str:
    return MSG_NEWORDER_BLUEPRINT.format(
        id=msg.id,
        ordertype=msg.ordertype,
        price=msg.price,
        quantity=msg.quantity,
        sender=msg.sender,
        side=msg.side,
        symbol=msg.symbol,
        timeinforce=msg.timeinforce,
    )


def produce_cancel_json(msg: BinanceCancelMsg) -> str:
    return MSG_CANCEL_BLUEPRINT.format(
        refid=msg.refid, sender=msg.sender, symbol=msg.symbol
    )


def address_from_public_key(pubkey: bytes, hrp: str) -> str:
    """
    Address = RIPEMD160(SHA256(compressed public key))
    Address_Bech32 = HRP + '1' + bech32.encode(convert8BitsTo5Bits(RIPEMD160(SHA256(compressed public key))))
    HRP - bnb for productions, tbnb for tests
    """

    h = sha256(pubkey).digest()
    h = ripemd160(h).digest()

    convertedbits = bech32.convertbits(h, 8, 5, False)

    return bech32.bech32_encode(hrp, convertedbits)


def validate_full_path(path: list) -> bool:
    """
    Validates derivation path to equal 44'/714'/a'/0/0,
    where `a` is an account index from 0 to 1 000 000.
    Similar to Ethereum this should be 44'/714'/a', but for
    compatibility with other HW vendors we use 44'/714'/a'/0/0.
    """
    if len(path) != 5:
        return False
    if path[0] != 44 | HARDENED:
        return False
    if path[1] != 714 | HARDENED:
        return False
    if path[2] < HARDENED or path[2] > 1000000 | HARDENED:
        return False
    if path[3] != 0:
        return False
    if path[4] != 0:
        return False
    return True
