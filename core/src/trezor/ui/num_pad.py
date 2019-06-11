from micropython import const

from trezor import res, ui
from trezor.ui.button import Button, ButtonMono, ButtonMonoDark

if False:
    from typing import List

_ITEMS_PER_PAGE = const(10)
_BACK_BUTTON_POSITION = const(9)
_PLUS_BUTTON_POSITION = const(11)


class NumPad(ui.Layout):
    def __init__(self, label: str, start: int, end: int) -> None:
        """
        Generates a numpad with numbers from `start` to `end` excluding.
        """
        self.label = label
        self.start = start
        self.end = end
        self.page = 0
        self.buttons = generate_buttons(self.start, self.end, self.page, self)

    def dispatch(self, event: int, x: int, y: int) -> None:
        for button in self.buttons:
            button.dispatch(event, x, y)
        if event is ui.RENDER:
            # render header label
            ui.display.text_center(
                ui.WIDTH // 2, 36, self.label, ui.BOLD, ui.GREY, ui.BG
            )

    def on_back(self) -> None:
        self.page -= 1
        self.buttons = generate_buttons(self.start, self.end, self.page, self)
        ui.display.clear()  # we need to clear old buttons

    def on_plus(self) -> None:
        self.page += 1
        self.buttons = generate_buttons(self.start, self.end, self.page, self)
        ui.display.clear()  # we need to clear old buttons

    def on_select(self, number: int) -> None:
        raise ui.Result(number)


class NumButton(Button):
    def __init__(self, index: int, digit: int, pad: NumPad):
        self.pad = pad
        area = ui.grid(index + 3)  # skip the first line
        super().__init__(area, str(digit), ButtonMono)

    def on_click(self) -> None:
        self.pad.on_select(int(self.text))


def generate_buttons(start: int, end: int, page: int, pad: NumPad) -> List[Button]:
    start = start + (_ITEMS_PER_PAGE + 1) * page - page
    end = min(end, (_ITEMS_PER_PAGE + 1) * (page + 1) - page)
    digits = list(range(start, end))

    buttons = [NumButton(i, d, pad) for i, d in enumerate(digits)]  # type: List[Button]

    area = ui.grid(_PLUS_BUTTON_POSITION + 3)
    plus = Button(area, str(end) + "+", ButtonMonoDark)
    plus.on_click = pad.on_plus  # type: ignore

    area = ui.grid(_BACK_BUTTON_POSITION + 3)
    back = Button(area, res.load(ui.ICON_BACK), ButtonMonoDark)
    back.on_click = pad.on_back  # type: ignore

    if len(digits) == _ITEMS_PER_PAGE:
        # move the tenth button to its proper place and make place for the back button
        buttons[-1].area = ui.grid(_PLUS_BUTTON_POSITION - 1 + 3)
        buttons.append(plus)

    if page == 0:
        back.disable()
    buttons.append(back)

    return buttons
