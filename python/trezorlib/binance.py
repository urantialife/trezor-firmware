from . import messages
from .tools import expect, session


@expect(messages.BinanceAddress, field="address")
def get_address(client, address_n, show_display=False):
    return client.call(
        messages.BinanceGetAddress(address_n=address_n, show_display=show_display)
    )


@expect(messages.BinancePublicKey, field="public_key")
def get_public_key(client, address_n, show_display=False):
    return client.call(
        messages.BinanceGetPublicKey(address_n=address_n, show_display=show_display)
    )


@session
def sign_tx(client, address_n, tx_json):
    msg = tx_json["msgs"][0]
    envelope = messages.BinanceSignTx(
        msg_count=1,
        account_number=int(tx_json["account_number"]),
        chain_id=tx_json["chain_id"],
        memo=tx_json["memo"],
        sequence=int(tx_json["sequence"]),
        source=int(tx_json["source"]),
        address_n=address_n,
    )

    response = client.call(envelope)

    if not isinstance(response, messages.BinanceTxRequest):
        raise RuntimeError(
            "Invalid response, expected BinanceTxRequest, received "
            + type(response).__name__
        )

    msg_type = determine_message_type(msg)
    if msg_type == messages.MessageType.BinanceCancelMsg:
        msg = json_to_cancel_msg(msg)
    elif msg_type == messages.MessageType.BinanceOrderMsg:
        msg = json_to_order_msg(msg)
    elif msg_type == messages.MessageType.BinanceTransferMsg:
        msg = json_to_transfer_msg(msg)

    response = client.call(msg)

    if not isinstance(response, messages.BinanceSignedTx):
        raise RuntimeError(
            "Invalid response, expected BinanceSignedTx, received "
            + type(response).__name__
        )

    return response


def json_to_cancel_msg(json_msg):
    return messages.BinanceCancelMsg(
        refid=json_msg["refid"], sender=json_msg["sender"], symbol=json_msg["symbol"]
    )


def json_to_order_msg(json_msg):
    return messages.BinanceOrderMsg(
        id=json_msg["id"],
        ordertype=int(json_msg["ordertype"]),
        price=int(json_msg["price"]),
        quantity=int(json_msg["quantity"]),
        sender=json_msg["sender"],
        side=int(json_msg["side"]),
        symbol=json_msg["symbol"],
        timeinforce=int(json_msg["timeinforce"]),
    )


def json_to_transfer_msg(json_msg):
    json_inputs = json_msg["inputs"]
    inputs = []
    for txinput in json_inputs:
        input_coins = []
        for input_coin in txinput["coins"]:
            coin_msg = messages.BinanceCoin(
                int(input_coin["amount"]), input_coin["denom"]
            )
            input_coins.append(coin_msg)
        input_msg = messages.BinanceInputOutput(txinput["address"], input_coins)
        inputs.append(input_msg)

    json_outputs = json_msg["outputs"]
    outputs = []
    for txoutput in json_outputs:
        output_coins = []
        for output_coin in txoutput["coins"]:
            coin_msg = messages.BinanceCoin(
                int(output_coin["amount"]), output_coin["denom"]
            )
            output_coins.append(coin_msg)
        output_msg = messages.BinanceInputOutput(txoutput["address"], output_coins)
        outputs.append(output_msg)

    return messages.BinanceTransferMsg(inputs, outputs)


def determine_message_type(msg):
    if "refid" in msg:
        return messages.MessageType.BinanceCancelMsg
    elif "inputs" in msg:
        return messages.MessageType.BinanceTransferMsg
    elif "ordertype" in msg:
        return messages.MessageType.BinanceOrderMsg
    else:
        raise ValueError("unknown message type")
