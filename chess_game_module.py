from pieces import *
import pyperclip as clip
import pygame as pg
import board_data
from konfig import *

pg.init()
chessboard_font = pg.font.Font(FONT_CHESSBOARD_PATH, FONT_CHESSBOARD_SIZE)
text_font = pg.font.Font(FONT_TEXT_PATH, FONT_TEXT_SIZE)


class Chessboard:

    def __init__(self, parent_surface: pg.Surface, root_count: int = ROOT_COUNT, root_size: int = ROOT_SIZE):
        self.__screen = parent_surface
        self.__count = root_count
        self.__board_data = board_data.board
        self.__size = root_size
        self.__pieces = PIECES_DICT
        self.__all_roots = pg.sprite.Group()
        self.__all_pieces = pg.sprite.Group()
        self.__all_areas = pg.sprite.Group()
        self.__all_inputboxes = pg.sprite.Group()
        self.__input_box = None
        self.__pressed_root = None
        self.__picked_piece = None
        self.__taken_piece = None
        self.__clicked = False
        self.__func_keys = [pg.K_LCTRL, pg.K_RCTRL, pg.K_v, pg.K_RETURN, pg.K_BACKSPACE]
        self.__hotkey = {pg.K_LCTRL: False, pg.K_RCTRL: False, pg.K_v: False}
        self.__prepare_screen()
        self.__drawplayboard()
        self.__setup_board()
        self.__grand_update()

    def __prepare_screen(self):
        background_img = pg.image.load(IMG_PATH + STATIC_IMG_PATH + BACKGROUND_IMG)
        background_img = pg.transform.scale(background_img, WINDOW_SIZE)
        self.__screen.blit(background_img, (0, 0))

    def __drawplayboard(self):
        total_width = self.__count * self.__size
        num_fields = self.__create_num_fields()
        self.__all_roots = self.__create_all_roots()
        num_fields_depth = num_fields[0].get_width()
        playboard_view = pg.Surface((2 * num_fields_depth + total_width,
                                     2 * num_fields_depth + total_width), pg.SRCALPHA).convert_alpha()

        board_background_img = pg.image.load(IMG_PATH + STATIC_IMG_PATH + BOARD_BACKGROUND_IMG)
        board_background_img = pg.transform.scale(board_background_img,
                                                  (playboard_view.get_width(),
                                                   playboard_view.get_height()))

        playboard_view.blit(board_background_img, (0, 0))
        playboard_view.blit(num_fields[0], (0, num_fields_depth))
        playboard_view.blit(num_fields[0], (num_fields_depth + total_width, num_fields_depth))
        playboard_view.blit(num_fields[1], (num_fields_depth, 0))
        playboard_view.blit(num_fields[1], (num_fields_depth, num_fields_depth + total_width))

        playboard_rect = playboard_view.get_rect()
        playboard_rect.x += (self.__screen.get_width() - playboard_rect.width) // 2
        playboard_rect.y += (self.__screen.get_height() - playboard_rect.height) // 4
        self.__screen.blit(playboard_view, playboard_rect)
        roots_coord_offset = (
            playboard_rect.x + num_fields_depth,
            playboard_rect.y + num_fields_depth,)
        self.__apply_offset_for_roots(roots_coord_offset)
        self.__clipped_area = pg.rect.Rect(roots_coord_offset, (total_width, total_width))
        self.__draw_input_box(playboard_rect)

    def __draw_input_box(self, board_rect: pg.Rect):
        self.__input_box = InputBox(board_rect)
        self.__all_roots.add(self.__input_box)

    def __create_num_fields(self):
        lines = pg.Surface((self.__count * self.__size, self.__size // 2), pg.SRCALPHA).convert_alpha()
        rows = pg.Surface((self.__size // 2, self.__count * self.__size), pg.SRCALPHA).convert_alpha()
        for i in range(0, self.__count):
            letter = chessboard_font.render(letters[i].upper(), True, LETTERS_COLOR)
            number = chessboard_font.render(str(self.__count - i), True, NUMBERS_COLOR)
            lines.blit(letter, (
                i * self.__size + (self.__size - letter.get_rect().width) // 2,
                (lines.get_height() - letter.get_rect().height) // 2
            ))
            rows.blit(number, (
                (rows.get_width() - number.get_rect().width) // 2,
                i * self.__size + (self.__size - number.get_rect().height) // 2
            ))

        return rows, lines

    def __create_all_roots(self):
        root_group = pg.sprite.Group()
        is_even_count = (self.__count % 2 == 0)
        root_color_order = False if is_even_count else True
        for y in range(self.__count):
            for x in range(self.__count):
                root = Root(root_color_order,
                            self.__size,
                            (x, y),
                            letters[x] + str(self.__count - y))
                root_group.add(root)
                root_color_order ^= True
            root_color_order = root_color_order ^ True if is_even_count else root_color_order
        return root_group

    def __apply_offset_for_roots(self, offset):
        for root in self.__all_roots:
            root.rect.x += offset[0]
            root.rect.y += offset[1]

    def __setup_board(self):
        for j, row in enumerate(self.__board_data):
            for i, root_value in enumerate(row):
                if root_value != 0:
                    piece = self.__create_piece(root_value, (j, i))
                    self.__all_pieces.add(piece)
        for piece in self.__all_pieces:
            for root in self.__all_roots:
                if piece.root_name == root.root_name:
                    piece.rect = root.rect.copy()
                    root.kept = True

    def __create_piece(self, piece_sym: str, board_data_coord: tuple):
        root_name = self.__to_root_name(board_data_coord)
        piece_tuple = self.__pieces[piece_sym]
        class_name = globals()[piece_tuple[0]]
        return class_name(self.__size, piece_tuple[1], root_name)

    def __to_root_name(self, board_data_coord: tuple):
        return letters[board_data_coord[1]] + str(self.__count - board_data_coord[0])

    def __get_root(self, pos: tuple):
        for root in self.__all_roots:
            if root.rect.collidepoint(pos):
                return root
        return None

    def __get_piece_on_click(self, root):
        for piece in self.__all_pieces:
            if piece.root_name == root.root_name:
                return piece
        return None

    def drag(self, pos: tuple):
        if self.__taken_piece is not None:
            if self.__clipped_area.collidepoint(pos[0] + self.__taken_piece.rect.width // 2,
                                                pos[1] + self.__taken_piece.rect.height // 2):
                self.__taken_piece.rect.center = pos
            else:
                self.__clicked = False
                self.__taken_piece.move_to_root(self.__pressed_root)
                self.__taken_piece = None
                self.__pick_root(self.__pressed_root)
            self.__grand_update()

    def mouse_btn_down(self, button_type: int, pos: tuple):
        self.__clicked = True
        self.__pressed_root = self.__get_root(pos)
        if self.__pressed_root is not None:
            if self.__pressed_root.root_name != 'input_box':
                self.__input_box.deactivate()
                if button_type == 1:
                    self.__taken_piece = self.__get_piece_on_click(self.__pressed_root)
                    self.__pressed_root.kept = False
                if self.__taken_piece is not None:
                    if self.__clipped_area.collidepoint(pos[0] + self.__taken_piece.rect.width // 2,
                                                        pos[1] + self.__taken_piece.rect.height // 2):
                        self.__taken_piece.rect.center = pos
                    else:
                        self.__picked_piece = None
                        self.__taken_piece = None
                    self.__grand_update()
            else:
                self.__pressed_root = None
                self.__input_box.activate()

    def mouse_btn_up(self, button_type: int, pos: tuple):
        released_root = self.__get_root(pos)
        if released_root is not None:
            if button_type == 3:
                self.__mark_root(released_root)
            if button_type == 1:
                if self.__clicked and not released_root.kept:
                    self.__pick_root(released_root)
            if self.__taken_piece is not None:
                self.__pressed_root.kept = False
                if not released_root.kept:
                    self.__taken_piece.move_to_root(released_root)
                else:
                    self.__taken_piece.move_to_root(self.__pressed_root)
                self.__taken_piece = None
        else:
            if self.__taken_piece is not None:
                self.__pressed_root.kept = False
                self.__taken_piece.move_to_root(self.__pressed_root)
                self.__taken_piece = None
        self.__clicked = False
        self.__grand_update()

    def __check_paste(self):
        if (self.__hotkey[pg.K_LCTRL] or self.__hotkey[pg.K_RCTRL]) and self.__hotkey[pg.K_v]:
            self.__input_box.put_char(clip.paste())
            return True
        else: return False

    def keyboard_btn_down(self, event):
        if self.__input_box.active and event.key in self.__func_keys:
            if event.key == pg.K_LCTRL:
                self.__hotkey[pg.K_LCTRL] = True
            if event.key == pg.K_RCTRL:
                self.__hotkey[pg.K_RCTRL] = True
            if event.key == pg.K_v:
                self.__hotkey[pg.K_v] = True
                if not self.__check_paste():
                    self.__input_box.put_char(event.unicode)
            if event.key == pg.K_RETURN:
                self.__setup_board_with_fen()
            if event.key == pg.K_BACKSPACE:
                self.__input_box.del_char()
        elif self.__input_box.active:
            self.__input_box.put_char(event.unicode)
        self.__grand_update()

    def keyboard_btn_up(self, event):
        if event.key == pg.K_LCTRL: self.__hotkey[pg.K_LCTRL] = False
        if event.key == pg.K_RCTRL: self.__hotkey[pg.K_RCTRL] = False
        if event.key == pg.K_v: self.__hotkey[pg.K_v] = False

    def __setup_board_with_fen(self):
        empty_roots = 0
        piece_map = self.__input_box.text.split('/')
        print(piece_map)
        for i in range(len(self.__board_data)):
            print('i =', i, '\b, board_data[i] =', self.__board_data[i])
            index = 0
            for j in range(len(self.__board_data[i])):
                print('j =', j, '\b, empty_roots =', empty_roots)
                if empty_roots == 0:
                    print('Empty roots is 0')
                    try:
                        print(':')
                        print('piece_map[i][index]:', piece_map[i][index])
                        empty_roots = int(piece_map[i][index])
                        print('board_data[i][j] =', self.__board_data[i][j])
                        self.__board_data[i][j] = 0
                        print('board_data[i][j] =', self.__board_data[i][j])
                        empty_roots -= 1
                        print('empty_roots =', empty_roots)
                        print('Non except ^^^^')
                    except ValueError:
                        print('Except')
                        print('board_data[i][j] =', self.__board_data[i][j])
                        self.__board_data[i][j] = piece_map[i][index]
                        print('board_data[i][j] =', self.__board_data[i][j])
                        index += 1
                        print('index:', index)
                else:
                    print('Else')
                    print('board_data[i][j] =', self.__board_data[i][j])
                    self.__board_data[i][j] = 0
                    empty_roots -= 1
                    print('empty_roots =', empty_roots)
        self.__all_pieces.empty()
        self.__setup_board()
        self.__grand_update()

    def __mark_root(self, root):
        if not root.mark:
            mark = Area(root)
            self.__all_areas.add(mark)
        else:
            for area in self.__all_areas:
                if area.root_name == root.root_name:
                    area.kill()
                    break
        root.mark ^= True

    def __pick_root(self, root):
        if self.__picked_piece is None:
            piece = self.__get_piece_on_click(root)
            if piece is not None:
                pick = Area(root, False)
                self.__all_areas.add(pick)
                self.__picked_piece = piece
        else:
            self.__picked_piece.move_to_root(root)
            if self.__picked_piece.is_moved:
                self.__unmark_all_roots()
                self.__picked_piece = None

    def __unmark_all_roots(self):
        self.__all_areas.empty()
        for root in self.__all_roots:
            root.mark = False

    def __grand_update(self):
        self.__all_roots.draw(self.__screen)
        self.__all_areas.draw(self.__screen)
        self.__all_pieces.draw(self.__screen)
        pg.display.update()


class InputBox(pg.sprite.Sprite):
    def __init__(self, board_rect: pg.Rect):
        super().__init__()
        x, y = board_rect.x, board_rect.y
        width, height = board_rect.width, board_rect.height
        self.root_name = 'input_box'
        self.text = ''
        self.active = False
        self.kept = False
        self.image = pg.Surface((width, INPUT_BOX_SIZE)).convert_alpha()
        self.image.fill(BLACK)
        pg.draw.rect(self.image, WHITE, (0, 0, width, INPUT_BOX_SIZE), 2)
        self.rect = pg.Rect(x, 2 * y + height, width, INPUT_BOX_SIZE)

    def activate(self):
        self.active = True
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)

    def deactivate(self):
        self.active = False
        pg.draw.rect(self.image, WHITE, (0, 0, self.rect.width, self.rect.height), 2)

    def put_char(self, char: str):
        self.text += char
        self.__update_text()

    def del_char(self):
        self.text = self.text[:-1]
        self.__update_text()

    def __update_text(self):
        self.image.fill(BLACK)
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)
        fen_text = text_font.render(self.text, True, INPUT_FONT_COLOR)
        self.image.blit(fen_text, (9, 9))


class Root(pg.sprite.Sprite):

    def __init__(self, color_order: int, size: int, coords: tuple, name: str):
        super().__init__()
        x, y = coords
        self.color = ROOT_COLORS[color_order]
        self.root_name = name
        self.image = pg.image.load(IMG_PATH + self.color)
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = pg.Rect(x * size, y * size, size, size)
        self.mark = False
        self.kept = False


class Area(pg.sprite.Sprite):

    def __init__(self, root: Root, type_of_area: bool = True):
        super().__init__()
        coords = (root.rect.x, root.rect.y)
        area_size = (root.rect.width, root.rect.height)
        if type_of_area:
            # mark root
            picture = pg.image.load(IMG_PATH + OTHER_IMG_PATH + 'mark.png').convert_alpha()
            self.image = pg.transform.scale(picture, area_size)
        else:
            # pick piece
            self.image = pg.Surface(area_size).convert_alpha()
            self.image.fill(ACTIVE_ROOT_COLOR)
        self.rect = pg.Rect(coords, area_size)
        self.root_name = root.root_name
