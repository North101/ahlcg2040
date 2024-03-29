import badger2040w
from ahlcg2040.data import investigator_data
from badger_ui import App, Offset, Size, Widget
from badger_ui.list import ListWidget

from .faction_tab import FactionTab
from .investigator_item import InvestigatorItemWidget
from .stats_screen import StatsScreen


class InvestigatorScreen(Widget):
  def __init__(self):
    self.page_item_count = 5
    self.faction_tab = FactionTab()
    self.create_list()

  def create_list(self):
    self.items = list(self.faction_items())
    self.list = ListWidget(
        item_count=len(self.items),
        item_height=21,
        item_builder=self.item_builder,
        page_item_count=self.page_item_count,
    )

  def faction_items(self):
    for item in investigator_data.data:
      if item.faction == self.faction_tab.selected_index:
        yield item

  def item_builder(self, index: int, selected: bool):
    return InvestigatorItemWidget(
        investigator=self.items[index],
        selected=selected,
    )

  def on_button(self, app: App, pressed: dict[int, bool]):
    if self.faction_tab.on_button(app, pressed):
      self.create_list()
      return True

    elif pressed[badger2040w.BUTTON_B]:
      app.child = StatsScreen(
          investigator=self.items[self.list.selected_index],
      )
      return True

    return self.list.on_button(app, pressed) or super().on_button(app, pressed)

  def render(self, app: App, size: Size, offset: Offset):
    self.faction_tab.render(app, Size(size.width, 24), Offset(0, self.list.item_height * 5))
    self.list.render(app, size, offset)
