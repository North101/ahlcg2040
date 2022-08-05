from ahlcg2040.data import (faction_icons, investigator_data, number_icons,
                            stat_icons)
from ahlcg2040.widgets.app import MyApp


def start():
  faction_icons.load()
  investigator_data.load()
  number_icons.load()
  stat_icons.load()

  app = MyApp()
  while True:
    app.update()
