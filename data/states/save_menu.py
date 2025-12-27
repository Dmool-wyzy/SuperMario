import pygame as pg
from .. import tools, constants as c, setup
from ..save_manager import SaveManager


class SaveMenu(tools._State):
    def __init__(self):
        super().__init__()
        self.title_font = pg.font.SysFont("arial", 34)
        self.font = pg.font.SysFont("arial", 26)
        self.hint_font = pg.font.SysFont("arial", 18)

        self.save_manager = SaveManager()
        self.selected_slot = 0
        self.notice = None
        self.notice_until = 0

    def startup(self, current_time, persist):
        self.persist = persist
        self.next = c.LOAD_SCREEN
        self.notice = None
        self.notice_until = 0

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

            elif event.key == pg.K_DELETE:
                self.delete_slot()

            elif event.key == pg.K_ESCAPE:
                self.next = c.MAIN_MENU
                self.done = True

    def confirm_slot(self):
        slot = self.selected_slot

        data, err = self.save_manager.load_with_error(slot)
        if err:
            self.notice = err
            self.notice_until = pg.time.get_ticks() + 2000

        if data is None:
            data = self.save_manager.create_new(slot)

        player = data.get("player", {})
        self.persist["save_slot"] = slot
        self.persist["save_data"] = data
        self.persist[c.LIVES] = player.get("lives", 3)
        self.persist[c.SCORE] = player.get("score", 0)
        self.persist[c.COIN_TOTAL] = player.get("coin_total", 0)
        self.persist[c.TOP_SCORE] = player.get("top_score", 0)
        self.persist[c.LEVEL_STATE] = c.NOT_FROZEN
        self.persist[c.MARIO_DEAD] = False

        self.done = True

    def delete_slot(self):
        slot = self.selected_slot
        if self.save_manager.delete(slot):
            self.notice = f"已删除 SLOT {slot + 1}"
        else:
            self.notice = f"SLOT {slot + 1} 为空或删除失败"
        self.notice_until = pg.time.get_ticks() + 2000

    def update(self, surface, keys, current_time):
        surface.blit(self.background, self.viewport, self.viewport)
        title = self.title_font.render("SAVE SELECT", True, (255, 255, 255))
        surface.blit(title, (250, 110))

        for i in range(6):
            y = 180 + i * 40
            selected = (i == self.selected_slot)

            summary = self.save_manager.summarize(i)

            if not summary["exists"]:
                text = f"SLOT {i + 1}   EMPTY"
            else:
                lives = summary.get("lives", 3)
                score = summary.get("score", 0)
                checkpoint = summary.get("checkpoint", None)
                checkpoint_text = "START" if not checkpoint else f"CP {checkpoint}"
                text = f"SLOT {i + 1}   {checkpoint_text}   LIVES {lives}   SCORE {score}"

            if selected:
                bar = pg.Surface((560, 32), pg.SRCALPHA)
                bar.fill((40, 40, 40, 160))
                surface.blit(bar, (150, y - 2))
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            img = self.font.render(text, True, color)
            surface.blit(img, (160, y))

        now = pg.time.get_ticks()
        if self.notice and now < self.notice_until:
            notice_bar = pg.Surface((800, 28), pg.SRCALPHA)
            notice_bar.fill((0, 0, 0, 160))
            surface.blit(notice_bar, (0, 505))
            notice_img = self.hint_font.render(self.notice, True, (255, 255, 255))
            surface.blit(notice_img, (20, 510))

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
