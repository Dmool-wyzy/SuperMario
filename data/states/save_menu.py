import pygame as pg
from .. import tools, constants as c, setup


class SaveMenu(tools._State):
    def __init__(self):
        super().__init__()
        self.font = pg.font.Font(None, 36)
        self.slot = 0  # 0~5

    def startup(self, current_time, persist):
        self.persist = persist
        self.next = c.LOAD_SCREEN

        self.background = setup.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(
            self.background,
            (int(self.background_rect.width * c.BACKGROUND_MULTIPLER),
             int(self.background_rect.height * c.BACKGROUND_MULTIPLER))
        )

        self.viewport = setup.SCREEN.get_rect(
            bottom=setup.SCREEN_RECT.bottom
        )

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.slot = (self.slot + 1) % 6
            elif event.key == pg.K_UP:
                self.slot = (self.slot - 1) % 6
            elif event.key == pg.K_RETURN:
                self.persist['save_slot'] = self.slot
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.next = c.MAIN_MENU
                self.done = True

    def update(self, surface, keys, current_time):
        surface.blit(self.background, self.viewport, self.viewport)
        title = self.font.render("SAVE SELECT", True, (255, 255, 255))
        surface.blit(title, (180, 120))

        for i in range(6):
            color = (255, 255, 0) if i == self.slot else (200, 200, 200)
            text = self.font.render(f"SLOT {i+1}", True, color)
            surface.blit(text, (260, 200 + i * 40))
