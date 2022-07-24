import badger2040
from ahlcg2040.data import Faction, faction_icons
from badger_ui.base import Widget, WidgetMixin
from badger_ui.util import Offset, Size


class FactionTab(Widget):
  def __init__(self, parent: WidgetMixin, size: Size, offset: Offset = None):
    super().__init__(parent, size, offset)

    self.icons = faction_icons
    self.selected_index = 0

  def on_button(self, pressed: dict[int, bool]):
    if pressed[badger2040.BUTTON_A]:
      self.selected_index = (self.selected_index - 1) % len(Faction.values)
      return True
    elif pressed[badger2040.BUTTON_C]:
      self.selected_index = (self.selected_index + 1) % len(Faction.values)
      return True

    return super().on_button(pressed)

  def render(self):
    super().render()

    count = self.icons.count // 2
    offset = self.display_offset + Offset((self.size.width - (self.icons.size * count)) // 2, 0)
    for i in range(count):
      icon_offset = offset + Offset(self.icons.size * i, 0)
      self.icons.icon(
          display=self.display,
          icon_index=i + count if i == self.selected_index else i,
          offset=icon_offset,
      )