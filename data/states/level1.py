from __future__ import division


import pygame as pg
import time
from .. import setup, tools
from .. import constants as c
from .. import game_sound
from .. components import mario
from .. components import collider
from .. components import bricks
from .. components import coin_box
from .. components import enemies
from .. components import checkpoint
from .. components import flagpole
from .. components import info
from .. components import score
from .. components import castle_flag


class Level1(tools._State):
    def __init__(self):
        tools._State.__init__(self)
        self.save_manager = tools.SaveManager()
        self.clear_saved = False

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info.setdefault(c.COIN_TOTAL, 0)
        self.game_info.setdefault(c.SCORE, 0)
        self.game_info.setdefault(c.LIVES, 3)
        self.game_info.setdefault(c.TOP_SCORE, 0)
        self.game_info.setdefault(c.CAMERA_START_X, 0)
        self.game_info.setdefault(c.MARIO_DEAD, False)
        self.game_info[c.CURRENT_TIME] = current_time
        self.current_time = current_time

        save_data = self.persist.get("save_data")
        if isinstance(save_data, dict):
            progress = save_data.get("progress", {})
            viewport_x = progress.get("viewport_x", None) if isinstance(progress, dict) else None
            if isinstance(viewport_x, (int, float)):
                self.game_info[c.CAMERA_START_X] = int(viewport_x)

            flags = save_data.get("flags", {})
            if isinstance(flags, dict):
                self.persist["cheat_invincible"] = bool(flags.get("cheat_invincible", False))
        self.persist.setdefault("cheat_invincible", False)

        self.state = c.NOT_FROZEN
        self.game_info[c.LEVEL_STATE] = self.state
        self.death_timer = 0
        self.flag_timer = 0
        self.flag_score = None
        self.flag_score_total = 0
        self.clear_saved = False

        self.moving_score_list = []
        self.overhead_info_display = info.OverheadInfo(self.game_info, c.LEVEL)
        self.sound_manager = game_sound.Sound(self.overhead_info_display)

        self.setup_background()
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.setup_flag_pole()
        self.setup_enemies()
        self.setup_mario()
        self.setup_checkpoints()
        self.setup_spritegroups()
        self.apply_loaded_save(self.persist.get("save_data"))
        self.sync_cheat_invincible()

    def handle_hotkey(self, key):
        if key == pg.K_F6:
            self.manual_save()
        if key == pg.K_F9:
            self.request_load()
        if key == pg.K_F1:
            self.persist["cheat_invincible"] = not bool(self.persist.get("cheat_invincible", False))
            self.sync_cheat_invincible()
        return None

    def sync_cheat_invincible(self):
        active = bool(self.persist.get("cheat_invincible", False))
        if active:
            self.mario._cheat_invincible_forced = True
            self.mario.invincible = True
            self.mario.losing_invincibility = False
            self.mario.invincible_start_timer = self.current_time
        else:
            if getattr(self.mario, "_cheat_invincible_forced", False):
                self.mario._cheat_invincible_forced = False
                self.mario.invincible = False


    def setup_background(self):
        """Sets the background image, rect and scales it to the correct
        proportions"""
        self.background = setup.GFX['level_1']
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                  (int(self.back_rect.width*c.BACKGROUND_MULTIPLER),
                                  int(self.back_rect.height*c.BACKGROUND_MULTIPLER)))
        self.back_rect = self.background.get_rect()
        width = self.back_rect.width
        height = self.back_rect.height

        self.level = pg.Surface((width, height)).convert()
        self.level_rect = self.level.get_rect()
        self.viewport = setup.SCREEN.get_rect(bottom=self.level_rect.bottom)
        self.viewport.x = self.game_info[c.CAMERA_START_X]


    def setup_ground(self):
        """Creates collideable, invisible rectangles over top of the ground for
        sprites to walk on"""
        ground_rect1 = collider.Collider(0, c.GROUND_HEIGHT,    2953, 60)
        ground_rect2 = collider.Collider(3048, c.GROUND_HEIGHT,  635, 60)
        ground_rect3 = collider.Collider(3819, c.GROUND_HEIGHT, 2735, 60)
        ground_rect4 = collider.Collider(6647, c.GROUND_HEIGHT, 2300, 60)

        self.ground_group = pg.sprite.Group(ground_rect1,
                                           ground_rect2,
                                           ground_rect3,
                                           ground_rect4)


    def setup_pipes(self):
        """Create collideable rects for all the pipes"""

        pipe1 = collider.Collider(1202, 452, 83, 82)
        pipe2 = collider.Collider(1631, 409, 83, 140)
        pipe3 = collider.Collider(1973, 366, 83, 170)
        pipe4 = collider.Collider(2445, 366, 83, 170)
        pipe5 = collider.Collider(6989, 452, 83, 82)
        pipe6 = collider.Collider(7675, 452, 83, 82)

        self.pipe_group = pg.sprite.Group(pipe1, pipe2,
                                          pipe3, pipe4,
                                          pipe5, pipe6)


    def setup_steps(self):
        """Create collideable rects for all the steps"""
        step1 = collider.Collider(5745, 495, 40, 44)
        step2 = collider.Collider(5788, 452, 40, 44)
        step3 = collider.Collider(5831, 409, 40, 44)
        step4 = collider.Collider(5874, 366, 40, 176)


        step5 = collider.Collider(6001, 366, 40, 176)
        step6 = collider.Collider(6044, 408, 40, 40)
        step7 = collider.Collider(6087, 452, 40, 40)
        step8 = collider.Collider(6130, 495, 40, 40)

        step9 = collider.Collider(6345, 495, 40, 40)
        step10 = collider.Collider(6388, 452, 40, 40)
        step11 = collider.Collider(6431, 409, 40, 40)
        step12 = collider.Collider(6474, 366, 40, 40)
        step13 = collider.Collider(6517, 366, 40, 176)

        step14 = collider.Collider(6644, 366, 40, 176)
        step15 = collider.Collider(6687, 408, 40, 40)
        step16 = collider.Collider(6728, 452, 40, 40)
        step17 = collider.Collider(6771, 495, 40, 40)

        step18 = collider.Collider(7760, 495, 40, 40)
        step19 = collider.Collider(7803, 452, 40, 40)
        step20 = collider.Collider(7845, 409, 40, 40)
        step21 = collider.Collider(7888, 366, 40, 40)
        step22 = collider.Collider(7931, 323, 40, 40)
        step23 = collider.Collider(7974, 280, 40, 40)
        step24 = collider.Collider(8017, 237, 40, 40)
        step25 = collider.Collider(8060, 194, 40, 40)
        step26 = collider.Collider(8103, 194, 40, 360)

        step27 = collider.Collider(8488, 495, 40, 40)

        self.step_group = pg.sprite.Group(step1,  step2,
                                          step3,  step4,
                                          step5,  step6,
                                          step7,  step8,
                                          step9,  step10,
                                          step11, step12,
                                          step13, step14,
                                          step15, step16,
                                          step17, step18,
                                          step19, step20,
                                          step21, step22,
                                          step23, step24,
                                          step25, step26,
                                          step27)


    def setup_bricks(self):
        """Creates all the breakable bricks for the level.  Coin and
        powerup groups are created so they can be passed to bricks."""
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.brick_pieces_group = pg.sprite.Group()

        brick1  = bricks.Brick(858,  365)
        brick2  = bricks.Brick(944,  365)
        brick3  = bricks.Brick(1030, 365)
        brick4  = bricks.Brick(3299, 365)
        brick5  = bricks.Brick(3385, 365)
        brick6  = bricks.Brick(3430, 193)
        brick7  = bricks.Brick(3473, 193)
        brick8  = bricks.Brick(3516, 193)
        brick9  = bricks.Brick(3559, 193)
        brick10 = bricks.Brick(3602, 193)
        brick11 = bricks.Brick(3645, 193)
        brick12 = bricks.Brick(3688, 193)
        brick13 = bricks.Brick(3731, 193)
        brick14 = bricks.Brick(3901, 193)
        brick15 = bricks.Brick(3944, 193)
        brick16 = bricks.Brick(3987, 193)
        brick17 = bricks.Brick(4030, 365, c.SIXCOINS, self.coin_group)
        brick18 = bricks.Brick(4287, 365)
        brick19 = bricks.Brick(4330, 365, c.STAR, self.powerup_group)
        brick20 = bricks.Brick(5058, 365)
        brick21 = bricks.Brick(5187, 193)
        brick22 = bricks.Brick(5230, 193)
        brick23 = bricks.Brick(5273, 193)
        brick24 = bricks.Brick(5488, 193)
        brick25 = bricks.Brick(5574, 193)
        brick26 = bricks.Brick(5617, 193)
        brick27 = bricks.Brick(5531, 365)
        brick28 = bricks.Brick(5574, 365)
        brick29 = bricks.Brick(7202, 365)
        brick30 = bricks.Brick(7245, 365)
        brick31 = bricks.Brick(7331, 365)

        self.brick_group = pg.sprite.Group(brick1,  brick2,
                                           brick3,  brick4,
                                           brick5,  brick6,
                                           brick7,  brick8,
                                           brick9,  brick10,
                                           brick11, brick12,
                                           brick13, brick14,
                                           brick15, brick16,
                                           brick17, brick18,
                                           brick19, brick20,
                                           brick21, brick22,
                                           brick23, brick24,
                                           brick25, brick26,
                                           brick27, brick28,
                                           brick29, brick30,
                                           brick31)


    def setup_coin_boxes(self):
        """Creates all the coin boxes and puts them in a sprite group"""
        coin_box1  = coin_box.Coin_box(685, 365, c.COIN, self.coin_group)
        coin_box2  = coin_box.Coin_box(901, 365, c.MUSHROOM, self.powerup_group)
        coin_box3  = coin_box.Coin_box(987, 365, c.COIN, self.coin_group)
        coin_box4  = coin_box.Coin_box(943, 193, c.COIN, self.coin_group)
        coin_box5  = coin_box.Coin_box(3342, 365, c.MUSHROOM, self.powerup_group)
        coin_box6  = coin_box.Coin_box(4030, 193, c.COIN, self.coin_group)
        coin_box7  = coin_box.Coin_box(4544, 365, c.COIN, self.coin_group)
        coin_box8  = coin_box.Coin_box(4672, 365, c.COIN, self.coin_group)
        coin_box9  = coin_box.Coin_box(4672, 193, c.MUSHROOM, self.powerup_group)
        coin_box10 = coin_box.Coin_box(4800, 365, c.COIN, self.coin_group)
        coin_box11 = coin_box.Coin_box(5531, 193, c.COIN, self.coin_group)
        coin_box12 = coin_box.Coin_box(7288, 365, c.COIN, self.coin_group)

        self.coin_box_group = pg.sprite.Group(coin_box1,  coin_box2,
                                              coin_box3,  coin_box4,
                                              coin_box5,  coin_box6,
                                              coin_box7,  coin_box8,
                                              coin_box9,  coin_box10,
                                              coin_box11, coin_box12)


    def setup_flag_pole(self):
        """Creates the flag pole at the end of the level"""
        self.flag = flagpole.Flag(8505, 100)

        pole0 = flagpole.Pole(8505, 97)
        pole1 = flagpole.Pole(8505, 137)
        pole2 = flagpole.Pole(8505, 177)
        pole3 = flagpole.Pole(8505, 217)
        pole4 = flagpole.Pole(8505, 257)
        pole5 = flagpole.Pole(8505, 297)
        pole6 = flagpole.Pole(8505, 337)
        pole7 = flagpole.Pole(8505, 377)
        pole8 = flagpole.Pole(8505, 417)
        pole9 = flagpole.Pole(8505, 450)

        finial = flagpole.Finial(8507, 97)

        self.flag_pole_group = pg.sprite.Group(self.flag,
                                               finial,
                                               pole0,
                                               pole1,
                                               pole2,
                                               pole3,
                                               pole4,
                                               pole5,
                                               pole6,
                                               pole7,
                                               pole8,
                                               pole9)


    def setup_enemies(self):
        """Creates all the enemies and stores them in a list of lists."""
        goomba0 = enemies.Goomba()
        goomba1 = enemies.Goomba()
        goomba2 = enemies.Goomba()
        goomba3 = enemies.Goomba()
        goomba4 = enemies.Goomba(193)
        goomba5 = enemies.Goomba(193)
        goomba6 = enemies.Goomba()
        goomba7 = enemies.Goomba()
        goomba8 = enemies.Goomba()
        goomba9 = enemies.Goomba()
        goomba10 = enemies.Goomba()
        goomba11 = enemies.Goomba()
        goomba12 = enemies.Goomba()
        goomba13 = enemies.Goomba()
        goomba14 = enemies.Goomba()
        goomba15 = enemies.Goomba()

        koopa0 = enemies.Koopa()

        enemy_group1 = pg.sprite.Group(goomba0)
        enemy_group2 = pg.sprite.Group(goomba1)
        enemy_group3 = pg.sprite.Group(goomba2, goomba3)
        enemy_group4 = pg.sprite.Group(goomba4, goomba5)
        enemy_group5 = pg.sprite.Group(goomba6, goomba7)
        enemy_group6 = pg.sprite.Group(koopa0)
        enemy_group7 = pg.sprite.Group(goomba8, goomba9)
        enemy_group8 = pg.sprite.Group(goomba10, goomba11)
        enemy_group9 = pg.sprite.Group(goomba12, goomba13)
        enemy_group10 = pg.sprite.Group(goomba14, goomba15)

        self.enemy_group_list = [enemy_group1,
                                 enemy_group2,
                                 enemy_group3,
                                 enemy_group4,
                                 enemy_group5,
                                 enemy_group6,
                                 enemy_group7,
                                 enemy_group8,
                                 enemy_group9,
                                 enemy_group10]


    def setup_mario(self):
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        self.mario.rect.x = self.viewport.x + 110
        self.mario.rect.bottom = c.GROUND_HEIGHT


    def setup_checkpoints(self):
        """Creates invisible checkpoints that when collided will trigger
        the creation of enemies from the self.enemy_group_list"""
        check1 = checkpoint.Checkpoint(510, "1")
        check2 = checkpoint.Checkpoint(1400, '2')
        check3 = checkpoint.Checkpoint(1740, '3')
        check4 = checkpoint.Checkpoint(3080, '4')
        check5 = checkpoint.Checkpoint(3750, '5')
        check6 = checkpoint.Checkpoint(4150, '6')
        check7 = checkpoint.Checkpoint(4470, '7')
        check8 = checkpoint.Checkpoint(4950, '8')
        check9 = checkpoint.Checkpoint(5100, '9')
        check10 = checkpoint.Checkpoint(6800, '10')
        check11 = checkpoint.Checkpoint(8504, '11', 5, 6)
        check12 = checkpoint.Checkpoint(8775, '12')
        check13 = checkpoint.Checkpoint(2740, 'secret_mushroom', 360, 40, 12)

        self.check_point_group = pg.sprite.Group(check1, check2, check3,
                                                 check4, check5, check6,
                                                 check7, check8, check9,
                                                 check10, check11, check12,
                                                 check13)


    def setup_spritegroups(self):
        """Sprite groups created for convenience"""
        self.sprites_about_to_die_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()

        self.ground_step_pipe_group = pg.sprite.Group(self.ground_group,
                                                      self.pipe_group,
                                                      self.step_group)

        self.mario_and_enemy_group = pg.sprite.Group(self.mario,
                                                     self.enemy_group)


    def update(self, surface, keys, current_time):
        """Updates Entire level using states.  Called by the control object"""
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(keys)
        self.check_if_time_out()
        self.blit_everything(surface)
        self.sound_manager.update(self.game_info, self.mario)



    def handle_states(self, keys):
        """If the level is in a FROZEN state, only mario will update"""
        if self.state == c.FROZEN:
            self.update_during_transition_state(keys)
        elif self.state == c.NOT_FROZEN:
            self.update_all_sprites(keys)
        elif self.state == c.IN_CASTLE:
            self.update_while_in_castle()
        elif self.state == c.FLAG_AND_FIREWORKS:
            self.update_flag_and_fireworks()

    def update_during_transition_state(self, keys):
        """Updates mario in a transition state (like becoming big, small,
         or dies). Checks if he leaves the transition state or dies to
         change the level state back"""
        self.mario.update(keys, self.game_info, self.powerup_group)
        self.sync_cheat_invincible()
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        self.coin_box_group.update(self.game_info)
        self.flag_pole_group.update(self.game_info)
        self.check_if_mario_in_transition_state()
        self.check_flag()
        self.check_for_mario_death()
        self.overhead_info_display.update(self.game_info, self.mario)


    def check_if_mario_in_transition_state(self):
        """If mario is in a transition state, the level will be in a FREEZE
        state"""
        if self.mario.in_transition_state:
            self.game_info[c.LEVEL_STATE] = self.state = c.FROZEN
        elif self.mario.in_transition_state == False:
            if self.state == c.FROZEN:
                self.game_info[c.LEVEL_STATE] = self.state = c.NOT_FROZEN


    def update_all_sprites(self, keys):
        """Updates the location of all sprites on the screen."""
        self.mario.update(keys, self.game_info, self.powerup_group)
        self.sync_cheat_invincible()
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        self.flag_pole_group.update()
        self.check_points_check()
        self.enemy_group.update(self.game_info)
        self.sprites_about_to_die_group.update(self.game_info, self.viewport)
        self.shell_group.update(self.game_info)
        self.brick_group.update()
        self.coin_box_group.update(self.game_info)
        self.powerup_group.update(self.game_info, self.viewport)
        self.coin_group.update(self.game_info, self.viewport)
        self.brick_pieces_group.update()
        self.adjust_sprite_positions()
        self.check_if_mario_in_transition_state()
        self.check_for_mario_death()
        self.update_viewport()
        self.overhead_info_display.update(self.game_info, self.mario)


    def check_points_check(self):
        """Detect if checkpoint collision occurs, delete checkpoint,
        add enemies to self.enemy_group"""
        checkpoint = pg.sprite.spritecollideany(self.mario,
                                                 self.check_point_group)
        if checkpoint:
            checkpoint.kill()
            if getattr(checkpoint, "name", None) == "12":
                self.record_level_clear_and_reset_save()
                self.clear_saved = True
            else:
                self.save_progress(checkpoint)

            for i in range(1,11):
                if checkpoint.name == str(i):
                    for index, enemy in enumerate(self.enemy_group_list[i -1]):
                        enemy.rect.x = self.viewport.right + (index * 60)
                    self.enemy_group.add(self.enemy_group_list[i-1])

            if checkpoint.name == '11':
                self.mario.state = c.FLAGPOLE
                self.mario.invincible = False
                self.mario.flag_pole_right = checkpoint.rect.right
                if self.mario.rect.bottom < self.flag.rect.y:
                    self.mario.rect.bottom = self.flag.rect.y
                self.flag.state = c.SLIDE_DOWN
                self.create_flag_points()

            elif checkpoint.name == '12':
                self.state = c.IN_CASTLE
                self.mario.kill()
                self.mario.state = c.STAND
                self.mario.in_castle = True
                self.overhead_info_display.state = c.FAST_COUNT_DOWN


            elif checkpoint.name == 'secret_mushroom' and self.mario.y_vel < 0:
                mushroom_box = coin_box.Coin_box(checkpoint.rect.x,
                                        checkpoint.rect.bottom - 40,
                                        '1up_mushroom',
                                        self.powerup_group)
                mushroom_box.start_bump(self.moving_score_list)
                self.coin_box_group.add(mushroom_box)

                self.mario.y_vel = 7
                self.mario.rect.y = mushroom_box.rect.bottom
                self.mario.state = c.FALL

            self.mario_and_enemy_group.add(self.enemy_group)

    def save_progress(self, checkpoint_sprite=None):
        slot = self.persist.get("save_slot", 0)
        checkpoint_name = None
        if checkpoint_sprite is not None:
            checkpoint_name = getattr(checkpoint_sprite, "name", None)
        if checkpoint_name in ("11", "12"):
            checkpoint_name = "10"
        data = self.build_save_payload(checkpoint_name=checkpoint_name)
        self.persist["save_data"] = data
        self.save_manager.save(slot, data)

    def save_player_state(self):
        slot = self.persist.get("save_slot", None)
        if not isinstance(slot, int):
            return

        existing = self.persist.get("save_data") if isinstance(self.persist.get("save_data"), dict) else None
        data = self.save_manager.normalize(existing or {}, slot) or self.save_manager.create_new(slot)
        if not isinstance(data, dict):
            return

        player = data.setdefault("player", {})
        if not isinstance(player, dict):
            player = {}
            data["player"] = player

        try:
            player["lives"] = int(self.persist.get(c.LIVES, 3))
        except (TypeError, ValueError):
            player["lives"] = 3
        try:
            player["score"] = int(self.persist.get(c.SCORE, 0))
        except (TypeError, ValueError):
            player["score"] = 0
        try:
            player["coin_total"] = int(self.persist.get(c.COIN_TOTAL, 0))
        except (TypeError, ValueError):
            player["coin_total"] = 0
        try:
            player["top_score"] = int(self.persist.get(c.TOP_SCORE, 0))
        except (TypeError, ValueError):
            player["top_score"] = 0

        player["big"] = bool(getattr(self.mario, "big", False))
        player["fire"] = bool(getattr(self.mario, "fire", False))

        flags = data.setdefault("flags", {})
        if isinstance(flags, dict):
            flags["cheat_invincible"] = bool(self.persist.get("cheat_invincible", False))

        self.persist["save_data"] = data
        self.save_manager.save(slot, data)

    def build_save_payload(self, checkpoint_name=None):
        slot = self.persist.get("save_slot", 0)
        existing = self.persist.get("save_data") if isinstance(self.persist.get("save_data"), dict) else None
        data = self.save_manager.normalize(existing or {}, slot) or self.save_manager.create_new(slot)

        player = data.setdefault("player", {})
        player["lives"] = int(self.game_info.get(c.LIVES, 3))
        player["score"] = int(self.game_info.get(c.SCORE, 0))
        player["coin_total"] = int(self.game_info.get(c.COIN_TOTAL, 0))
        player["top_score"] = int(self.game_info.get(c.TOP_SCORE, 0))
        player["big"] = bool(getattr(self.mario, "big", False))
        player["fire"] = bool(getattr(self.mario, "fire", False))

        progress = data.setdefault("progress", {})
        progress["level"] = 1
        if checkpoint_name is not None:
            progress["checkpoint"] = checkpoint_name
        progress["mario_x"] = int(self.mario.rect.x)
        progress["mario_y"] = int(self.mario.rect.y)
        progress["viewport_x"] = int(self.viewport.x)

        flags = data.setdefault("flags", {})
        flags["cheat_invincible"] = bool(self.persist.get("cheat_invincible", False))

        return data

    def manual_save(self):
        slot = self.persist.get("save_slot", 0)
        data = self.build_save_payload(checkpoint_name=None)
        err = self.save_manager.save_with_error(slot, data)
        if err:
            return f"手动存档失败：{err}"
        self.persist["save_data"] = data
        return f"手动存档成功：SLOT {int(slot) + 1}"

    def request_load(self):
        slot = self.persist.get("save_slot", 0)
        data, err = self.save_manager.load_with_error(slot)
        if err:
            return f"读档失败：{err}"
        if data is None:
            return "读档失败：该槽位为空"

        player = data.get("player", {})
        try:
            lives = int(player.get("lives", 3)) if isinstance(player, dict) else 3
        except (TypeError, ValueError):
            lives = 3
        if lives <= 0:
            data = self.save_manager.reset_run(data, slot) or self.save_manager.create_new(slot)
            self.save_manager.save(slot, data)
            player = data.get("player", {})

        self.persist["save_data"] = data
        self.persist[c.LIVES] = int(player.get("lives", 3)) if isinstance(player, dict) else 3
        self.persist[c.SCORE] = int(player.get("score", 0)) if isinstance(player, dict) else 0
        self.persist[c.COIN_TOTAL] = int(player.get("coin_total", 0)) if isinstance(player, dict) else 0
        self.persist[c.TOP_SCORE] = int(player.get("top_score", 0)) if isinstance(player, dict) else 0
        flags = data.get("flags", {})
        if isinstance(flags, dict):
            self.persist["cheat_invincible"] = bool(flags.get("cheat_invincible", False))
        self.game_info[c.CAMERA_START_X] = 0
        self.next = c.LOAD_SCREEN
        self.done = True
        return f"读档成功：SLOT {int(slot) + 1}"

    def apply_loaded_save(self, save_data):
        if not isinstance(save_data, dict):
            return

        save_data = self.save_manager.normalize(save_data, self.persist.get("save_slot", 0))
        if not isinstance(save_data, dict):
            return
        self.persist["save_data"] = save_data

        player = save_data.get("player", {})
        if isinstance(player, dict):
            try:
                lives = int(player.get("lives", self.game_info.get(c.LIVES, 3)))
            except (TypeError, ValueError):
                lives = int(self.game_info.get(c.LIVES, 3))
            if lives <= 0:
                slot = self.persist.get("save_slot", None)
                reset = self.save_manager.reset_run(save_data, slot) if isinstance(slot, int) else None
                if isinstance(reset, dict):
                    save_data = reset
                    self.persist["save_data"] = save_data
                    player = save_data.get("player", {})
                    lives = int(player.get("lives", 3)) if isinstance(player, dict) else 3
                    if isinstance(slot, int):
                        self.save_manager.save(slot, save_data)
                else:
                    lives = 3
                    player["lives"] = lives
                    if isinstance(slot, int):
                        self.save_manager.save(slot, save_data)
            self.game_info[c.LIVES] = lives
            self.game_info[c.SCORE] = int(player.get("score", self.game_info.get(c.SCORE, 0)))
            self.game_info[c.COIN_TOTAL] = int(player.get("coin_total", self.game_info.get(c.COIN_TOTAL, 0)))
            self.game_info[c.TOP_SCORE] = int(player.get("top_score", self.game_info.get(c.TOP_SCORE, 0)))
            self.apply_mario_power_state(bool(player.get("big", False)), bool(player.get("fire", False)))


        progress = save_data.get("progress", {})
        if isinstance(progress, dict):
            checkpoint_name = progress.get("checkpoint", None)
            mario_x = progress.get("mario_x", None)
            mario_y = progress.get("mario_y", None)
            viewport_x = progress.get("viewport_x", None)

            end_checkpoint = False
            try:
                checkpoint_int = int(checkpoint_name) if checkpoint_name is not None else None
            except (TypeError, ValueError):
                checkpoint_int = None
            if checkpoint_int is not None and checkpoint_int >= 11:
                end_checkpoint = True
            if isinstance(mario_x, (int, float)) and mario_x >= 8500:
                end_checkpoint = True
            if isinstance(viewport_x, (int, float)) and viewport_x >= 8400:
                end_checkpoint = True

            if end_checkpoint:
                self.migrate_end_checkpoint_to_clear_record(save_data)

                spawn_x = 110
                spawn_y = int(c.GROUND_HEIGHT - self.mario.rect.height)
                mario_x = spawn_x
                mario_y = spawn_y
                viewport_x = 0
                progress["checkpoint"] = None
                progress["mario_x"] = spawn_x
                progress["mario_y"] = spawn_y
                progress["viewport_x"] = 0
                self.game_info[c.CAMERA_START_X] = 0

            if isinstance(mario_x, (int, float)):
                self.mario.rect.x = int(mario_x)
            if isinstance(mario_y, (int, float)):
                self.mario.rect.y = int(mario_y)
            if self.mario.rect.bottom > c.GROUND_HEIGHT:
                self.mario.rect.bottom = c.GROUND_HEIGHT

            if isinstance(viewport_x, (int, float)):
                highest = self.level_rect.w - self.viewport.w
                self.viewport.x = max(0, min(int(viewport_x), highest))
            else:
                highest = self.level_rect.w - self.viewport.w
                target = self.mario.rect.centerx - self.viewport.w // 3
                self.viewport.x = max(0, min(int(target), highest))

            self.apply_checkpoint_state(progress.get("checkpoint", None))

            if end_checkpoint:
                slot = self.persist.get("save_slot", None)
                if isinstance(slot, int):
                    self.save_manager.save(slot, save_data)

        flags = save_data.get("flags", {})
        if isinstance(flags, dict):
            self.persist["cheat_invincible"] = bool(flags.get("cheat_invincible", self.persist.get("cheat_invincible", False)))

    def migrate_end_checkpoint_to_clear_record(self, save_data):
        if not isinstance(save_data, dict):
            return

        records = save_data.setdefault("records", {})
        if not isinstance(records, dict):
            records = {}
            save_data["records"] = records

        level1_records = records.setdefault("level1", {})
        if not isinstance(level1_records, dict):
            level1_records = {}
            records["level1"] = level1_records

        source_updated_at_ms = save_data.get("updated_at_ms", None)
        try:
            source_updated_at_ms = int(source_updated_at_ms) if source_updated_at_ms is not None else None
        except (TypeError, ValueError):
            source_updated_at_ms = None

        if source_updated_at_ms is not None and level1_records.get("last_clear_updated_at_ms") == source_updated_at_ms:
            return

        player = save_data.get("player", {})
        progress = save_data.get("progress", {})
        last_clear = {
            "timestamp_ms": int(time.time() * 1000),
            "score": int(player.get("score", 0)) if isinstance(player, dict) else 0,
            "coin_total": int(player.get("coin_total", 0)) if isinstance(player, dict) else 0,
            "lives": int(player.get("lives", 3)) if isinstance(player, dict) else 3,
            "checkpoint": progress.get("checkpoint", None) if isinstance(progress, dict) else None,
            "mario_x": progress.get("mario_x", None) if isinstance(progress, dict) else None,
            "mario_y": progress.get("mario_y", None) if isinstance(progress, dict) else None,
            "viewport_x": progress.get("viewport_x", None) if isinstance(progress, dict) else None,
        }

        try:
            clears = int(level1_records.get("clears", 0))
        except (TypeError, ValueError):
            clears = 0

        level1_records["clears"] = clears + 1
        level1_records["last_clear"] = last_clear
        if source_updated_at_ms is not None:
            level1_records["last_clear_updated_at_ms"] = source_updated_at_ms

    def record_level_clear_and_reset_save(self):
        slot = self.persist.get("save_slot", None)
        if not isinstance(slot, int):
            return

        existing = self.persist.get("save_data") if isinstance(self.persist.get("save_data"), dict) else None
        data = self.save_manager.normalize(existing or {}, slot) or self.save_manager.create_new(slot)
        if not isinstance(data, dict):
            return

        records = data.setdefault("records", {})
        if not isinstance(records, dict):
            records = {}
            data["records"] = records

        level1_records = records.setdefault("level1", {})
        if not isinstance(level1_records, dict):
            level1_records = {}
            records["level1"] = level1_records

        try:
            clears = int(level1_records.get("clears", 0))
        except (TypeError, ValueError):
            clears = 0

        level1_records["clears"] = clears + 1
        level1_records["last_clear"] = {
            "timestamp_ms": int(time.time() * 1000),
            "score": int(self.game_info.get(c.SCORE, 0)),
            "coin_total": int(self.game_info.get(c.COIN_TOTAL, 0)),
            "lives": int(self.game_info.get(c.LIVES, 3)),
        }

        player = data.setdefault("player", {})
        if isinstance(player, dict):
            try:
                previous_top = int(player.get("top_score", 0))
            except (TypeError, ValueError):
                previous_top = 0
            try:
                current_top = int(self.persist.get(c.TOP_SCORE, previous_top))
            except (TypeError, ValueError):
                current_top = previous_top
            try:
                current_score = int(self.game_info.get(c.SCORE, 0))
            except (TypeError, ValueError):
                current_score = 0

            player["lives"] = 3
            player["score"] = 0
            player["coin_total"] = 0
            player["top_score"] = max(previous_top, current_top, current_score)
            player["big"] = False
            player["fire"] = False

        progress = data.setdefault("progress", {})
        if isinstance(progress, dict):
            progress["level"] = 1
            progress["checkpoint"] = None
            progress["mario_x"] = None
            progress["mario_y"] = None
            progress["viewport_x"] = 0

        self.persist["save_data"] = data
        self.save_manager.save(slot, data)

    def apply_mario_power_state(self, big, fire):
        bottom = self.mario.rect.bottom
        x = self.mario.rect.x
        self.mario.big = bool(big) or bool(fire)
        self.mario.fire = bool(fire)
        if self.mario.fire:
            self.mario.right_frames = self.mario.right_fire_frames
            self.mario.left_frames = self.mario.left_fire_frames
        elif self.mario.big:
            self.mario.right_frames = self.mario.right_big_normal_frames
            self.mario.left_frames = self.mario.left_big_normal_frames
        else:
            self.mario.right_frames = self.mario.right_small_normal_frames
            self.mario.left_frames = self.mario.left_small_normal_frames
        self.mario.frame_index = 0
        self.mario.image = self.mario.right_frames[self.mario.frame_index] if self.mario.facing_right else self.mario.left_frames[self.mario.frame_index]
        self.mario.rect = self.mario.image.get_rect()
        self.mario.rect.bottom = bottom
        self.mario.rect.x = x

    def apply_checkpoint_state(self, checkpoint_name):
        if not checkpoint_name:
            return
        try:
            index = int(checkpoint_name)
        except (TypeError, ValueError):
            return
        if not (1 <= index <= 10):
            return

        for cp in list(self.check_point_group):
            try:
                cp_index = int(getattr(cp, "name", ""))
            except (TypeError, ValueError):
                continue
            if 1 <= cp_index <= index:
                cp.kill()

        for i in range(1, index + 1):
            for enemy_index, enemy in enumerate(self.enemy_group_list[i - 1]):
                enemy.rect.x = self.viewport.right + (enemy_index * 60)
            self.enemy_group.add(self.enemy_group_list[i - 1])
        self.mario_and_enemy_group.add(self.enemy_group)

    def create_flag_points(self):
        """Creates the points that appear when Mario touches the
        flag pole"""
        x = 8518
        y = c.GROUND_HEIGHT - 60
        mario_bottom = self.mario.rect.bottom

        if mario_bottom > (c.GROUND_HEIGHT - 40 - 40):
            self.flag_score = score.Score(x, y, 100, True)
            self.flag_score_total = 100
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 160):
            self.flag_score = score.Score(x, y, 400, True)
            self.flag_score_total = 400
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 240):
            self.flag_score = score.Score(x, y, 800, True)
            self.flag_score_total = 800
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 360):
            self.flag_score = score.Score(x, y, 2000, True)
            self.flag_score_total = 2000
        else:
            self.flag_score = score.Score(x, y, 5000, True)
            self.flag_score_total = 5000


    def adjust_sprite_positions(self):
        """Adjusts sprites by their x and y velocities and collisions"""
        self.adjust_mario_position()
        self.adjust_enemy_position()
        self.adjust_shell_position()
        self.adjust_powerup_position()


    def adjust_mario_position(self):
        """Adjusts Mario's position based on his x, y velocities and
        potential collisions"""
        self.last_x_position = self.mario.rect.right
        self.mario.rect.x += round(self.mario.x_vel)
        self.check_mario_x_collisions()

        if self.mario.in_transition_state == False:
            self.mario.rect.y += round(self.mario.y_vel)
            self.check_mario_y_collisions()

        if self.mario.rect.x < (self.viewport.x + 5):
            self.mario.rect.x = (self.viewport.x + 5)


    def check_mario_x_collisions(self):
        """Check for collisions after Mario is moved on the x axis"""
        collider = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)
        powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)

        if coin_box:
            self.adjust_mario_for_x_collisions(coin_box)

        elif brick:
            self.adjust_mario_for_x_collisions(brick)

        elif collider:
            self.adjust_mario_for_x_collisions(collider)

        elif enemy:
            if self.mario.invincible or self.persist.get("cheat_invincible", False):
                setup.SFX['kick'].play()
                self.game_info[c.SCORE] += 100
                self.moving_score_list.append(
                    score.Score(self.mario.rect.right - self.viewport.x,
                                self.mario.rect.y, 100))
                enemy.kill()
                enemy.start_death_jump(c.RIGHT)
                self.sprites_about_to_die_group.add(enemy)
            elif self.mario.big:
                setup.SFX['pipe'].play()
                self.mario.fire = False
                self.mario.y_vel = -1
                self.mario.state = c.BIG_TO_SMALL
                self.convert_fireflowers_to_mushrooms()
            elif self.mario.hurt_invincible:
                pass
            else:
                self.mario.start_death_jump(self.game_info)
                self.state = c.FROZEN

        elif shell:
            self.adjust_mario_for_x_shell_collisions(shell)

        elif powerup:
            if powerup.name == c.STAR:
                self.game_info[c.SCORE] += 1000

                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x,
                                self.mario.rect.y, 1000))
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time
            elif powerup.name == c.MUSHROOM:
                setup.SFX['powerup'].play()
                self.game_info[c.SCORE] += 1000
                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x,
                                self.mario.rect.y - 20, 1000))

                self.mario.y_vel = -1
                self.mario.state = c.SMALL_TO_BIG
                self.mario.in_transition_state = True
                self.convert_mushrooms_to_fireflowers()
            elif powerup.name == c.LIFE_MUSHROOM:
                self.moving_score_list.append(
                    score.Score(powerup.rect.right - self.viewport.x,
                                powerup.rect.y,
                                c.ONEUP))

                self.game_info[c.LIVES] += 1
                setup.SFX['one_up'].play()
                self.save_player_state()
            elif powerup.name == c.FIREFLOWER:
                setup.SFX['powerup'].play()
                self.game_info[c.SCORE] += 1000
                self.moving_score_list.append(
                    score.Score(self.mario.rect.centerx - self.viewport.x,
                                self.mario.rect.y, 1000))

                if self.mario.big and self.mario.fire == False:
                    self.mario.state = c.BIG_TO_FIRE
                    self.mario.in_transition_state = True
                elif self.mario.big == False:
                    self.mario.state = c.SMALL_TO_BIG
                    self.mario.in_transition_state = True
                    self.convert_mushrooms_to_fireflowers()

            if powerup.name != c.FIREBALL:
                powerup.kill()


    def convert_mushrooms_to_fireflowers(self):
        """When Mario becomees big, converts all fireflower powerups to
        mushroom powerups"""
        for brick in self.brick_group:
            if brick.contents == c.MUSHROOM:
                brick.contents = c.FIREFLOWER
        for coin_box in self.coin_box_group:
            if coin_box.contents == c.MUSHROOM:
                coin_box.contents = c.FIREFLOWER


    def convert_fireflowers_to_mushrooms(self):
        """When Mario becomes small, converts all mushroom powerups to
        fireflower powerups"""
        for brick in self.brick_group:
            if brick.contents == c.FIREFLOWER:
                brick.contents = c.MUSHROOM
        for coin_box in self.coin_box_group:
            if coin_box.contents == c.FIREFLOWER:
                coin_box.contents = c.MUSHROOM


    def adjust_mario_for_x_collisions(self, collider):
        """Puts Mario flush next to the collider after moving on the x axis"""
        if self.mario.rect.x < collider.rect.x:
            self.mario.rect.right = collider.rect.left
        else:
            self.mario.rect.left = collider.rect.right

        self.mario.x_vel = 0


    def adjust_mario_for_x_shell_collisions(self, shell):
        """Deals with Mario if he hits a shell moving on the x axis"""
        if shell.state == c.JUMPED_ON:
            if self.mario.rect.x < shell.rect.x:
                self.game_info[c.SCORE] += 400
                self.moving_score_list.append(
                    score.Score(shell.rect.centerx - self.viewport.x,
                                shell.rect.y,
                                400))
                self.mario.rect.right = shell.rect.left
                shell.direction = c.RIGHT
                shell.x_vel = 5
                shell.rect.x += 5

            else:
                self.mario.rect.left = shell.rect.right
                shell.direction = c.LEFT
                shell.x_vel = -5
                shell.rect.x += -5

            shell.state = c.SHELL_SLIDE

        elif shell.state == c.SHELL_SLIDE:
            invincible = self.mario.invincible or self.persist.get("cheat_invincible", False)
            if self.mario.big and not invincible:
                self.mario.state = c.BIG_TO_SMALL
            elif invincible:
                self.game_info[c.SCORE] += 200
                self.moving_score_list.append(
                    score.Score(shell.rect.right - self.viewport.x,
                                shell.rect.y, 200))
                shell.kill()
                self.sprites_about_to_die_group.add(shell)
                shell.start_death_jump(c.RIGHT)
            else:
                if not self.mario.hurt_invincible and not invincible:
                    self.state = c.FROZEN
                    self.mario.start_death_jump(self.game_info)


    def check_mario_y_collisions(self):
        """Checks for collisions when Mario moves along the y-axis"""
        ground_step_or_pipe = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)

        brick, coin_box = self.prevent_collision_conflict(brick, coin_box)

        if coin_box:
            self.adjust_mario_for_y_coin_box_collisions(coin_box)

        elif brick:
            self.adjust_mario_for_y_brick_collisions(brick)

        elif ground_step_or_pipe:
            self.adjust_mario_for_y_ground_pipe_collisions(ground_step_or_pipe)

        elif enemy:
            if self.mario.invincible or self.persist.get("cheat_invincible", False):
                setup.SFX['kick'].play()
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                enemy.start_death_jump(c.RIGHT)
            else:
                self.adjust_mario_for_y_enemy_collisions(enemy)

        elif shell:
            self.adjust_mario_for_y_shell_collisions(shell)

        elif powerup:
            if powerup.name == c.STAR:
                setup.SFX['powerup'].play()
                powerup.kill()
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time

        self.test_if_mario_is_falling()


    def prevent_collision_conflict(self, obstacle1, obstacle2):
        """Allows collisions only for the item closest to marios centerx"""
        if obstacle1 and obstacle2:
            obstacle1_distance = self.mario.rect.centerx - obstacle1.rect.centerx
            if obstacle1_distance < 0:
                obstacle1_distance *= -1
            obstacle2_distance = self.mario.rect.centerx - obstacle2.rect.centerx
            if obstacle2_distance < 0:
                obstacle2_distance *= -1

            if obstacle1_distance < obstacle2_distance:
                obstacle2 = False
            else:
                obstacle1 = False

        return obstacle1, obstacle2


    def adjust_mario_for_y_coin_box_collisions(self, coin_box):
        """Mario collisions with coin boxes on the y-axis"""
        if self.mario.rect.y > coin_box.rect.y:
            if coin_box.state == c.RESTING:
                if coin_box.contents == c.COIN:
                    self.game_info[c.SCORE] += 200
                    coin_box.start_bump(self.moving_score_list)
                    if coin_box.contents == c.COIN:
                        self.game_info[c.COIN_TOTAL] += 1
                else:
                    coin_box.start_bump(self.moving_score_list)

            elif coin_box.state == c.OPENED:
                pass
            setup.SFX['bump'].play()
            self.mario.y_vel = 7
            self.mario.rect.y = coin_box.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = coin_box.rect.top
            self.mario.state = c.WALK


    def adjust_mario_for_y_brick_collisions(self, brick):
        """Mario collisions with bricks on the y-axis"""
        if self.mario.rect.y > brick.rect.y:
            if brick.state == c.RESTING:
                if self.mario.big and brick.contents is None:
                    setup.SFX['brick_smash'].play()
                    self.check_if_enemy_on_brick(brick)
                    brick.kill()
                    self.brick_pieces_group.add(
                        bricks.BrickPiece(brick.rect.x,
                                               brick.rect.y - (brick.rect.height/2),
                                               -2, -12),
                        bricks.BrickPiece(brick.rect.right,
                                               brick.rect.y - (brick.rect.height/2),
                                               2, -12),
                        bricks.BrickPiece(brick.rect.x,
                                               brick.rect.y,
                                               -2, -6),
                        bricks.BrickPiece(brick.rect.right,
                                               brick.rect.y,
                                               2, -6))
                else:
                    setup.SFX['bump'].play()
                    if brick.coin_total > 0:
                        self.game_info[c.COIN_TOTAL] += 1
                        self.game_info[c.SCORE] += 200
                    self.check_if_enemy_on_brick(brick)
                    brick.start_bump(self.moving_score_list)
            elif brick.state == c.OPENED:
                setup.SFX['bump'].play()
            self.mario.y_vel = 7
            self.mario.rect.y = brick.rect.bottom
            self.mario.state = c.FALL

        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = brick.rect.top
            self.mario.state = c.WALK


    def check_if_enemy_on_brick(self, brick):
        """Kills enemy if on a bumped or broken brick"""
        brick.rect.y -= 5

        enemy = pg.sprite.spritecollideany(brick, self.enemy_group)

        if enemy:
            setup.SFX['kick'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.centerx - self.viewport.x,
                            enemy.rect.y,
                            100))
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            if self.mario.rect.centerx > brick.rect.centerx:
                enemy.start_death_jump('right')
            else:
                enemy.start_death_jump('left')

        brick.rect.y += 5



    def adjust_mario_for_y_ground_pipe_collisions(self, collider):
        """Mario collisions with pipes on the y-axis"""
        if collider.rect.bottom > self.mario.rect.bottom:
            self.mario.y_vel = 0
            self.mario.rect.bottom = collider.rect.top
            if self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.WALKING_TO_CASTLE
            else:
                self.mario.state = c.WALK
        elif collider.rect.top < self.mario.rect.top:
            self.mario.y_vel = 7
            self.mario.rect.top = collider.rect.bottom
            self.mario.state = c.FALL


    def test_if_mario_is_falling(self):
        """Changes Mario to a FALL state if more than a pixel above a pipe,
        ground, step or box"""
        self.mario.rect.y += 1
        test_collide_group = pg.sprite.Group(self.ground_step_pipe_group,
                                                 self.brick_group,
                                                 self.coin_box_group)


        if pg.sprite.spritecollideany(self.mario, test_collide_group) is None:
            if self.mario.state != c.JUMP \
                and self.mario.state != c.DEATH_JUMP \
                and self.mario.state != c.SMALL_TO_BIG \
                and self.mario.state != c.BIG_TO_FIRE \
                and self.mario.state != c.BIG_TO_SMALL \
                and self.mario.state != c.FLAGPOLE \
                and self.mario.state != c.WALKING_TO_CASTLE \
                and self.mario.state != c.END_OF_LEVEL_FALL:
                self.mario.state = c.FALL
            elif self.mario.state == c.WALKING_TO_CASTLE or \
                self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.END_OF_LEVEL_FALL

        self.mario.rect.y -= 1


    def adjust_mario_for_y_enemy_collisions(self, enemy):
        """Mario collisions with all enemies on the y-axis"""
        if self.mario.y_vel > 0:
            setup.SFX['stomp'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.centerx - self.viewport.x,
                            enemy.rect.y, 100))
            enemy.state = c.JUMPED_ON
            enemy.kill()
            if enemy.name == c.GOOMBA:
                enemy.death_timer = self.current_time
                self.sprites_about_to_die_group.add(enemy)
            elif enemy.name == c.KOOPA:
                self.shell_group.add(enemy)

            self.mario.rect.bottom = enemy.rect.top
            self.mario.state = c.JUMP
            self.mario.y_vel = -7
        


    def adjust_mario_for_y_shell_collisions(self, shell):
        """Mario collisions with Koopas in their shells on the y axis"""
        if self.mario.y_vel > 0:
            self.game_info[c.SCORE] += 400
            self.moving_score_list.append(
                score.Score(self.mario.rect.centerx - self.viewport.x,
                            self.mario.rect.y, 400))
            if shell.state == c.JUMPED_ON:
                setup.SFX['kick'].play()
                shell.state = c.SHELL_SLIDE
                if self.mario.rect.centerx < shell.rect.centerx:
                    shell.direction = c.RIGHT
                    shell.rect.left = self.mario.rect.right + 5
                else:
                    shell.direction = c.LEFT
                    shell.rect.right = self.mario.rect.left - 5
            else:
                shell.state = c.JUMPED_ON


    def adjust_enemy_position(self):
        """Moves all enemies along the x, y axes and check for collisions"""
        for enemy in self.enemy_group:
            enemy.rect.x += enemy.x_vel
            self.check_enemy_x_collisions(enemy)

            enemy.rect.y += enemy.y_vel
            self.check_enemy_y_collisions(enemy)
            self.delete_if_off_screen(enemy)


    def check_enemy_x_collisions(self, enemy):
        """Enemy collisions along the x axis.  Removes enemy from enemy group
        in order to check against all other enemies then adds it back."""
        enemy.kill()

        collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        enemy_collider = pg.sprite.spritecollideany(enemy, self.enemy_group)

        if collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = collider.rect.left
                enemy.direction = c.LEFT
                enemy.x_vel = -2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = collider.rect.right
                enemy.direction = c.RIGHT
                enemy.x_vel = 2


        elif enemy_collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = enemy_collider.rect.left
                enemy.direction = c.LEFT
                enemy_collider.direction = c.RIGHT
                enemy.x_vel = -2
                enemy_collider.x_vel = 2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = enemy_collider.rect.right
                enemy.direction = c.RIGHT
                enemy_collider.direction = c.LEFT
                enemy.x_vel = 2
                enemy_collider.x_vel = -2

        self.enemy_group.add(enemy)
        self.mario_and_enemy_group.add(self.enemy_group)


    def check_enemy_y_collisions(self, enemy):
        """Enemy collisions on the y axis"""
        collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(enemy, self.brick_group)
        coin_box = pg.sprite.spritecollideany(enemy, self.coin_box_group)

        if collider:
            if enemy.rect.bottom > collider.rect.bottom:
                enemy.y_vel = 7
                enemy.rect.top = collider.rect.bottom
                enemy.state = c.FALL
            elif enemy.rect.bottom < collider.rect.bottom:

                enemy.y_vel = 0
                enemy.rect.bottom = collider.rect.top
                enemy.state = c.WALK

        elif brick:
            if brick.state == c.BUMPED:
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                if self.mario.rect.centerx > brick.rect.centerx:
                    enemy.start_death_jump('right')
                else:
                    enemy.start_death_jump('left')

            elif enemy.rect.x > brick.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = brick.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = brick.rect.top
                enemy.state = c.WALK

        elif coin_box:
            if coin_box.state == c.BUMPED:
                self.game_info[c.SCORE] += 100
                self.moving_score_list.append(
                    score.Score(enemy.rect.centerx - self.viewport.x,
                                enemy.rect.y, 100))
                enemy.kill()
                self.sprites_about_to_die_group.add(enemy)
                if self.mario.rect.centerx > coin_box.rect.centerx:
                    enemy.start_death_jump('right')
                else:
                    enemy.start_death_jump('left')

            elif enemy.rect.x > coin_box.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = coin_box.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = coin_box.rect.top
                enemy.state = c.WALK


        else:
            enemy.rect.y += 1
            test_group = pg.sprite.Group(self.ground_step_pipe_group,
                                         self.coin_box_group,
                                         self.brick_group)
            if pg.sprite.spritecollideany(enemy, test_group) is None:
                if enemy.state != c.JUMP:
                    enemy.state = c.FALL

            enemy.rect.y -= 1


    def adjust_shell_position(self):
        """Moves any koopa in a shell along the x, y axes and checks for
        collisions"""
        for shell in self.shell_group:
            shell.rect.x += shell.x_vel
            self.check_shell_x_collisions(shell)

            shell.rect.y += shell.y_vel
            self.check_shell_y_collisions(shell)
            self.delete_if_off_screen(shell)


    def check_shell_x_collisions(self, shell):
        """Shell collisions along the x axis"""
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(shell, self.enemy_group)

        if collider:
            setup.SFX['bump'].play()
            if shell.x_vel > 0:
                shell.direction = c.LEFT
                shell.rect.right = collider.rect.left
            else:
                shell.direction = c.RIGHT
                shell.rect.left = collider.rect.right

        if enemy:
            setup.SFX['kick'].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(enemy.rect.right - self.viewport.x,
                            enemy.rect.y, 100))
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            enemy.start_death_jump(shell.direction)


    def check_shell_y_collisions(self, shell):
        """Shell collisions along the y axis"""
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)

        if collider:
            shell.y_vel = 0
            shell.rect.bottom = collider.rect.top
            shell.state = c.SHELL_SLIDE

        else:
            shell.rect.y += 1
            if pg.sprite.spritecollideany(shell, self.ground_step_pipe_group) is None:
                shell.state = c.FALL
            shell.rect.y -= 1


    def adjust_powerup_position(self):
        """Moves mushrooms, stars and fireballs along the x, y axes"""
        for powerup in self.powerup_group:
            if powerup.name == c.MUSHROOM:
                self.adjust_mushroom_position(powerup)
            elif powerup.name == c.STAR:
                self.adjust_star_position(powerup)
            elif powerup.name == c.FIREBALL:
                self.adjust_fireball_position(powerup)
            elif powerup.name == '1up_mushroom':
                self.adjust_mushroom_position(powerup)


    def adjust_mushroom_position(self, mushroom):
        """Moves mushroom along the x, y axes."""
        if mushroom.state != c.REVEAL:
            mushroom.rect.x += mushroom.x_vel
            self.check_mushroom_x_collisions(mushroom)

            mushroom.rect.y += mushroom.y_vel
            self.check_mushroom_y_collisions(mushroom)
            self.delete_if_off_screen(mushroom)


    def check_mushroom_x_collisions(self, mushroom):
        """Mushroom collisions along the x axis"""
        collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_mushroom_for_collision_x(mushroom, collider)

        elif brick:
            self.adjust_mushroom_for_collision_x(mushroom, brick)

        elif coin_box:
            self.adjust_mushroom_for_collision_x(mushroom, coin_box)


    def check_mushroom_y_collisions(self, mushroom):
        """Mushroom collisions along the y axis"""
        collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_mushroom_for_collision_y(mushroom, collider)
        elif brick:
            self.adjust_mushroom_for_collision_y(mushroom, brick)
        elif coin_box:
            self.adjust_mushroom_for_collision_y(mushroom, coin_box)
        else:
            self.check_if_falling(mushroom, self.ground_step_pipe_group)
            self.check_if_falling(mushroom, self.brick_group)
            self.check_if_falling(mushroom, self.coin_box_group)


    def adjust_mushroom_for_collision_x(self, item, collider):
        """Changes mushroom direction if collision along x axis"""
        if item.rect.x < collider.rect.x:
            item.rect.right = collider.rect.x
            item.direction = c.LEFT
        else:
            item.rect.x = collider.rect.right
            item.direction = c.RIGHT


    def adjust_mushroom_for_collision_y(self, item, collider):
        """Changes mushroom state to SLIDE after hitting ground from fall"""
        item.rect.bottom = collider.rect.y
        item.state = c.SLIDE
        item.y_vel = 0


    def adjust_star_position(self, star):
        """Moves invincible star along x, y axes and checks for collisions"""
        if star.state == c.BOUNCE:
            star.rect.x += star.x_vel
            self.check_mushroom_x_collisions(star)
            star.rect.y += star.y_vel
            self.check_star_y_collisions(star)
            star.y_vel += star.gravity
            self.delete_if_off_screen(star)


    def check_star_y_collisions(self, star):
        """Invincible star collisions along y axis"""
        collider = pg.sprite.spritecollideany(star, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(star, self.brick_group)
        coin_box = pg.sprite.spritecollideany(star, self.coin_box_group)

        if collider:
            self.adjust_star_for_collision_y(star, collider)
        elif brick:
            self.adjust_star_for_collision_y(star, brick)
        elif coin_box:
            self.adjust_star_for_collision_y(star, coin_box)


    def adjust_star_for_collision_y(self, star, collider):
        """Allows for a star bounce off the ground and on the bottom of a
        box"""
        if star.rect.y > collider.rect.y:
            star.rect.y = collider.rect.bottom
            star.y_vel = 0
        else:
            star.rect.bottom = collider.rect.top
            star.start_bounce(-8)


    def adjust_fireball_position(self, fireball):
        """Moves fireball along the x, y axes and checks for collisions"""
        if fireball.state == c.FLYING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
        elif fireball.state == c.BOUNCING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
            fireball.y_vel += fireball.gravity
        self.delete_if_off_screen(fireball)


    def bounce_fireball(self, fireball):
        """Simulates fireball bounce off ground"""
        fireball.y_vel = -8
        if fireball.direction == c.RIGHT:
            fireball.x_vel = 15
        else:
            fireball.x_vel = -15

        if fireball in self.powerup_group:
            fireball.state = c.BOUNCING


    def check_fireball_x_collisions(self, fireball):
        """Fireball collisions along x axis"""
        collide_group = pg.sprite.Group(self.ground_group,
                                        self.pipe_group,
                                        self.step_group,
                                        self.coin_box_group,
                                        self.brick_group)

        collider = pg.sprite.spritecollideany(fireball, collide_group)

        if collider:
            fireball.kill()
            self.sprites_about_to_die_group.add(fireball)
            fireball.explode_transition()



    def check_fireball_y_collisions(self, fireball):
        """Fireball collisions along y axis"""
        collide_group = pg.sprite.Group(self.ground_group,
                                        self.pipe_group,
                                        self.step_group,
                                        self.coin_box_group,
                                        self.brick_group)

        collider = pg.sprite.spritecollideany(fireball, collide_group)
        enemy = pg.sprite.spritecollideany(fireball, self.enemy_group)
        shell = pg.sprite.spritecollideany(fireball, self.shell_group)

        if collider and (fireball in self.powerup_group):
            fireball.rect.bottom = collider.rect.y
            self.bounce_fireball(fireball)

        elif enemy:
            self.fireball_kill(fireball, enemy)

        elif shell:
            self.fireball_kill(fireball, shell)


    def fireball_kill(self, fireball, enemy):
        """Kills enemy if hit with fireball"""
        setup.SFX['kick'].play()
        self.game_info[c.SCORE] += 100
        self.moving_score_list.append(
            score.Score(enemy.rect.centerx - self.viewport.x,
                        enemy.rect.y,100))
        fireball.kill()
        enemy.kill()
        self.sprites_about_to_die_group.add(enemy, fireball)
        enemy.start_death_jump(fireball.direction)
        fireball.explode_transition()


    def check_if_falling(self, sprite, sprite_group):
        """Checks if sprite should enter a falling state"""
        sprite.rect.y += 1

        if pg.sprite.spritecollideany(sprite, sprite_group) is None:
            if sprite.state != c.JUMP:
                sprite.state = c.FALL

        sprite.rect.y -= 1


    def delete_if_off_screen(self, enemy):
        """Removes enemy from sprite groups if 500 pixels left off the screen,
         underneath the bottom of the screen, or right of the screen if shell"""
        if enemy.rect.x < (self.viewport.x - 300):
            enemy.kill()

        elif enemy.rect.y > (self.viewport.bottom):
            enemy.kill()

        elif enemy.state == c.SHELL_SLIDE:
            if enemy.rect.x > (self.viewport.right + 500):
                enemy.kill()


    def check_flag(self):
        """Adjusts mario's state when the flag is at the bottom"""
        if (self.flag.state == c.BOTTOM_OF_POLE
            and self.mario.state == c.FLAGPOLE):
            self.mario.set_state_to_bottom_of_pole()


    def check_to_add_flag_score(self):
        """Adds flag score if at top"""
        if self.flag_score.y_vel == 0:
            self.game_info[c.SCORE] += self.flag_score_total
            self.flag_score_total = 0


    def check_for_mario_death(self):
        """Restarts the level if Mario is dead"""
        if self.mario.rect.y > c.SCREEN_HEIGHT and not self.mario.in_castle:
            self.mario.dead = True
            self.mario.x_vel = 0
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True

        if self.mario.dead:
            self.play_death_song()


    def play_death_song(self):
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 3000:
            self.set_game_info_values()
            self.done = True


    def set_game_info_values(self):
        """sets the new game values after a player's death"""
        if self.game_info[c.SCORE] > self.persist[c.TOP_SCORE]:
            self.persist[c.TOP_SCORE] = self.game_info[c.SCORE]
        if self.mario.dead:
            try:
                current_lives = int(self.persist.get(c.LIVES, 0))
            except (TypeError, ValueError):
                current_lives = 0
            self.persist[c.LIVES] = max(0, current_lives - 1)
            self.save_player_state()

        if self.persist[c.LIVES] <= 0:
            self.next = c.GAME_OVER
            self.game_info[c.CAMERA_START_X] = 0
        elif self.mario.dead == False:
            self.next = c.MAIN_MENU
            self.game_info[c.CAMERA_START_X] = 0
        elif self.overhead_info_display.time == 0:
            self.next = c.TIME_OUT
        else:
            if self.mario.rect.x > 3670 \
                    and self.game_info[c.CAMERA_START_X] == 0:
                self.game_info[c.CAMERA_START_X] = 3440
            self.next = c.LOAD_SCREEN


    def check_if_time_out(self):
        """Check if time has run down to 0"""
        if self.overhead_info_display.time <= 0 \
                and not self.mario.dead \
                and not self.mario.in_castle:
            self.state = c.FROZEN
            self.mario.start_death_jump(self.game_info)


    def update_viewport(self):
        """Changes the view of the camera"""
        third = self.viewport.x + self.viewport.w//3
        mario_center = self.mario.rect.centerx
        mario_right = self.mario.rect.right

        if self.mario.x_vel > 0 and mario_center >= third:
            mult = 0.5 if mario_right < self.viewport.centerx else 1
            new = self.viewport.x + mult * self.mario.x_vel
            highest = self.level_rect.w - self.viewport.w
            self.viewport.x = min(highest, new)


    def update_while_in_castle(self):
        """Updates while Mario is in castle at the end of the level"""
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        self.overhead_info_display.update(self.game_info)

        if self.overhead_info_display.state == c.END_OF_LEVEL:
            self.state = c.FLAG_AND_FIREWORKS
            self.flag_pole_group.add(castle_flag.Flag(8745, 322))


    def update_flag_and_fireworks(self):
        """Updates the level for the fireworks and castle flag"""
        for score in self.moving_score_list:
            score.update(self.moving_score_list, self.game_info)
        self.overhead_info_display.update(self.game_info)
        self.flag_pole_group.update()

        self.end_game()


    def end_game(self):
        """End the game"""
        if self.flag_timer == 0:
            self.flag_timer = self.current_time
        elif (self.current_time - self.flag_timer) > 2000:
            self.set_game_info_values()
            if not self.clear_saved:
                self.record_level_clear_and_reset_save()
                self.clear_saved = True
            self.next = c.GAME_OVER
            self.sound_manager.stop_music()
            self.done = True


    def blit_everything(self, surface):
        """Blit all sprites to the main surface"""
        self.level.blit(self.background, self.viewport, self.viewport)
        if self.flag_score:
            self.flag_score.draw(self.level)
        self.powerup_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.brick_group.draw(self.level)
        self.coin_box_group.draw(self.level)
        self.sprites_about_to_die_group.draw(self.level)
        self.shell_group.draw(self.level)
        #self.check_point_group.draw(self.level)
        self.brick_pieces_group.draw(self.level)
        self.flag_pole_group.draw(self.level)
        self.mario_and_enemy_group.draw(self.level)
        if self.persist.get("cheat_invincible", False):
            self.draw_cheat_invincible_overlay()

        surface.blit(self.level, (0,0), self.viewport)
        self.overhead_info_display.draw(surface)
        for score in self.moving_score_list:
            score.draw(surface)

    def draw_cheat_invincible_overlay(self):
        center = self.mario.rect.center
        radius = max(self.mario.rect.w, self.mario.rect.h) // 2 + 6
        size = radius * 2 + 2
        overlay = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(overlay, (255, 215, 0, 180), (size // 2, size // 2), radius, 3)
        pg.draw.circle(overlay, (255, 255, 255, 90), (size // 2, size // 2), radius - 6, 2)
        self.level.blit(overlay, (center[0] - size // 2, center[1] - size // 2))


