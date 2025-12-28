__author__ = 'justinarmstrong'

from . import setup,tools
from .states import main_menu, load_screen, level1, save_menu
from . import constants as c


def main():
    """Add states to control here."""
    run_it = tools.Control(setup.ORIGINAL_CAPTION)

    state_dict = {
        c.MAIN_MENU: main_menu.Menu(),
        c.LOAD_SCREEN: load_screen.LoadScreen(),
        c.TIME_OUT: load_screen.TimeOut(),
        c.GAME_OVER: load_screen.GameOver(),
        c.LEVEL1: level1.Level1(),
        c.SAVE_MENU: save_menu.SaveMenu()  # 添加存档选择状态
    }

    run_it.setup_states(state_dict, c.MAIN_MENU)
    run_it.main()



