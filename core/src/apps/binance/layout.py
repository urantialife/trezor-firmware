from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.ui.text import Text
from trezor.utils import format_amount

from . import helpers

from apps.common.confirm import hold_to_confirm, require_confirm
from apps.common.layout import split_address


async def require_confirm_transfer(ctx, to, value, denom):
    text = Text("Confirm sending", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold(format_amount(value, helpers.DIVISIBILITY) + " " + denom)
    text.normal("to")
    text.mono(*split_address(to))
    return await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)


async def require_confirm_cancel(ctx, refid):
    text = Text("Confirm cancel", ui.ICON_SEND, icon_color=ui.GREEN)
    text.normal("Reference id:")
    text.bold(refid)
    return await hold_to_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_order_side(ctx, side):
    text = Text("Confirm order side", ui.ICON_SEND, icon_color=ui.GREEN)
    if side == 1:
        text.bold("buy")
    elif side == 2:
        text.bold("sell")
    return await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)


async def require_confirm_order_details(ctx, quantity, price):
    text = Text("Confirm order", ui.ICON_SEND, icon_color=ui.GREEN)
    text.normal("Quantity:")
    text.bold(str(quantity))
    text.normal("Price:")
    text.bold(str(price))
    return await hold_to_confirm(ctx, text, ButtonRequestType.ConfirmOutput)


async def require_confirm_order_address(ctx, address):
    text = Text("Confirm order sender", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold(address)
    return await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)
