__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import info, mario


class Menu(tools._State):
    def __init__(self):
        """Initializes the state"""
        tools._State.__init__(self)
        persist = {c.COIN_TOTAL: 0,
                   c.SCORE: 0,
                   c.LIVES: 3,
                   c.TOP_SCORE: 0,
                   c.CURRENT_TIME: 0.0,
                   c.LEVEL_STATE: None,
                   c.CAMERA_START_X: 0,
                   c.MARIO_DEAD: False}
        self.startup(0.0, persist)

    def startup(self, current_time, persist):
        """Called every time the game's state becomes this one.  Initializes
        certain values"""
        self.next = c.SAVE_MENU
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)
        self.help_active = False

        self.sprite_sheet = setup.GFX['title_screen']
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()
        self.setup_help_labels()


    def setup_cursor(self):
        """Creates the mushroom cursor to select 1 or 2 player game"""
        self.cursor = pg.sprite.Sprite()
        dest = (220, 358)
        self.cursor.image, self.cursor.rect = self.get_image(
            24, 160, 8, 8, dest, setup.GFX['item_objects'])
        self.cursor.state = c.PLAYER1

    def setup_help_labels(self):
        self.help_menu_label = []
        self.overhead_info.create_label(self.help_menu_label, 'HELP', 304, 450)

        self.help_title = []
        self.overhead_info.create_label(self.help_title, 'HELP', 0, 0)
        self.center_label(self.help_title, setup.SCREEN_RECT.centerx)

        self.help_lines = []
        lines = [
            'MAIN MENU',
            'UP DOWN SELECT',
            'ENTER CONFIRM',
            'SAVE MENU',
            'UP DOWN SELECT',
            'ENTER LOAD',
            'DEL DELETE',
            'ESC BACK',
            'IN GAME',
            'F6 SAVE   F9 LOAD',
            'F12 SCREENSHOT',
            'F1 INVINCIBLE',
        ]
        step = 22
        total_h = (len(lines) - 1) * step
        y = setup.SCREEN_RECT.centery - total_h // 2
        for i, text in enumerate(lines):
            label = []
            self.overhead_info.create_label(label, text, 0, y + i * step)
            self.center_label(label, setup.SCREEN_RECT.centerx)
            self.help_lines.append(label)

    def center_label(self, label, center_x):
        if not label:
            return
        left = label[0].rect.left
        right = label[-1].rect.right
        dx = int(center_x - (left + right) / 2)
        if dx:
            for letter in label:
                letter.rect.x += dx


    def setup_mario(self):
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        self.mario.rect.x = 110
        self.mario.rect.bottom = c.GROUND_HEIGHT


    def setup_background(self):
        """Setup the background image to blit"""
        self.background = setup.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                   (int(self.background_rect.width*c.BACKGROUND_MULTIPLER),
                                    int(self.background_rect.height*c.BACKGROUND_MULTIPLER)))
        self.viewport = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom)

        self.image_dict = {}
        self.image_dict['GAME_NAME_BOX'] = self.get_image(
            1, 60, 176, 88, (170, 100), setup.GFX['title_screen'])



    def get_image(self, x, y, width, height, dest, sprite_sheet):
        """Returns images and rects to blit onto the screen"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sprite_sheet, (0, 0), (x, y, width, height))
        if sprite_sheet == setup.GFX['title_screen']:
            image.set_colorkey((255, 0, 220))
            image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        else:
            image.set_colorkey(c.BLACK)
            image = pg.transform.scale(image,
                                   (int(rect.width*3),
                                    int(rect.height*3)))

        rect = image.get_rect()
        rect.x = dest[0]
        rect.y = dest[1]
        return (image, rect)


    def update(self, surface, keys, current_time):
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.overhead_info.update(self.game_info)

        surface.blit(self.background, self.viewport, self.viewport)
        if self.help_active:
            for letter in self.help_title:
                surface.blit(letter.image, letter.rect)
            for line in self.help_lines:
                for letter in line:
                    surface.blit(letter.image, letter.rect)
        else:
            surface.blit(self.image_dict['GAME_NAME_BOX'][0],
                         self.image_dict['GAME_NAME_BOX'][1])
            self.update_cursor(keys)
            surface.blit(self.mario.image, self.mario.rect)
            surface.blit(self.cursor.image, self.cursor.rect)
            self.overhead_info.draw(surface)
            for letter in self.help_menu_label:
                surface.blit(letter.image, letter.rect)

    def get_event(self, event):
        if self.help_active and event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE or event.key == pg.K_RETURN:
                self.help_active = False


    def update_cursor(self, keys):
        """Update the position of the cursor"""
        input_list = [pg.K_RETURN, pg.K_a, pg.K_s]

        if self.cursor.state == c.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pg.K_DOWN]:
                self.cursor.state = c.PLAYER2
            for input in input_list:
                if keys[input]:
                    self.reset_game_info()
                    self.persist[c.PLAYER_MODE] = self.cursor.state
                    self.done = True
        elif self.cursor.state == c.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pg.K_UP]:
                self.cursor.state = c.PLAYER1
            elif keys[pg.K_DOWN]:
                self.cursor.state = 'help'
            for input in input_list:
                if keys[input]:
                    self.reset_game_info()
                    self.persist[c.PLAYER_MODE] = self.cursor.state
                    self.done = True
        elif self.cursor.state == 'help':
            self.cursor.rect.y = 448
            if keys[pg.K_UP]:
                self.cursor.state = c.PLAYER2
            for input in input_list:
                if keys[input]:
                    self.help_active = True


    def reset_game_info(self):
        """Resets the game info in case of a Game Over and restart"""
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_STATE] = None

        self.persist = self.game_info















