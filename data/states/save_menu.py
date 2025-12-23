import pygame as pg
from .. import tools, constants as c, setup
from ..save_manager import SaveManager


class SaveMenu(tools._State):
    def __init__(self):
        super().__init__()
        self.font = pg.font.SysFont("arial", 28)
        self.slot = 0  # 0~5

        self.save_manager = SaveManager()
        self.selected_slot = 0

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
            if event.key == pg.K_UP:
                self.selected_slot = (self.selected_slot - 1) % 6

            elif event.key == pg.K_DOWN:
                self.selected_slot = (self.selected_slot + 1) % 6

            elif event.key == pg.K_RETURN:
                self.confirm_slot()

            elif event.key == pg.K_ESCAPE:
                self.done = True

    def confirm_slot(self):
        slot = self.selected_slot

        data = self.save_manager.load(slot)

        if data is None:
            # 新建存档
            data = {
                "lives": 3,
                "score": 0
            }

        # 传给下一个 State
        self.persist["save_slot"] = slot
        self.persist["save_data"] = data

        self.next = c.LEVEL1
        self.done = True

    def update(self, surface, keys, current_time):
        surface.blit(self.background, self.viewport, self.viewport)
        title = self.font.render("SAVE SELECT", True, (255, 255, 255))
        surface.blit(title, (180, 120))

        for i in range(6):
            y = 180 + i * 40
            selected = (i == self.selected_slot)

            data = self.save_manager.load(i)

            if data is None:
                text = f"SLOT {i + 1}   EMPTY"
            else:
                lives = data.get("lives", 3)
                score = data.get("score", 0)
                text = f"SLOT {i + 1}   LIVES {lives}   SCORE {score}"

            color = (255, 255, 0) if selected else (255, 255, 255)
            img = self.font.render(text, True, color)
            surface.blit(img, (180, y))

    def get_image(self, x, y, width, height, dest, sprite_sheet):
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((255, 0, 220))
        image = pg.transform.scale(
            image,
            (int(rect.width * c.SIZE_MULTIPLIER),
             int(rect.height * c.SIZE_MULTIPLIER))
        )

        rect = image.get_rect()
        rect.x, rect.y = dest
        return image, rect
