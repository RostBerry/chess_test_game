import json
from pieces import *
import pyperclip as clip
from common import *
import random
import datetime
import socket

AVAILABLE_IMG = Image.open(IMG_PATH + OTHER_IMG_PATH + 'available.png').resize((ROOT_SIZE, ROOT_SIZE))
AVAILABLE_SURF = pg.Surface((ROOT_SIZE, ROOT_SIZE), pg.SRCALPHA).convert_alpha()
AVAILABLE_SURF.fill((0, 0, 0, 0))
pg.draw.circle(AVAILABLE_SURF, BLACK, (AVAILABLE_SURF.get_width() // 2,
                                       AVAILABLE_SURF.get_height() // 2), ROOT_SIZE // 5)
TAKEABLE_IMG = Image.open(IMG_PATH + OTHER_IMG_PATH + 'takeable.png').resize((ROOT_SIZE, ROOT_SIZE))
TAKEABLE_SURF = pg.Surface((ROOT_SIZE, ROOT_SIZE), pg.SRCALPHA).convert_alpha()
TAKEABLE_SURF.fill(BLACK)
pg.draw.circle(TAKEABLE_SURF, (0, 0, 0, 0), (TAKEABLE_SURF.get_width() // 2,
                                             TAKEABLE_SURF.get_height() // 2), ROOT_SIZE // 2)

MARK_IMG = Image.open(IMG_PATH + OTHER_IMG_PATH + 'mark.png').resize((ROOT_SIZE, ROOT_SIZE))
MARK_SURF = pg.Surface((ROOT_SIZE, ROOT_SIZE), pg.SRCALPHA).convert_alpha()
MARK_SURF.fill((0, 0, 0, 0))
pg.draw.circle(MARK_SURF, (0, 200, 0), (MARK_SURF.get_width() // 2,
                                           MARK_SURF.get_height() // 2), ROOT_SIZE // 3, 6)

MOVABLE_IMG_DICT = {'available': AVAILABLE_IMG,
                    'takeable': TAKEABLE_IMG,
                    'mark': MARK_IMG}

pg.mixer.music.load(MUSIC_PATH + BACKGROUND_MUSIC)
pg.mixer.music.set_volume(0.3)
pg.mixer.music.play(-1)

func_keys = [pg.K_LCTRL, pg.K_RCTRL, pg.K_v, pg.K_RETURN, pg.K_BACKSPACE, pg.K_c]

def colorize_buttons(pos):
    for button in Common.all_buttons:
        color = button.second_color
        if button.rect.collidepoint(pos):
            button.second_color = Common.SELECTED_COLOR
        else:
            if button.selected:
                button.second_color = Common.SELECTED_COLOR
            else:
                button.second_color = Common.MAIN_STROKE_COLOR
        if button.second_color != color:
            button.update()


def get_button_on_click(pos):
    for button in Common.all_buttons:
        if button.rect.collidepoint(pos):
            return button
    return None


def create_back_button(end_x: int, y):
    return Button('BACK', (end_x // 2 - BACK_BTN_SIZE[0] // 2,
                    y), BACK_BTN_SIZE, 24, 3)


def check_copy(input_box):
    if (Common.hotkeys[pg.K_LCTRL] or Common.hotkeys[pg.K_RCTRL]) and Common.hotkeys[pg.K_c]:
        copy_to_buffer(input_box)
        return True
    else:
        return False


def check_paste():
    """Checks if the user's keyboard input is Ctrl+V"""
    if (Common.hotkeys[pg.K_LCTRL] or Common.hotkeys[pg.K_RCTRL]) and Common.hotkeys[pg.K_v]:
        return True
    else:
        return False


def copy_to_buffer(input_box):
    clip.copy(input_box.text)


def keyboard_btn_up(event):
    """Works when the keyboard btn is released"""
    # Releasing all keys
    if event.key == pg.K_LCTRL:
        Common.hotkeys[pg.K_LCTRL] = False
    if event.key == pg.K_RCTRL:
        Common.hotkeys[pg.K_RCTRL] = False
    if event.key == pg.K_v:
        Common.hotkeys[pg.K_v] = False


class Menu:
    """Main menu class"""

    def __init__(self, parent_screen: pg.Surface):
        pg.display.set_caption('Main menu')
        self.__screen = parent_screen
        self.is_game_started = False
        self.is_options_started = False
        self.is_quit = False
        self.__main_game_text_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE)
        self.all_content = pg.Surface(self.__screen.get_size()).convert_alpha()
        self.all_content.fill((0, 0, 0, 0))
        self.__play_button = None
        self.__options_button = None
        self.__quit_button = None
        self.__all_buttons_size = None
        self.__background = None
        self.__prepare_screen()
        self.__grand_update()

    def __prepare_screen(self):
        Common.all_buttons.empty()
        Common.all_input_boxes.empty()
        self.__draw_main_text()
        self.__draw_buttons()

    def __draw_buttons(self):
        button_count = 3
        btw_button_distance = 35
        button_pos = (self.__screen.get_width() // 2 - MAIN_BTN_SIZE[0] // 2,

                      (self.__main_text_size[1] +
                      ((self.__screen.get_height() - self.__main_text_size[1]) // 2) -
                      (MAIN_BTN_SIZE[1] * button_count + btw_button_distance * button_count - 1) // 2) -
                      btw_button_distance
                      )

        self.__play_button = Button('PLAY', button_pos)
        button_pos = (button_pos[0], button_pos[1] + MAIN_BTN_SIZE[1] + btw_button_distance)
        self.__options_button = Button('OPTIONS', button_pos)
        button_pos = (button_pos[0], button_pos[1] + MAIN_BTN_SIZE[1] + btw_button_distance)
        self.__quit_button = Button('QUIT', button_pos)
        self.__all_buttons_size = (MAIN_BTN_SIZE[0],
                                   MAIN_BTN_SIZE[1] * button_count + btw_button_distance * button_count)
        Common.all_buttons.add(self.__play_button, self.__options_button, self.__quit_button)

    def __draw_main_text(self):
        main_game_text_stroke_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE + 2)
        main_game_text_stroke = main_game_text_stroke_font.render('CHESS',
                                                                  True,
                                                                  Common.MAIN_STROKE_COLOR)
        main_game_text = self.__main_game_text_font.render('CHESS',
                                                           True,
                                                           Common.MAIN_COLOR)
        main_text_stroke_pos = (self.__screen.get_width() // 2 -
                                main_game_text_stroke.get_width() // 2, 0)

        main_text_pos = (self.__screen.get_width() // 2 - main_game_text.get_width() // 2, 0)

        self.__main_text_size = main_game_text_stroke.get_size()

        self.all_content.blit(main_game_text_stroke, main_text_stroke_pos)
        self.all_content.blit(main_game_text, main_text_pos)

    def mouse_btn_down(self, btn, pos):
        if btn == 1:
            clicked_button = get_button_on_click(pos)
            if clicked_button is not None:
                if clicked_button.button_type == 'PLAY':
                    self.is_game_started = True
                elif clicked_button.button_type == 'OPTIONS':
                    self.is_options_started = True
                elif clicked_button.button_type == 'QUIT':
                    self.is_quit = True
                self.close()

    def mouse_motion(self, pos):
        colorize_buttons(pos)
        self.__grand_update()

    def close(self):
        Common.all_buttons.empty()

    def __grand_update(self):
        self.__screen.fill(Common.BACKGROUND)
        self.__screen.blit(self.all_content, (0, 0))
        Common.all_buttons.draw(self.__screen)
        pg.display.update()


class Options:
    def __init__(self, parent_screen: pg.Surface):
        pg.display.set_caption('Options')
        self.__screen = parent_screen
        self.__main_text_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE)
        self.__header_font = pg.font.Font(FONT_TEXT_PATH, FONT_HEADER_SIZE)
        self.__text_font = pg.font.Font(FONT_TEXT_PATH, FONT_TEXT_SIZE)
        self.all_content = pg.Surface(self.__screen.get_size()).convert_alpha()
        self.all_content.fill((0, 0, 0, 0))
        self.back = False
        self.__prepare_screen()
        self.__grand_update()

    def __prepare_screen(self):
        self.all_content.fill((0, 0, 0, 0))
        Common.all_buttons.empty()
        Common.all_input_boxes.empty()
        main_text_stroke_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE + 2)
        main_text_stroke = main_text_stroke_font.render('OPTIONS',
                                                        True,
                                                        Common.MAIN_STROKE_COLOR)
        main_text = self.__main_text_font.render('OPTIONS',
                                                 True,
                                                 Common.MAIN_COLOR)
        main_text_pos = (self.__screen.get_width() // 2 -
                         main_text.get_width() // 2, 0)

        main_text_stroke_pos = (self.__screen.get_width() // 2 -
                                main_text_stroke.get_width() // 2, 0)

        self.all_content.blit(main_text_stroke, main_text_stroke_pos)
        self.all_content.blit(main_text, main_text_pos)

        color_palette_switcher_text = self.__header_font.render('Color scheme:',
                                                                True,
                                                                Common.MAIN_STROKE_COLOR)
        color_palette_switcher_text_pos = (main_text_stroke_pos[0],
                                           main_text_stroke.get_height())
        self.all_content.blit(color_palette_switcher_text, color_palette_switcher_text_pos)

        color_palette_switcher_prev = Button('PREV',
                                             (color_palette_switcher_text_pos[0] +
                                             color_palette_switcher_text.get_width(),
                                              color_palette_switcher_text_pos[1]), (45, 35), 16, 2)

        color_scheme_text = self.__header_font.render(Common.PALETTE, True, Common.MAIN_STROKE_COLOR)
        self.all_content.blit(color_scheme_text, (color_palette_switcher_prev.rect.x +
                                                  color_palette_switcher_prev.rect.width,
                                                  color_palette_switcher_prev.rect.y))

        color_palette_switcher_next = Button('NEXT',
                                             (color_palette_switcher_text_pos[0] +
                                              color_palette_switcher_text.get_width() +
                                              color_palette_switcher_prev.rect.width +
                                              color_scheme_text.get_width(),
                                              color_palette_switcher_text_pos[1]), (45, 35), 16, 2)

        Common.all_buttons.add(color_palette_switcher_prev)
        Common.all_buttons.add(color_palette_switcher_next)

        content_list_pos = color_palette_switcher_text_pos[1] + color_palette_switcher_text.get_height() + 20

        username_asking_text = self.__header_font.render('Your Username: ', True,
                                                         Common.MAIN_STROKE_COLOR)
        self.all_content.blit(username_asking_text,
                              (main_text_stroke_pos[0], content_list_pos - 5))
        with open('saved_info.json') as info:
            username = json.load(info)['username']
        self.__username_input_box = InputBox(0,
                                      main_text_stroke_pos[0] + username_asking_text.get_width(),
                                      content_list_pos, username_asking_text.get_width(),
                                      username_asking_text.get_height(), 0, username,
                                      FONT_HEADER_SIZE, 'custom')
        if self.__username_input_box.text == '':
            self.__username_input_box.put_char('Anonymous')
        Common.all_input_boxes.add(self.__username_input_box)
        content_list_pos += username_asking_text.get_height()

        back_button = create_back_button(main_text_stroke_pos[0],
                                         color_palette_switcher_text_pos[1] - BACK_BTN_SIZE[1])
        Common.all_buttons.add(back_button)

    def mouse_motion(self, pos):
        colorize_buttons(pos)
        self.__grand_update()

    def mouse_btn_down(self, mouse_btn, pos):
        button = get_button_on_click(pos)
        self.__username_input_box.deactivate()
        if self.__username_input_box.text == '':
            self.__username_input_box.put_char('Anonymous')
        if self.__username_input_box.rect.collidepoint(pos):
            if mouse_btn == 1:
                self.__username_input_box.activate()
        elif button is not None:
            if mouse_btn == 1:
                if button.button_type in ['PREV', 'NEXT']:
                    palette_index = list(PALETTES_LIST).index(Common.PALETTE)
                    changed_palette_offset = (1 if button.button_type == 'NEXT' else -1)
                    if button.button_type == 'NEXT':
                        if palette_index + changed_palette_offset > len(PALETTES_LIST) - 1:
                            palette_index = 0
                            changed_palette_offset = 0
                    Common.PALETTE = list(PALETTES_LIST)[palette_index + changed_palette_offset]
                    renew_colors()
                    self.__prepare_screen()
                    with open('saved_info.json', 'r') as info:
                        saved_info = json.load(info)
                    saved_info['color scheme'] = Common.PALETTE
                    with open('saved_info.json', 'w') as info:
                        json.dump(saved_info, info)
                elif button.button_type == 'BACK':
                    with open('saved_info.json', 'r') as info:
                        all_info = json.load(info)
                    all_info['username'] = self.__username_input_box.text
                    with open('saved_info.json', 'w') as info:
                        json.dump(all_info, info)
                    self.back = True
        self.__grand_update()

    def keyboard_btn_down(self, event):
        """Works when the keyboard btn is clicked"""
        if self.__username_input_box.active and event.key in func_keys:
            if event.key == pg.K_LCTRL:  # Left Ctrl
                Common.hotkeys[pg.K_LCTRL] = True

            if event.key == pg.K_RCTRL:  # Right Ctrl
                Common.hotkeys[pg.K_RCTRL] = True

            if event.key == pg.K_v:  # v
                Common.hotkeys[pg.K_v] = True
                if not check_paste():
                    self.__username_input_box.put_char(event.unicode)
                else:
                    self.__username_input_box.put_char(clip.paste())

            if event.key == pg.K_BACKSPACE:  # Backspace
                self.__username_input_box.del_char()

            if event.key == pg.K_c:
                Common.hotkeys[pg.K_c] = True
                if not check_copy(self.__username_input_box):
                    self.__username_input_box.put_char(event.unicode)

        elif self.__username_input_box.active:  # Works if user didn't press any functional key
            self.__username_input_box.put_char(event.unicode)

        with open('saved_info.json', 'r') as info:
            all_info = json.load(info)
        all_info['username'] = self.__username_input_box.text
        with open('saved_info.json', 'w') as info:
            json.dump(all_info, info)
        self.__grand_update()

    def __grand_update(self):
        self.__screen.fill(Common.BACKGROUND)
        self.__screen.blit(self.all_content, (0, 0))
        Common.all_buttons.draw(self.__screen)
        Common.all_input_boxes.draw(self.__screen)
        pg.display.update()


class GameModeChanger:
    def __init__(self, parent_screen: pg.Surface):
        pg.display.set_caption('Game Mode')
        self.__screen = parent_screen
        self.__main_text_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE)
        self.__header_font = pg.font.Font(FONT_TEXT_PATH, FONT_HEADER_SIZE)
        self.__text_font = pg.font.Font(FONT_TEXT_PATH, FONT_TEXT_SIZE)
        self.all_content = pg.Surface(self.__screen.get_size()).convert_alpha()
        self.all_content.fill((0, 0, 0, 0))
        self.additional_prefs = pg.Surface(self.__screen.get_size()).convert_alpha()
        self.additional_prefs.fill((0, 0, 0, 0))
        self.back = False
        self.is_started = False
        self.__prepare_screen()
        self.__grand_update()

    def __prepare_screen(self):
        self.all_content.fill((0, 0, 0, 0))
        Common.all_buttons.empty()
        Common.all_input_boxes.empty()
        main_text_stroke_font = pg.font.Font(FONT_TEXT_PATH, FONT_MAIN_GAME_SIZE + 2)
        main_text_stroke = main_text_stroke_font.render('GAME',
                                                        True,
                                                        Common.MAIN_STROKE_COLOR)
        main_text = self.__main_text_font.render('GAME',
                                                 True,
                                                 Common.MAIN_COLOR)
        main_text_pos = (self.__screen.get_width() // 2 -
                         main_text.get_width() // 2, 0)

        main_text_stroke_pos = (self.__screen.get_width() // 2 -
                                main_text_stroke.get_width() // 2, 0)

        self.all_content.blit(main_text_stroke, main_text_stroke_pos)
        self.all_content.blit(main_text, main_text_pos)

        back_button = create_back_button(main_text_stroke_pos[0],
                                         main_text_stroke_pos[1] + main_text_stroke.get_height() - BACK_BTN_SIZE[1])
        Common.all_buttons.add(back_button)

        content_list_pos = main_text_stroke.get_height() + 15
        back_btn_end_x = back_button.rect.x + back_button.rect.width + 10
        game_mode_btn_size = ((self.__screen.get_width() - back_btn_end_x * 2) // 3, 50)
        online_btn = Button('ONLINE', (back_btn_end_x, content_list_pos), game_mode_btn_size, 24, 3, 1)
        back_btn_end_x += game_mode_btn_size[0] + 10
        bot_btn = Button('BOT', (back_btn_end_x, content_list_pos), game_mode_btn_size, 24, 3, 1)
        back_btn_end_x += game_mode_btn_size[0] + 10
        sandbox_btn = Button('SANDBOX', (back_btn_end_x, content_list_pos), game_mode_btn_size, 24, 3, 1)
        Common.all_buttons.add(online_btn)
        Common.all_buttons.add(bot_btn)
        Common.all_buttons.add(sandbox_btn)

        content_list_pos += game_mode_btn_size[1] + 20

        time_control_ask = self.__header_font.render('Time control: ', True, Common.MAIN_STROKE_COLOR)
        self.additional_prefs.blit(time_control_ask,
                                   (back_button.rect.x + back_button.rect.width + 15, content_list_pos))

        minute_control_button_size = (75, 35)
        minute_control_button_pos_x = old_control_pos_x = (back_button.rect.x + back_button.rect.width + 10 +
                                                           time_control_ask.get_width())

        minute_controls = ('10 SEC', '15 SEC', '30 SEC', '45 SEC', '1 MIN', '3 MIN', '5 MIN', '10 MIN',
                           '15 MIN', '30 MIN', '∞')

        for control in minute_controls:
            if minute_control_button_pos_x + minute_control_button_size[0] > sandbox_btn.rect.x + sandbox_btn.rect.width:
                minute_control_button_pos_x = old_control_pos_x
                content_list_pos += minute_control_button_size[1] + 3
            control = Button(control, (minute_control_button_pos_x, content_list_pos),
                             minute_control_button_size, 16 if control != '∞' else 35, 2, 2)
            Common.all_buttons.add(control)
            minute_control_button_pos_x += minute_control_button_size[0] + 3
            
        content_list_pos += minute_control_button_size[1] * 2
        start_btn = Button('START', (self.__screen.get_width() // 2 - MAIN_BTN_SIZE[0] // 2, content_list_pos),
                           MAIN_BTN_SIZE)
        Common.all_buttons.add(start_btn)

    def mouse_motion(self, pos):
        colorize_buttons(pos)
        self.__grand_update()

    def mouse_btn_down(self, mouse_btn, pos):
        button = get_button_on_click(pos)
        if button is not None:
            if mouse_btn == 1:
                if button.selection_group > 0:
                    for btn in Common.all_buttons:
                        if btn.selection_group == button.selection_group:
                            btn.second_color = Common.MAIN_STROKE_COLOR
                            btn.selected = False
                            btn.update()
                    button.selected = True
                    button.second_color = Common.SELECTED_COLOR
                    button.update()
                    if button.selection_group == 1:
                        Common.game_mode['mode'] = button.button_type
                    elif button.selection_group == 2:
                        Common.game_mode['time control'] = button.button_type

                if button.button_type in ['BACK', 'START']:
                    with open('saved_info.json', 'r') as info:
                        all_info = json.load(info)
                    #all_info['username'] = self.__username_input_box.text
                    with open('saved_info.json', 'w') as info:
                        json.dump(all_info, info)
                    if button.button_type == 'BACK':
                        self.back = True
                    elif button.button_type == 'START':
                        self.is_started = True
        self.__grand_update()

    def __grand_update(self):
        self.__screen.fill(Common.BACKGROUND)
        self.__screen.blit(self.all_content, (0, 0))
        self.__screen.blit(self.additional_prefs, (0, 0))
        Common.all_buttons.draw(self.__screen)
        Common.all_input_boxes.draw(self.__screen)
        pg.display.update()


class Button(pg.sprite.Sprite):
    def __init__(self, btn_type: str, button_pos: tuple,
                 size: tuple = MAIN_BTN_SIZE, font_size: int = FONT_MAIN_BUTTONS_SIZE,
                 stroke_size: int = 3, selectable: int = 0):
        super().__init__()
        self.stroke_size = stroke_size
        self.image = pg.Surface(size)
        self.image.fill(Common.MAIN_COLOR)
        self.rect = pg.Rect(button_pos, size)
        self.button_type = btn_type
        self.second_color = Common.MAIN_STROKE_COLOR
        self.text_font = pg.font.Font(FONT_TEXT_PATH, font_size)
        self.text = None
        self.selection_group = selectable
        self.selected = False
        self.update()

    def update(self):
        self.image.fill(Common.MAIN_COLOR)
        self.text = self.text_font.render(self.button_type, True, self.second_color)
        self.image.blit(self.text, (self.image.get_width() // 2 - self.text.get_width() // 2,
                                    self.image.get_height() // 2 - self.text.get_height() // 2))
        pg.draw.rect(self.image, self.second_color,
                     (0, 0, self.rect.width, self.rect.height),
                     self.stroke_size)


class Chessboard:
    """Main chessboard class"""

    def __init__(self, parent_surface: pg.Surface, root_count: int = ROOT_COUNT,
                 root_size: int = ROOT_SIZE):
        # Defining constants from the konfig or __init__ params
        Common.all_buttons.empty()
        Common.all_dialogues.empty()
        self.__screen = parent_surface
        self.__count = root_count
        self.__board_data = board
        self.__size = root_size
        self.__pieces = PIECES_DICT
        self.__input_box_font_size = FONT_TEXT_SIZE
        self.__chessboard_font_size = FONT_CHESSBOARD_SIZE
        self.__chessboard_font = pg.font.Font(FONT_CHESSBOARD_PATH, self.__chessboard_font_size)
        self.__text_font = pg.font.Font(FONT_TEXT_PATH, self.__input_box_font_size)
        self.__timer_font = pg.font.Font(FONT_CHESSBOARD_PATH, FONT_TIMER_SIZE)
        self.__background = None
        self.__play_board_view = None
        self.__play_board_view_pos = None
        # Defining sprite groups
        self.__all_pieces_list = []
        self.__all_selects = pg.sprite.Group()
        self.__all_checks = pg.sprite.Group()
        self.__all_input_boxes = pg.sprite.Group()
        self.__all_marks = pg.sprite.Group()
        self.__all_choices = pg.sprite.Group()
        # Defining interactive objects or variables
        self.__input_box = None
        self.__flip_button = None
        self.__choice = None
        self.__choosing_cell = None
        self.__choosing_pawn = None
        self.__chosen_new_piece = None
        self.__new_created_piece = None
        self.__all_possible_pieces = {}
        self.__all_fen_positions = {}
        self.__pressed_input_box = None
        self.__pressed_root = None
        self.__released_root = None
        self.__selected_piece = None
        self.__taken_piece = None
        self.__prev_piece_value = None
        self.__clicked = False
        self.__can_drag = False
        self.back = False
        self.is_piece_killed = False
        self.is_checked = False
        self.__turn = None
        self.__turn_increment_check = True
        self.__do_cycling = True
        # Initialization methods
        pg.display.set_caption('Chess Session')
        time_control = Common.game_mode['time control']
        self.__game_mode = Common.game_mode['mode']
        self.__do_time_control = True if len(time_control) > 1 else False
        if self.__do_time_control:
            self.__time_control = int(time_control[:2]) * (1 if time_control[3:] == 'SEC' else 60)
            self.__white_time = float(self.__time_control)
            self.__black_time = float(self.__time_control)
        else:
            self.__time_control = None

        self.__prepare_screen()
        self.__draw_play_board()

        self.__draw_all_buttons()
        if self.__game_mode != 'SANDBOX':
            self.__input_box.text = default_board

        self.__setup_board_with_fen()

        self.__draw_waiting_window()
        self.__reset_timer()
        if self.color == 'b':
            self.__flip()
            self.__setup_board_with_fen()
            self.grand_update()
            self.wait_next_move()
        self.grand_update()

    def __play_move_sound(self):
        """Activates when a piece have been moved"""
        if self.is_checked:
            sound = pg.mixer.Sound(MUSIC_PATH + 'effects/check.wav')
        elif self.is_piece_killed:
            sound = pg.mixer.Sound(MUSIC_PATH + MOVE_SOUND + '7.ogg')
        else:
            sound = pg.mixer.Sound(MUSIC_PATH + MOVE_SOUND + str(random.randint(1, 6)) + '.ogg')
        sound.play()
        self.is_checked = False
        self.is_piece_killed = False

    def __prepare_screen(self):
        """Draws background"""
        Common.all_marks.empty()
        self.__background = pg.Surface(self.__screen.get_size())
        self.__background.fill(Common.BACKGROUND)
        self.__screen.blit(self.__background, (0, 0))

    def __draw_waiting_window(self):
        if self.__game_mode == 'ONLINE':
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            waiting_window = DialogueWindow(self.__screen, 'waiting')
            Common.all_dialogues.add(waiting_window)
            self.grand_update()

            self.client.connect((HOST, PORT))
            print(clients_text := self.client.recv(1024).decode('utf-8'))
            print(self.client.recv(1024).decode('utf-8'))
            Common.all_dialogues.empty()
            self.color = clients_text[-5]
        elif self.__game_mode == 'BOT':
            self.color = 'w'
        else:
            self.color = 'wb'

    def __draw_play_board(self):
        """Draws play board"""
        self.total_width = self.__count * self.__size
        # Creating main board objects
        self.num_fields = self.__create_num_fields()
        Common.all_roots = self.__create_all_roots()
        self.num_fields_depth = self.num_fields[0].get_width()
        self.__play_board_view = pg.Surface((2 * self.num_fields_depth + self.total_width,
                                             2 * self.num_fields_depth + self.total_width), pg.SRCALPHA)

        self.__blit_to_play_board()

        # Moves the board to the window center
        self.play_board_rect = self.__play_board_view.get_rect()
        self.play_board_rect.x += (self.__screen.get_width() - self.play_board_rect.width) // 2
        self.play_board_rect.y += (self.__screen.get_height() - self.play_board_rect.height) // 4
        self.__play_board_view_pos = (self.play_board_rect.x, self.play_board_rect.y)
        self.__screen.blit(self.__play_board_view, self.play_board_rect)
        roots_coord_offset = (
            self.play_board_rect.x + self.num_fields_depth,
            self.play_board_rect.y + self.num_fields_depth,)
        self.__apply_offset_for_roots(roots_coord_offset)

        self.__draw_input_box(self.play_board_rect)

        self.__black_timer_pos = (self.play_board_rect.x - TIMER_SIZE[0] - 15, self.play_board_rect.y + TIMER_SIZE[1])
        self.__white_timer_pos = (self.play_board_rect.x - TIMER_SIZE[0] - 15,
                                  self.play_board_rect.y + self.play_board_rect.height - TIMER_SIZE[1] * 2)

        pg.display.update()

    def __draw_timer(self):
        if self.__do_time_control:
            white_timer = pg.Surface(TIMER_SIZE).convert_alpha()
            black_timer = pg.Surface(TIMER_SIZE).convert_alpha()
            black_timer.fill(Common.MAIN_STROKE_COLOR)
            white_timer.fill(Common.MAIN_STROKE_COLOR)

            if self.__white_time <= 0:
                self.__white_time = 0
                self.__turn = '-'
                if not Common.game_ended:
                    win = DialogueWindow(self.__screen, 'b by time')
                    Common.all_dialogues.add(win)
                Common.game_ended = True
            elif self.__black_time <= 0:
                self.__black_time = 0
                self.__turn = '-'
                if not Common.game_ended:
                    win = DialogueWindow(self.__screen, 'w by time')
                    Common.all_dialogues.add(win)
                Common.game_ended = True

            new_times = [None, None]
            for time_index, time_value in enumerate((self.__white_time, self.__black_time)):
                old_time_value = time_value
                minutes = 0
                while time_value >= 60:
                    time_value -= 60
                    minutes += 1
                string_time_val = str(time_value).replace('.', '')
                time_to_draw = f'{minutes}:{string_time_val[:2]}'
                if old_time_value < 10:
                    do_sort = False
                    for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        if num in string_time_val:
                            do_sort = True
                            break
                    if do_sort:
                        time_to_draw = list(time_to_draw)
                        time_to_draw.insert(2, '0')
                        time_to_draw.insert(4, '.')
                        time_to_draw.insert(5, string_time_val[1])
                        time_to_draw[6] = string_time_val[2]
                        new_time_to_draw = ''
                        for char in time_to_draw:
                            new_time_to_draw += char
                        time_to_draw = new_time_to_draw
                    else:
                        time_to_draw = '0:00.00'
                elif old_time_value < 60:
                    time_to_draw += f'.{string_time_val[2:3]}'
                new_times[time_index] = time_to_draw

            white_time_value = self.__timer_font.render(new_times[0], True,
                                                        Common.MAIN_COLOR if self.__turn == 'w'
                                                        else Common.BACKGROUND)
            black_time_value = self.__timer_font.render(new_times[1], True,
                                                        Common.MAIN_COLOR if self.__turn == 'b'
                                                        else Common.BACKGROUND)
            white_timer.blit(white_time_value,
                             (TIMER_SIZE[0] // 2 - white_time_value.get_width() // 2,
                              TIMER_SIZE[1] // 2 - white_time_value.get_height() // 2))
            black_timer.blit(black_time_value,
                             (TIMER_SIZE[0] // 2 - black_time_value.get_width() // 2,
                              TIMER_SIZE[1] // 2 - black_time_value.get_height() // 2))

            self.__screen.blit(white_timer, self.__white_timer_pos)
            self.__screen.blit(black_timer, self.__black_timer_pos)



    def decrease_timer(self):
        if self.__do_time_control and not Common.game_ended:
            #print(self.__turn, self.color, self.__white_time, self.__black_time)
            if self.__turn == 'w':
                self.__white_time -= 0.016666666667
            elif self.__turn == 'b':
                self.__black_time -= 0.016666666667

    def __reset_timer(self):
        if self.__do_time_control:
            old = datetime.datetime.now()
            self.__turn = '-'
            self.__white_time = float(self.__time_control)
            self.__black_time = float(self.__time_control)
            self.grand_update()
            if self.__do_cycling:
                while True:
                    if (datetime.datetime.now() - old).total_seconds() > 1:
                        self.__turn = 'w'
                        break
            self.__do_cycling = False

    def __draw_input_box(self, board_rect: pg.Rect):
        """Draws input box in the bottom"""
        self.__input_box = InputBox(board_rect, 0, 0, 0, 0, 0, 0)
        Common.all_input_boxes.add(self.__input_box)

    def __draw_all_buttons(self):
        btn_count_right = 0
        self.__fen_reset_button = Button('RESET',
                                         (self.__play_board_view_pos[0] + self.play_board_rect.width +
                                         (self.__screen.get_width() -
                                          (self.play_board_rect.x + self.play_board_rect.width))
                                         // 2 - MAIN_BTN_SIZE[0] // 2, self.play_board_rect.y +
                                         MAIN_BTN_SIZE[1] * btn_count_right + 10 * btn_count_right))
        Common.all_buttons.add(self.__fen_reset_button)
        btn_count_right += 1
        self.__copy_button = Button('COPY',
                                    (self.__input_box.rect.x +
                                     self.__input_box.rect.width,
                                     self.__input_box.rect.y),
                                    (self.__input_box.rect.height,
                                     self.__input_box.rect.height), 14, 2)
        self.__flip_button = Button('FLIP',
                                    (self.__input_box.rect.x +
                                     self.__input_box.rect.width + self.__input_box.rect.height,
                                     self.__input_box.rect.y),
                                    (self.__input_box.rect.height,
                                     self.__input_box.rect.height), 14, 2)

        back_button = create_back_button(self.__play_board_view_pos[0], self.__play_board_view_pos[1])
        Common.all_buttons.add(back_button)
        Common.all_buttons.add(self.__copy_button)
        Common.all_buttons.add(self.__flip_button)

    def __blit_to_play_board(self):
        self.__play_board_view.fill(Common.BOARD_BACKGROUND_COLOR)
        self.__play_board_view.blit(self.num_fields[0],
                                    (0, self.num_fields_depth))
        self.__play_board_view.blit(self.num_fields[0],
                                    (self.num_fields_depth + self.total_width, self.num_fields_depth))
        self.__play_board_view.blit(self.num_fields[1],
                                    (self.num_fields_depth, 0))
        self.__play_board_view.blit(self.num_fields[1],
                                    (self.num_fields_depth, self.num_fields_depth + self.total_width))

    def __create_num_fields(self):
        """Creates the rows and lines near the board (like 1-8, a-g)"""
        lines = pg.Surface((self.__count * self.__size, self.__size // 2)).convert_alpha()
        rows = pg.Surface((self.__size // 2, self.__count * self.__size)).convert_alpha()
        lines.fill((0, 0, 0, 0))
        rows.fill((0, 0, 0, 0))
        # Numerates the lines and rows
        for i in range(self.__count):
            letter = self.__chessboard_font.render(letters[i if not Common.is_flipped
                                                           else self.__count - i - 1].upper(),
                                                   True,
                                                   Common.BOARD_TEXT_COLOR)
            number = self.__chessboard_font.render(str((self.__count - i)
                                                       if not Common.is_flipped
                                                       else i + 1),
                                                   True,
                                                   Common.BOARD_TEXT_COLOR)
            # Puts a letter to the line
            lines.blit(letter, (
                i * self.__size + (self.__size - letter.get_rect().width) // 2,
                (lines.get_height() - letter.get_rect().height) // 2
            ))
            # Puts a number to the row
            rows.blit(number, (
                (rows.get_width() - number.get_rect().width) // 2,
                i * self.__size + (self.__size - number.get_rect().height) // 2
            ))
        return [rows, lines]

    def __create_all_roots(self):
        """Draws all roots on the board"""
        root_group = pg.sprite.Group()
        # Statement needed for correct color on the root
        is_even_count = (self.__count % 2 == 0)
        root_color_order = False if is_even_count else True
        # Creates the roots and adds them to the sprite group
        for y in range(self.__count):
            for x in range(self.__count):
                root_name = self.__to_root_name((y if not Common.is_flipped else self.__count - y - 1,
                                                 x if not Common.is_flipped else self.__count - x - 1))
                Common.roots_dict[root_name[0]] = root_name[1]
                root = Root(
                    root_color_order, self.__size,
                    (x, y), root_name
                )
                root_group.add(root)
                root_color_order ^= True  # Changing the root color
                pg.display.update()

            root_color_order = root_color_order ^ True if is_even_count else root_color_order
        return root_group

    def __apply_offset_for_roots(self, offset):
        """Moves the roots onto the board, not on the background"""
        for root in Common.all_roots:
            root.rect.x += offset[0]
            root.rect.y += offset[1]

    def __setup_board(self):
        """Draws the pieces on the roots from board_data"""
        self.__all_pieces_list = []
        for j in range(len(self.__board_data)):
            for i, root_value in enumerate(self.__board_data[j]):
                if root_value != 0:
                    # Creating a piece based on board_data and adding it to the group
                    piece = self.__create_piece(root_value, (j, i))
                    Common.all_pieces.add(piece)
                    self.__all_possible_pieces[piece.piece_name] = piece
        for piece in Common.all_pieces:
            for root in Common.all_roots:
                # Places the piece on the root
                if piece.root_name[1] == root.root_name[1]:
                    piece.rect = root.rect.copy()

    def __setup_board_with_fen(self):
        """Decodes the Forsyth Edwards Notation and setups new board konfig"""
        # Separating the fen string to pieces placement and additional info
        if Stockfish._is_fen_syntax_valid(self.__input_box.text):

            pieces_and_other_map = self.__input_box.text.split(' ')
            Common.pieces_map = pieces_and_other_map[0].split('/')
            Common.other_map = pieces_and_other_map[1:]
            Common.other_map[4] = int(Common.other_map[4])
            # Replacing the board data with new pieces placement
            for row in range(len(self.__board_data)):  # Running through board data rows
                value = 0
                piece_map_offset = 0
                while value < len(self.__board_data[row]):  # Running through board data values in rows
                    offset = 0
                    try:
                        for i in range(int(Common.pieces_map[row][value - piece_map_offset])):  # Placing the empty
                            self.__board_data[row][value + i] = 0  # roots if those have
                            offset = i  # been found
                        value += offset
                        piece_map_offset += offset
                    except ValueError:  # Placing regular piece if the value in pieces map isn't an integer
                        self.__board_data[row][value] = Common.pieces_map[row][value - piece_map_offset]
                    value += 1

            # Saving additional info
            self.__turn = Common.other_map[0]
            print("White's turn" if Common.other_map[0] == 'w' else "Black's turn")
            self.__castling_logic()
            print('The last pawn move is: {}'.format('None' if '-' in Common.other_map[2] else Common.other_map[2]))

            print(f'Halfmoves done: {Common.other_map[3]}')

            endings = {'1': 'st', '2': 'nd', '3': 'rd'}
            print(  # What move is it
                f'{Common.other_map[4]}{endings[Common.other_map[4]] if Common.other_map[4] in endings else "th"} move '
            )

            if int(Common.other_map[3]) >= 50:
                print('Draw by the 50 turns rule')

            Common.all_pieces.empty()
            self.__setup_board()
            self.grand_update()
        else:
            print('Invalid FEN')

    def __write_fen_from_board(self):
        """Converts board data to a fen string"""
        fen_string = ''
        for row in range(len(self.__board_data)):
            value = 0
            empty_int = 0
            while value < len(self.__board_data[row]):
                if self.__board_data[row][value] == 0:
                    empty_int += 1
                else:
                    if empty_int > 0:
                        fen_string += str(empty_int)
                        empty_int = 0
                    fen_string += self.__board_data[row][value]
                value += 1
            if empty_int > 0:
                fen_string += str(empty_int)
            fen_string += '/' if self.__board_data[row] != self.__board_data[-1] else ''

        for info in Common.other_map:
            fen_string += ' ' + str(info)

        self.__input_box.text = fen_string  # Putting the fen string to the input bar
        self.__input_box.put_char('')  # Updating the text

        if self.__game_mode == 'SANDBOX':
            with open('saved_info.json', 'r') as info:
                all_info = json.load(info)
            with open('saved_info.json', 'w') as info:
                all_info['fen string'] = fen_string
                json.dump(all_info, info)

    def __create_piece(self, piece_sym: str, board_data_coord: tuple):
        """Creates a single piece"""
        root_name = self.__to_root_name(board_data_coord)
        piece_tuple = self.__pieces[piece_sym]
        class_name = globals()[piece_tuple[0]]
        return class_name(piece_tuple[1], root_name)

    def __to_root_name(self, board_data_coord: tuple):
        """Returns the name of the root"""
        return (letters[board_data_coord[1]] + str(self.__count - board_data_coord[0]),
                (board_data_coord[1] + 1, board_data_coord[0] + 1))

    def __get_root(self, pos: tuple):
        """Returns the root below the mouse position"""
        for root in Common.all_roots:
            if root.rect.collidepoint(pos):
                return root
        return None

    def __get_root_by_pos(self, pos: tuple):
        """Returns the root by (x, y) sample"""
        for root in Common.all_roots:
            if root.root_name[1] == pos:
                return root
        return None

    def __get_input_box(self, pos: tuple):
        """Returns the input box from mouse position"""
        if self.__input_box.rect.collidepoint(pos):
            return self.__input_box
        return None

    def __colorize_choosing_cell(self, pos: tuple):
        """Colorize one of the cells to choose a new piece for"""
        for cell in Common.all_choosing_cells:
            if cell.rect.collidepoint(pos):
                cell.image.fill(GRAY)
            else:
                cell.image.fill(WHITE)

    def __get_choosing_cell_on_click(self, pos: tuple):
        """Returns the clicked choosing cell"""
        for cell in Common.all_choosing_cells:
            if cell.rect.collidepoint(pos):
                return cell
        return None

    def __get_new_piece(self, choosing_cell):
        for choosing_piece in Common.all_choosing_pieces:
            if choosing_piece.counter == choosing_cell.counter:
                return choosing_piece
        return None

    def __get_piece_on_click(self, root):
        """Returns the clicked piece"""
        for piece in Common.all_pieces:
            if piece.root_name[1] == root.root_name[1]:
                if self.__game_mode != 'SANDBOX':
                    if piece.color == self.__turn == self.color:
                        if self.__taken_piece is not None:
                            self.__taken_piece.move_to_root(self.__pressed_root)
                        return piece
                else:
                    if self.__taken_piece is not None:
                        self.__taken_piece.move_to_root(self.__pressed_root)
                    return piece
        return None

    def __get_piece_pos_by_name(self, name):
        for finding_piece in Common.all_pieces:
            if finding_piece.piece_name == name:
                return finding_piece.root_name[1]

    def __get_piece_by_piece_pos(self, piece_pos):
        for piece in Common.all_pieces:
            if piece.root_name[1] == piece_pos:
                return piece

    def drag(self, pos: tuple):
        """Works when the mouse is moving"""
        if self.__choice is not None:
            self.__colorize_choosing_cell(pos)

        elif self.__taken_piece is not None:
            self.__taken_piece.rect.center = pos

        elif self.__selected_piece is not None:
            if self.__can_drag:
                self.__selected_piece.rect.center = pos

        else:
            colorize_buttons(pos)

        self.grand_update()

    def mouse_btn_down(self, button_type: int, pos: tuple):
        """Works when the mouse btn is clicked"""
        self.__clicked = True  # Statement needed to correct root selection
        # Checking if the user clicked on root or input box
        if button_type == 1:
            if self.__choice is not None:
                self.__choosing_cell = self.__get_choosing_cell_on_click(pos)
                if self.__choosing_cell is not None:
                    self.__chosen_new_piece = self.__get_new_piece(self.__choosing_cell)

            else:
                pressed_root = self.__get_root(pos)

                self.__pressed_root = (self.__get_root(pos))
                                       #if self.__selected_piece is None
                                       #else self.__pressed_root)

            button = get_button_on_click(pos)
            if button is not None:
                if button.button_type == 'FLIP':
                    self.__flip()
                elif button.button_type == 'COPY':
                    copy_to_buffer(self.__input_box)
                elif button.button_type == 'RESET':
                    self.__all_fen_positions = {}
                    self.__input_box.text = default_board
                    self.__input_box.put_char('')
                    self.__setup_board_with_fen()
                    with open('saved_info.json', 'r') as info:
                        all_info = json.load(info)
                    with open('saved_info.json', 'w') as info:
                        all_info['fen string'] = self.__input_box.text
                        json.dump(all_info, info)
                    self.__do_cycling = True
                    self.__reset_timer()
                elif button.button_type == 'X':
                    Common.all_dialogues.empty()
                    button.kill()
                elif button.button_type == 'BACK':
                    self.back = True
        self.__pressed_input_box = self.__get_input_box(pos)
        # User clicked on the input box
        if self.__pressed_input_box is not None:
            self.__input_box.activate()
        # User clicked on the root
        elif self.__pressed_root is not None:
            self.__input_box.deactivate()
            if button_type == 1:  # LMB
                self.__taken_piece = self.__get_piece_on_click(self.__pressed_root)

                if self.__taken_piece is not None:
                    self.__unmark_all_marks()
                    self.__taken_piece_logic(pos)

                elif self.__selected_piece is not None:
                    self.__unmark_all_marks()
                    self.__draw_available_roots(self.__selected_piece)
                    if self.__pressed_root is not None:
                        self.__unselect_all_roots()
                        self.__unmark_all_marks()
                        self.__taken_piece = self.__get_piece_on_click(self.__pressed_root)
                        if self.__taken_piece is not None:
                            self.__selected_piece = None
                            self.__taken_piece_logic(pos)
                        else:
                            self.__selected_piece.rect.center = pos
                            self.__can_drag = True
                            if self.__selected_piece.piece_name in ['k', 'K']:
                                self.__prev_piece_value = self.__selected_piece.root_name

                else:
                    self.__unmark_all_marks()

            elif button_type == 3:
                if self.__selected_piece is not None or self.__taken_piece is not None:
                    self.__move_or_select_piece(self.__pressed_root)
                    self.__unmark_all_marks()
                    self.__unselect_all_roots()
            self.grand_update()

    def __taken_piece_logic(self, pos):
        self.__select_root(self.__pressed_root)
        self.__prev_piece_value = self.__taken_piece.root_name
        for root in Common.all_roots:
            if root.root_name == self.__taken_piece.root_name:
                self.__prev_piece_root = root
        self.__draw_available_roots(self.__taken_piece)

        self.__taken_piece.rect.center = pos

    def mouse_btn_up(self, button_type: int, pos: tuple):
        """Works when the mouse btn is released"""
        self.__released_root = self.__get_root(pos)
        if button_type == 1:  # LMB
            self.__can_drag = False
        if self.__released_root is not None:
            if button_type == 3:  # RMB
                self.__mark_root(self.__released_root)
            if self.__choice is not None:
                self.__chosen_new_piece = self.__get_new_piece(self.__choosing_cell)
                if self.__chosen_new_piece is not None:
                    new_piece_coords = self.__choosing_pawn.root_name
                    self.__new_created_piece = self.__create_new_piece(self.__chosen_new_piece,
                                                                       new_piece_coords,
                                                                       self.__choosing_pawn)
                    Common.all_pieces.add(self.__new_created_piece)
                    self.__choice = None
                    self.__all_choices.empty()
                    Common.all_choosing_cells.empty()
                    Common.all_choosing_pieces.empty()
                    self.__write_to_board_data()
            if self.__clicked:
                if button_type == 1:
                    self.__move_or_select_piece(self.__released_root)
        else:
            if button_type == 1:
                self.__move_or_select_piece(self.__pressed_root)
        self.__clicked = False
        self.grand_update()

    def keyboard_btn_down(self, event):
        """Works when the keyboard btn is clicked"""
        if self.__input_box.active and event.key in func_keys:
            if event.key == pg.K_LCTRL:  # Left Ctrl
                Common.hotkeys[pg.K_LCTRL] = True

            if event.key == pg.K_RCTRL:  # Right Ctrl
                Common.hotkeys[pg.K_RCTRL] = True

            if event.key == pg.K_v:  # v
                Common.hotkeys[pg.K_v] = True
                if not check_paste():
                    self.__input_box.put_char(event.unicode)
                else:
                    self.__input_box.put_char(clip.paste())

            if event.key == pg.K_RETURN:  # Enter
                self.__setup_board_with_fen()

            if event.key == pg.K_BACKSPACE:  # Backspace
                self.__input_box.del_char()

            if event.key == pg.K_c:
                Common.hotkeys[pg.K_c] = True
                if not check_copy(self.__input_box):
                    self.__input_box.put_char(event.unicode)

        elif self.__input_box.active:  # Works if user didn't press any functional key
            self.__input_box.put_char(event.unicode)
        self.grand_update()

    def __flip(self):
        self.__unmark_all_marks()
        self.__taken_piece = None
        self.__selected_piece = None
        Common.is_flipped ^= True
        for root in Common.all_roots:
            root_name_tuple = (self.__count - root.root_name[1][0],
                               self.__count - root.root_name[1][1])
            root.root_name = self.__to_root_name(root_name_tuple[::-1])
            Common.roots_dict[root.root_name[0]] = root.root_name[1]
        for piece in Common.all_pieces:
            for root in Common.all_roots:
                if piece.root_name[0] == root.root_name[0]:
                    piece.rect = root.rect.copy()
        self.num_fields = self.__create_num_fields()
        self.__blit_to_play_board()

    def __mark_root(self, root):
        """Draws a green circle on the clicked root"""
        if not root.mark:
            mark = Mark(root, 'mark')
            Common.all_marks.add(mark)
        else:
            for mark in Common.all_marks:
                if mark.root_name[0] == root.root_name[0]:
                    mark.kill()
                    break
        root.mark ^= True

    def __select_root(self, root):
        """Selects the root and colors it to the transparent green"""
        select = Select(root)
        self.__all_selects.add(select)

    def __draw_available_roots(self, piece: Piece):
        if not Common.game_ended or self.__game_mode == 'SANDBOX':
            piece.check_movables(True)
            for available in piece.movable_roots:
                moving_dist = (available[0], available[1])
                for root in Common.all_roots:
                    if root.root_name[1] == moving_dist:
                        available_root = Mark(root, 'available')
                        Common.all_marks.add(available_root)
            for takeable in piece.takeable_roots:
                moving_dist = (takeable[0], takeable[1])
                for root in Common.all_roots:
                    if root.root_name[1] == moving_dist:
                        takeable_root = Mark(root, 'takeable')
                        Common.all_marks.add(takeable_root)

    def __move_or_select_piece(self, root):
        self.__unselect_all_roots()
        if self.__taken_piece is not None:
            if root.root_name[1] in self.__taken_piece.movable_roots + self.__taken_piece.takeable_roots:
                for piece in Common.all_pieces:
                    if piece.root_name == root.root_name:
                        self.kill_piece(piece)
                self.__taken_piece.move_to_root(root)
            else:
                self.__taken_piece.move_to_root(self.__pressed_root)
            if self.__taken_piece.is_moved:
                self.__after_move_preps(self.__taken_piece)
            else:
                self.__select_root(self.__pressed_root)
                self.__selected_piece = self.__taken_piece
            self.__taken_piece = None
        elif self.__selected_piece is not None:
            self.__unmark_all_marks()
            if root is not None and root.root_name[1] in self.__selected_piece.movable_roots + self.__selected_piece.takeable_roots:
                for piece in Common.all_pieces:
                    if piece.root_name == root.root_name:
                        self.kill_piece(piece)
                self.__selected_piece.move_to_root(root)
            else:
                self.__selected_piece.move_to_root(self.__prev_piece_root)
            if self.__selected_piece.is_moved:
                self.__after_move_preps(self.__selected_piece)
            self.__selected_piece = None

    def kill_piece(self, piece):
        piece.kill()
        Common.all_pieces.remove(piece)
        self.is_piece_killed = True

    def __create_new_piece(self, new_piece, new_piece_coords, pawn):
        piece = self.__create_piece(new_piece.piece_name, (new_piece_coords[1][1],
                                                           new_piece_coords[1][0]))
        piece.move_to_root(pawn)
        self.kill_piece(pawn)
        self.__check_check(piece)
        return piece

    def __write_to_board_data(self):
        for root in Common.all_roots:
            root_pos = root.root_name[1]
            found_piece = None
            for piece in Common.all_pieces:
                if piece.root_name[1] == root.root_name[1]:
                    found_piece = piece
            if found_piece is not None:
                self.__board_data[root_pos[1] - 1][root_pos[0] - 1] = found_piece.piece_name
            else:
                self.__board_data[root_pos[1] - 1][root_pos[0] - 1] = 0

        self.__write_fen_from_board()

    def __after_move_preps(self, piece):
        self.__unmark_all_marks()
        Common.other_map[2] = '-'

        if piece.piece_name in ['p', 'P']:
            self.__pawns_after_move_logic(piece)
        else:
            self.__increase_50_rule()

        if piece.piece_name in ['k', 'K']:
            self.__kings_after_move_logic(piece)

        if piece.piece_name in ['R', 'r']:
            self.__rooks_after_move_logic(piece)

        if not Common.other_map[1]:
            Common.other_map[1] = '-'
        piece.first_move = False
        self.__new_created_piece = None
        self.__uncheck_the_king(piece.color)
        self.__check_check(piece)
        self.__check_mate(piece.color)
        self.__play_move_sound()
        self.__change_turn()
        self.__turn_increment_check ^= True
        if self.__turn_increment_check:
            Common.other_map[4] += 1
        self.__write_to_board_data()
        self.__record_fen()
        self.__check_draw()
        if self.__game_mode != 'SANDBOX':
            if piece.color == self.color:
                self.__send_to_opponent()
                self.grand_update()
                self.wait_next_move()

    def __send_to_opponent(self):
        if self.__game_mode == 'ONLINE':
            time_to_send = self.__white_time if self.color == 'w' else self.__black_time
            self.client.send((str(time_to_send) + '|' + self.__input_box.text).encode('utf-8'))

    def wait_next_move(self):
        if self.__game_mode == 'ONLINE':
            rec_data = self.client.recv(1024).decode('utf-8').split('|')
            print(rec_data)
            if rec_data != 'None':
                Common.go_next_waiting_loop = False
                if self.color == 'b':
                    self.__white_time = float(rec_data[0])
                else:
                    self.__black_time = float(rec_data[0])
                self.__input_box.text = rec_data[1]
                self.__setup_board_with_fen()
            else:

                Common.go_next_waiting_loop = True

    def __record_fen(self):
        whitespace = self.__input_box.text.index(' ')
        fen = self.__input_box.text[:whitespace]
        if fen in self.__all_fen_positions.keys():
            self.__all_fen_positions[fen] += 1
        else:
            self.__all_fen_positions[fen] = 1
        print('')
        for position in self.__all_fen_positions:
            print(f'{position}: {self.__all_fen_positions[position]}')

    def __pawns_after_move_logic(self, pawn: Pawn):
        Common.other_map[3] = 0
        if pawn.root_name[1] == pawn.taking_on_the_pass_move:
            self.kill_piece(self.__get_piece_by_piece_pos(pawn.passing_pawn_pos))
        if pawn.first_move and pawn.root_name[1][1] - pawn.prev_root_name[1][1] in [2, -2]:
            Common.other_map[2] = pawn.root_name[0]
        if pawn.root_name[1][1] == (len(self.__board_data)
                                    if pawn.color == 'b'
                                    else 1):
            self.__choice = Choice(pawn)
            self.__choosing_pawn = pawn
        pawn.taking_on_the_pass_move = None
        pawn.passing_pawn_pos = None

    def __increase_50_rule(self):
        if not self.is_piece_killed:
            Common.other_map[3] = int(Common.other_map[3] + 1)
        else:
            Common.other_map[3] = 0

    def __kings_after_move_logic(self, king: King):
        king.is_long_castling_possible = False
        king.is_short_castling_possible = False
        Common.other_map[1] = Common.other_map[1].replace('K' if king.color == 'w' else 'k', '')
        Common.other_map[1] = Common.other_map[1].replace('Q' if king.color == 'w' else 'q', '')
        if king.root_name[1] in king.castling_roots:
            self.__do_castle(king, 'Long' if king.root_name[1][0] -
                             self.__prev_piece_value[1][0] < 0 else 'Short')
        king.castling_roots = []
        self.__prev_piece_value = None

    def __uncheck_the_king(self, color):
        for prob_king in Common.all_pieces:
            if prob_king.piece_name == ('k' if color == 'w' else 'K'):
                prob_king.is_checked = False

    def __rooks_after_move_logic(self, rook: Rook):
        king_pos = self.__get_piece_pos_by_name('K' if rook.color == 'w' else 'k')
        if (rook.first_move and
                rook.root_name[1][0] - king_pos[0] > 0):
            Common.other_map[1] = Common.other_map[1].replace('K' if rook.color == 'w' else 'k', '')
        else:
            Common.other_map[1] = Common.other_map[1].replace('Q' if rook.color == 'w' else 'q', '')

    def __castling_logic(self):
        colors = {'whites': ('KQ', 'K', 'Q'), 'blacks': ('kq', 'k', 'q')}
        for i in colors:  # What castlings can be done
            print(f'Both castlings possible for {i}' if colors[i][0] in Common.other_map[1]
                  else f'Short castling for {i}' if colors[i][1] in Common.other_map[1]
                  else f'Long castling for {i}' if colors[i][2] in Common.other_map[1]
                  else f'No possible castlings for {i}')

    def __do_castle(self, king: King, castling_type: str):
        rook = None
        for piece in Common.all_pieces:
            if (piece.piece_name == ('R' if king.color == 'w' else 'r')
                    and ((piece.root_name[1][0] - self.__prev_piece_value[1][0] < 0)
                         if castling_type == 'Long'
                         else (piece.root_name[1][0] - self.__prev_piece_value[1][0] > 0))):
                rook = piece
        castling_root = self.__get_root_by_pos((king.root_name[1][0] +
                                                (-1 if castling_type == 'Short' else 1),
                                                king.root_name[1][1]))
        rook.move_to_root(castling_root)
        self.__write_to_board_data()

    def __check_check(self, piece):
        piece.check_movables(False)
        for prob_king in Common.all_pieces:
            if prob_king.piece_name in ['k', 'K']:
                if prob_king.root_name[1] in piece.takeable_roots:
                    self.__check_logic(prob_king)

    def __check_logic(self, king: King):
        print('Check for white' if king.color == 'w' else 'Check for black')
        king.is_checked = True
        self.is_checked = True

    def __are_moves(self, color):
        no_moves = True
        for piece in Common.all_pieces:
            if piece.color != color:
                piece.check_movables(True)
                if piece.movable_roots or piece.takeable_roots:
                    no_moves = False
        return no_moves

    def __check_mate(self, color):
        if self.__are_moves(color):
            for prob_king in Common.all_pieces:
                if prob_king.piece_name == ('K' if color == 'b' else 'k'):
                    if not prob_king.is_checked:
                        print('Stalemate')
                        stalemate = DialogueWindow(self.__screen, 'stalemate')
                        Common.all_dialogues.add(stalemate)
                        Common.game_ended = True
                    else:
                        print('Mate for ' + ('white' if prob_king.piece_name == 'K' else 'black'))
                        win = DialogueWindow(self.__screen, 'w by mate' if prob_king.piece_name == 'k'
                                             else 'b by mate')
                        Common.all_dialogues.add(win)
                        Common.game_ended = True
            return True
        return False

    def __check_draw(self):
        for position in self.__all_fen_positions:
            if self.__all_fen_positions[position] == 3:
                draw = DialogueWindow(self.__screen, 'rep')
                Common.all_dialogues.add(draw)
                Common.game_ended = True
                break

        if Common.other_map[3] >= 50:
            draw = DialogueWindow(self.__screen, '50')
            Common.all_dialogues.add(draw)
            Common.game_ended = True

    def __change_turn(self):
        self.__turn = 'w' if self.__turn == 'b' else 'b'
        Common.other_map[0] = self.__turn

    def __unmark_all_marks(self):
        """Removes all marks from roots"""
        Common.all_marks.empty()
        for root in Common.all_roots:
            root.mark = False

    def __unselect_all_roots(self):
        """Removes all selects from roots"""
        self.__all_selects.empty()
        self.__all_checks.empty()

    def grand_update(self):
        """Refreshes the whole scene on the screen"""
        self.__screen.blit(self.__background, (0, 0))
        self.__screen.blit(self.__play_board_view, self.__play_board_view_pos)
        Common.all_roots.draw(self.__screen)
        Common.all_input_boxes.draw(self.__screen)
        self.__all_selects.draw(self.__screen)
        self.__all_checks.draw(self.__screen)
        Common.all_marks.draw(self.__screen)
        Common.all_pieces.draw(self.__screen)
        Common.all_choosing_cells.draw(self.__screen)
        Common.all_choosing_pieces.draw(self.__screen)
        self.__draw_timer()
        Common.all_dialogues.draw(self.__screen)
        Common.all_buttons.draw(self.__screen)
        pg.display.update()


class InputBox(pg.sprite.Sprite):
    """All the input boxes main class"""

    def __init__(self, board_rect: pg.Rect, optx: int, opty: int, width: str, height: str,
                 btn_cnt: int, text: str = '',
                 font_size: str = FONT_INPUT_BOX_SIZE, input_box_type: str = 'fen'):
        super().__init__()
        if input_box_type == 'fen':
            x, y = board_rect.x, board_rect.y
            board_width, board_height = board_rect.width, board_rect.height
            buttons_count = 2
            board_width -= INPUT_BOX_HEIGHT * buttons_count
            with open('saved_info.json', 'r') as info:
                self.text = json.load(info)['fen string']
            self.image = pg.Surface((board_width, INPUT_BOX_HEIGHT)).convert_alpha()
            self.rect = pg.Rect(x, 2 * y + board_height, board_width, INPUT_BOX_HEIGHT)
        elif input_box_type == 'custom':
            x, y = optx, opty
            buttons_count = btn_cnt
            width -= height * buttons_count
            self.text = text
            self.image = pg.Surface((width, height)).convert_alpha()
            self.rect = pg.Rect(x, y, width, height)

        self.input_box_font_size = font_size
        self.input_box_font = pg.font.Font(FONT_TEXT_PATH, self.input_box_font_size)
        self.__fen_text = None
        self.active = False
        self.image.fill(Common.MAIN_COLOR)
        self.__update_text()

    def activate(self):
        """Activates the input box"""
        self.active = True
        pg.draw.rect(self.image, Common.MAIN_STROKE_COLOR, (0, 0, self.rect.width, self.rect.height), 2)

    def deactivate(self):
        """Deactivates the input box"""
        self.active = False
        pg.draw.rect(self.image, Common.MAIN_COLOR, (0, 0, self.rect.width, self.rect.height), 2)

    def put_char(self, char: str):
        """Adds the symbol to the input box"""
        self.text += char
        self.__update_text()

    def del_char(self):
        """Removes the symbol from the input box"""
        self.text = self.text[:-1]
        self.__update_text()

    def __update_text(self):
        """Updates the input box if any changes have been made"""
        self.image.fill(Common.MAIN_COLOR)
        pg.draw.rect(self.image,
                     Common.MAIN_STROKE_COLOR if self.active else Common.MAIN_COLOR,
                     (0, 0, self.rect.width, self.rect.height), 2)
        self.__fen_text = self.input_box_font.render(self.text, True, Common.MAIN_STROKE_COLOR)
        self.__adapt_text()
        self.image.blit(self.__fen_text, (9, 9))

    def __adapt_text(self):
        done = False
        while not done:
            if (self.__fen_text.get_rect().width + 14 > self.rect.width or
                    self.__fen_text.get_rect().height + 14 > self.rect.height):
                self.input_box_font_size -= 1
                self.input_box_font = pg.font.Font(FONT_TEXT_PATH, self.input_box_font_size)
                self.__fen_text = self.input_box_font.render(self.text, True, Common.MAIN_STROKE_COLOR)
            else:
                done = True


class Root(pg.sprite.Sprite):
    """Root main class"""

    def __init__(self, color_order: int, size: int, coordinates: tuple, name: str):
        super().__init__()
        x, y = coordinates
        self.color = Common.ROOT_COLORS[color_order]
        self.root_name = name
        # image = Image.open(IMG_PATH + self.color).resize((size, size))
        # self.image = pg.image.fromstring(image.tobytes(), image.size, image.mode)
        self.image = pg.Surface((size, size))
        self.image.fill(self.color)
        self.rect = pg.Rect(x * size, y * size, size, size)
        self.mark = False
        self.is_selected = False


class Mark(pg.sprite.Sprite):
    """Root mark class"""

    def __init__(self, root: Root, mark_type):
        super().__init__()
        picture = MOVABLE_IMG_DICT[mark_type]
        self.image = (pg.image.fromstring(picture.tobytes(), picture.size, picture.mode).convert_alpha())
        if mark_type in ['available', 'takeable']:
            self.image = TAKEABLE_SURF if mark_type == 'takeable' else AVAILABLE_SURF
            self.image.set_alpha(80)
        elif mark_type == 'mark':
            self.image = MARK_SURF
        self.rect = pg.Rect((root.rect.x, root.rect.y), (ROOT_SIZE, ROOT_SIZE))
        self.root_name = root.root_name


class Select(pg.sprite.Sprite):
    """Root selection class"""

    def __init__(self, root: Root):
        super().__init__()
        self.image = pg.Surface((ROOT_SIZE, ROOT_SIZE)).convert_alpha()
        self.image.fill(ACTIVE_ROOT_COLOR)
        self.rect = pg.Rect((root.rect.x, root.rect.y), (ROOT_SIZE, ROOT_SIZE))
        self.root_name = root.root_name


class Choice(pg.sprite.Sprite):
    """This thing when you wanna be a queen on 8th root"""

    def __init__(self, pawn: Pawn):
        super().__init__()
        self.counter = 1
        while self.counter < 5:
            cell = ChoosingCell(pawn, self.counter)
            Common.all_choosing_cells.add(cell)
            self.counter += 1


class ChoosingPiece(pg.sprite.Sprite):
    """Piece to choose at the end of board"""

    def __init__(self, counter: int, pawn: Pawn):
        super().__init__()
        self.counter = counter
        self.names_dict = {1: 'queen', 2: 'rook', 3: 'knight', 4: 'bishop'}
        self.piece_names_dict = {1: ('q', 'Q'), 2: ('r', 'R'), 3: ('n', 'N'), 4: ('b', 'B')}
        self.piece_name = self.piece_names_dict[counter][0 if pawn.color == 'b' else 1]
        self.image = PIECES_IMG_DICT[pawn.color + '_' + self.names_dict[self.counter]]


class ChoosingCell(pg.sprite.Sprite):
    """One of the cells the choosing piece can be placed on"""

    def __init__(self, pawn: Pawn, counter):
        super().__init__()
        self.counter = counter
        self.image = pg.Surface((ROOT_SIZE, ROOT_SIZE))
        self.image.fill(WHITE)
        offset_dist = ((ROOT_SIZE if pawn.color == 'w' else -ROOT_SIZE)
                       if not Common.is_flipped else
                       (-ROOT_SIZE if pawn.color == 'w' else ROOT_SIZE))
        self.rect = pg.Rect((pawn.rect.x,
                             pawn.rect.y + offset_dist * counter),
                            (ROOT_SIZE, ROOT_SIZE))
        choosing = ChoosingPiece(counter, pawn)
        choosing.rect = self.rect
        Common.all_choosing_pieces.add(choosing)


class DialogueWindow(pg.sprite.Sprite):

    def __init__(self, parent_screen: pg.Surface, dialogue_type: str):
        super().__init__()
        self.__screen = parent_screen
        self.image = pg.Surface((self.__screen.get_width() // 100 * 60, self.__screen.get_height() // 100 * 60))
        self.image.fill(Common.MAIN_COLOR)
        pg.draw.rect(self.image, Common.MAIN_STROKE_COLOR, self.image.get_rect(), 3)
        self.rect = pg.Rect((self.__screen.get_rect().width // 2 - self.image.get_rect().width // 2,
                             self.__screen.get_rect().height // 2 - self.image.get_rect().height // 2),
                            (self.image.get_rect().width, self.image.get_rect().height))
        self.font = pg.font.Font(FONT_CHESSBOARD_PATH, FONT_HEADER_SIZE)
        if dialogue_type == 'waiting':
            text = self.font.render('Waiting for an opponent', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'w by time':
            text = self.font.render('White won by time', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'b by time':
            text = self.font.render('Black won by time', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'w by mate':
            text = self.font.render('White won by checkmate', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'b by mate':
            text = self.font.render('Black won by checkmate', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'stalemate':
            text = self.font.render('Stalemate', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == 'rep':
            text = self.font.render('Draw by repeating moves', True, Common.MAIN_STROKE_COLOR)
        elif dialogue_type == '50':
            text = self.font.render('Draw by the 50 turns rule', True, Common.MAIN_STROKE_COLOR)
        else:
            text = self.font.render('LOL', True, Common.MAIN_STROKE_COLOR)

        if dialogue_type not in ['waiting']:
            close_btn = Button('X', (self.rect.x + self.image.get_width() - CLOSE_BTN_SIZE[0] - 3,
                                     self.rect.y + 3),
                                CLOSE_BTN_SIZE, 42, 1)
            Common.all_buttons.add(close_btn)

        self.image.blit(text, (self.image.get_width() // 2 - text.get_width() // 2,
                               self.image.get_height() // 2 - text.get_height() // 2))
