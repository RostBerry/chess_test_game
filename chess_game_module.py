from pieces import *
import pyperclip as clip
import pygame as pg
import board_data
from konfig import *

# useless stuff
pg.init()
chessboard_font = pg.font.Font(FONT_CHESSBOARD_PATH, FONT_CHESSBOARD_SIZE)
text_font = pg.font.Font(FONT_TEXT_PATH, FONT_TEXT_SIZE)


class Chessboard:
    """Main chessboard class"""

    def __init__(self, parent_surface: pg.Surface, root_count: int = ROOT_COUNT, root_size: int = ROOT_SIZE):
        # Defining constants from the konfig
        self.__screen = parent_surface
        self.__count = root_count
        self.__board_data = board_data.board
        self.__size = root_size
        self.__pieces = PIECES_DICT
        # Defining sprite groups
        self.__all_roots = pg.sprite.Group()
        self.__all_pieces = pg.sprite.Group()
        self.__all_selects = pg.sprite.Group()
        self.__all_input_boxes = pg.sprite.Group()
        self.__all_marks = pg.sprite.Group()
        # Defining interactive objects or variables
        self.__input_box = None
        self.__pressed_input_box = None
        self.__pressed_root = None
        self.__released_root = None
        self.__picked_piece = None
        self.__taken_piece = None
        self.__clicked = False
        self.__piece_selected = False
        # Dictionaries
        self.__func_keys = [pg.K_LCTRL, pg.K_RCTRL, pg.K_v, pg.K_RETURN, pg.K_BACKSPACE]
        self.__hotkey = {pg.K_LCTRL: False, pg.K_RCTRL: False, pg.K_v: False}
        # Initialization methods
        self.__prepare_screen()
        self.__draw_play_board()
        self.__setup_board()
        self.__grand_update()

    def __prepare_screen(self):
        """Draws background"""
        background_img = pg.image.load(IMG_PATH + STATIC_IMG_PATH + BACKGROUND_IMG)
        background_img = pg.transform.scale(background_img, WINDOW_SIZE)
        self.__screen.blit(background_img, (0, 0))

    def __draw_play_board(self):
        """Draws play board"""
        total_width = self.__count * self.__size
        # Creating main board objects
        num_fields = self.__create_num_fields()
        self.__all_roots = self.__create_all_roots()
        num_fields_depth = num_fields[0].get_width()
        play_board_view = pg.Surface((2 * num_fields_depth + total_width,
                                     2 * num_fields_depth + total_width), pg.SRCALPHA).convert_alpha()

        board_background_img = pg.image.load(IMG_PATH + STATIC_IMG_PATH + BOARD_BACKGROUND_IMG)
        board_background_img = pg.transform.scale(board_background_img,
                                                  (play_board_view.get_width(),
                                                   play_board_view.get_height()))

        # Bind created objects to the main object
        play_board_view.blit(board_background_img, (0, 0))
        play_board_view.blit(num_fields[0], (0, num_fields_depth))
        play_board_view.blit(num_fields[0], (num_fields_depth + total_width, num_fields_depth))
        play_board_view.blit(num_fields[1], (num_fields_depth, 0))
        play_board_view.blit(num_fields[1], (num_fields_depth, num_fields_depth + total_width))

        # Moves the board to the window center
        play_board_rect = play_board_view.get_rect()
        play_board_rect.x += (self.__screen.get_width() - play_board_rect.width) // 2
        play_board_rect.y += (self.__screen.get_height() - play_board_rect.height) // 4
        self.__screen.blit(play_board_view, play_board_rect)
        roots_coord_offset = (
            play_board_rect.x + num_fields_depth,
            play_board_rect.y + num_fields_depth,)
        self.__apply_offset_for_roots(roots_coord_offset)
        # Creates the border for the mouse (will be needed later)
        self.__clipped_area = pg.rect.Rect(roots_coord_offset, (total_width, total_width))

        # Draws the input box below the board
        self.__draw_input_box(play_board_rect)

    def __draw_input_box(self, board_rect: pg.Rect):
        """Draws input box in the bottom"""
        self.__input_box = InputBox(board_rect)
        self.__all_input_boxes.add(self.__input_box)

    def __create_num_fields(self):
        """Creates the rows and lines near the board (like 1-8, a-g)"""
        lines = pg.Surface((self.__count * self.__size, self.__size // 2), pg.SRCALPHA).convert_alpha()
        rows = pg.Surface((self.__size // 2, self.__count * self.__size), pg.SRCALPHA).convert_alpha()
        # Numerates the lines and rows
        for i in range(0, self.__count):
            letter = chessboard_font.render(letters[i].upper(), True, LETTERS_COLOR)
            number = chessboard_font.render(str(self.__count - i), True, NUMBERS_COLOR)
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

        return rows, lines

    def __create_all_roots(self):
        """Draws all roots on the board"""
        root_group = pg.sprite.Group()
        # Statement needed for correct color on the root
        is_even_count = (self.__count % 2 == 0)
        root_color_order = False if is_even_count else True
        # Creates the roots and adds them to the sprite group
        for y in range(self.__count):
            for x in range(self.__count):
                root = Root(root_color_order,
                            self.__size,
                            (x, y),
                            letters[x] + str(self.__count - y))
                root_group.add(root)
                root_color_order ^= True  # Changing the root color
            root_color_order = root_color_order ^ True if is_even_count else root_color_order
        return root_group

    def __apply_offset_for_roots(self, offset):
        """Moves the roots onto the board, not on the background"""
        for root in self.__all_roots:
            root.rect.x += offset[0]
            root.rect.y += offset[1]

    def __setup_board(self):
        """Draws the pieces on the roots from board_data or user's input"""
        for j, row in enumerate(self.__board_data):
            for i, root_value in enumerate(row):
                if root_value != 0:
                    # Creating a piece based on board_data and adding it to the group
                    piece = self.__create_piece(root_value, (j, i))
                    self.__all_pieces.add(piece)
        for piece in self.__all_pieces:
            for root in self.__all_roots:
                # Places the piece on the root
                if piece.root_name == root.root_name:
                    piece.rect = root.rect.copy()
                    root.kept = True

    def __create_piece(self, piece_sym: str, board_data_coord: tuple):
        """Creates a single piece"""
        root_name = self.__to_root_name(board_data_coord)
        piece_tuple = self.__pieces[piece_sym]
        class_name = globals()[piece_tuple[0]]
        return class_name(self.__size, piece_tuple[1], root_name)

    def __to_root_name(self, board_data_coord: tuple):
        """Returns the name of the root"""
        return letters[board_data_coord[1]] + str(self.__count - board_data_coord[0])

    def __get_root(self, pos: tuple):
        """Returns the root below the mouse position"""
        for root in self.__all_roots:
            if root.rect.collidepoint(pos):
                return root
        return None

    def __get_input_box(self, pos: tuple):
        """Returns the input box from mouse position"""
        if self.__input_box.rect.collidepoint(pos):
            return self.__input_box
        return None

    def __get_piece_on_click(self, root):
        """Returns the clicked piece"""
        for piece in self.__all_pieces:
            if piece.root_name == root.root_name:
                return piece
        return None

    def drag(self, pos: tuple):
        """Works when the mouse is moving"""
        if self.__taken_piece is not None:
            # Checks if the piece isn't moving outside the clipped area and moves it
            if self.__clipped_area.collidepoint(pos[0] + self.__taken_piece.rect.width // 2,
                                                pos[1] + self.__taken_piece.rect.height // 2):
                self.__taken_piece.rect.center = pos
            else:
                self.__clicked = False  # Statement needed to correct root selection
                self.__taken_piece.move_to_root(self.__pressed_root)
                self.__taken_piece = None
                self.__pick_root(self.__pressed_root)
            self.__grand_update()

    def mouse_btn_down(self, button_type: int, pos: tuple):
        """Works when the mouse btn is clicked"""
        self.__clicked = True  # Statement needed to correct root selection
        # Checking if the user clicked on root or input box
        self.__pressed_root = self.__get_root(pos)
        self.__pressed_input_box = self.__get_input_box(pos)
        # User clicked on the root
        if self.__pressed_root is not None:
            self.__input_box.deactivate()
            if button_type == 1:  # LMB
                if not self.__piece_selected:
                    self.__taken_piece = self.__get_piece_on_click(self.__pressed_root)
            if self.__taken_piece is not None:
                # Checking if the piece wouldn't move outside the clipped area
                if self.__clipped_area.collidepoint(pos[0] + self.__taken_piece.rect.width // 2,
                                                    pos[1] + self.__taken_piece.rect.height // 2):
                    self.__taken_piece.rect.center = pos
                else:
                    self.__picked_piece = None
                    self.__taken_piece = None
                self.__grand_update()
        # User clicked on the input box
        elif self.__pressed_input_box is not None:
            self.__input_box.activate()

    def mouse_btn_up(self, button_type: int, pos: tuple):
        """Works when the mouse btn is released"""
        self.__released_root = self.__get_root(pos)
        if self.__released_root is not None:
            if button_type == 3:  # RMB
                self.__mark_root(self.__released_root)
            if button_type == 1:  # LMB
                if self.__clicked:
                    self.__pick_root(self.__released_root)

            if self.__taken_piece is not None:
                self.__pressed_root.kept = False
                if not self.__released_root.kept:
                    self.__taken_piece.move_to_root(self.__released_root)
                else:
                    self.__taken_piece.move_to_root(self.__pressed_root)
                self.__taken_piece = None
        self.__clicked = False
        self.__grand_update()

    def __check_paste(self):
        """Checks if the user's keyboard input is Ctrl+V"""
        if (self.__hotkey[pg.K_LCTRL] or self.__hotkey[pg.K_RCTRL]) and self.__hotkey[pg.K_v]:
            self.__input_box.put_char(clip.paste())
            return True
        else:
            return False

    def keyboard_btn_down(self, event):
        """Works when the keyboard btn is clicked"""
        if self.__input_box.active and event.key in self.__func_keys:
            if event.key == pg.K_LCTRL:  # Left Ctrl
                self.__hotkey[pg.K_LCTRL] = True
            if event.key == pg.K_RCTRL:  # Right Ctrl
                self.__hotkey[pg.K_RCTRL] = True
            if event.key == pg.K_v:  # v
                self.__hotkey[pg.K_v] = True
                if not self.__check_paste():
                    self.__input_box.put_char(event.unicode)
            if event.key == pg.K_RETURN:  # Enter
                self.__setup_board_with_fen()
            if event.key == pg.K_BACKSPACE:  # Backspace
                self.__input_box.del_char()
        elif self.__input_box.active:  # Works if user didn't press any functional key
            self.__input_box.put_char(event.unicode)
        self.__grand_update()

    def keyboard_btn_up(self, event):
        """Works when the keyboard btn is released"""
        # Releasing all keys
        if event.key == pg.K_LCTRL:
            self.__hotkey[pg.K_LCTRL] = False
        if event.key == pg.K_RCTRL:
            self.__hotkey[pg.K_RCTRL] = False
        if event.key == pg.K_v:
            self.__hotkey[pg.K_v] = False

    def __setup_board_with_fen(self):
        """Decodes the user's input and setups new board konfig"""
        empty_roots = 0
        piece_map = self.__input_box.text.split('/')
        for i in range(len(self.__board_data)):
            index = 0
            for j in range(len(self.__board_data[i])):
                if empty_roots == 0:
                    try:
                        empty_roots = int(piece_map[i][index])
                        self.__board_data[i][j] = 0
                        empty_roots -= 1
                    except ValueError:
                        self.__board_data[i][j] = piece_map[i][index]
                        index += 1
                else:
                    self.__board_data[i][j] = 0
                    empty_roots -= 1
        self.__all_pieces.empty()
        self.__setup_board()
        self.__grand_update()

    def __mark_root(self, root):
        """Draws a green circle on the clicked root"""
        if not root.mark:
            mark = Mark(root)
            self.__all_marks.add(mark)
        else:
            for mark in self.__all_marks:
                if mark.root_name == root.root_name:
                    mark.kill()
                    break
        root.mark ^= True

    def __select_root(self, root):
        """Selects the root and colors it to the transparent green"""
        select = Select(root)
        self.__piece_selected = True
        self.__all_selects.add(select)

    def __pick_root(self, root):
        """Works when the left mouse btn is clicked, unmarks all the marks and selects or moves the piece"""
        self.__un_mark_all_marks()
        if self.__picked_piece is None:
            if not root.kept:
                piece = self.__get_piece_on_click(root)
                if piece is not None:
                    self.__select_root(root)
                    self.__picked_piece = piece
        else:
            if not root.kept:
                self.__picked_piece.move_to_root(root)
                if self.__picked_piece.is_moved:
                    self.__un_select_all_roots()
                    self.__picked_piece = None

    def __un_mark_all_marks(self):
        """Removes all marks from roots"""
        self.__all_marks.empty()
        for root in self.__all_roots:
            root.mark = False

    def __un_select_all_roots(self):
        """Removes all selects from roots"""
        self.__piece_selected = False
        self.__all_selects.empty()

    def __grand_update(self):
        """Refreshes the whole scene on the screen"""
        self.__all_roots.draw(self.__screen)
        self.__all_input_boxes.draw(self.__screen)
        self.__all_selects.draw(self.__screen)
        self.__all_marks.draw(self.__screen)
        self.__all_pieces.draw(self.__screen)
        pg.display.update()


class InputBox(pg.sprite.Sprite):
    """All the input boxes main class"""
    def __init__(self, board_rect: pg.Rect):
        super().__init__()
        x, y = board_rect.x, board_rect.y
        width, height = board_rect.width, board_rect.height
        self.root_name = 'input_box'
        self.text = ''
        self.active = False
        self.image = pg.Surface((width, INPUT_BOX_SIZE)).convert_alpha()
        self.image.fill(BLACK)
        pg.draw.rect(self.image, WHITE, (0, 0, width, INPUT_BOX_SIZE), 2)
        self.rect = pg.Rect(x, 2 * y + height, width, INPUT_BOX_SIZE)

    def activate(self):
        """Activates the input box"""
        self.active = True
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)

    def deactivate(self):
        """Deactivates the input box"""
        self.active = False
        pg.draw.rect(self.image, WHITE, (0, 0, self.rect.width, self.rect.height), 2)

    def put_char(self, char: str):
        """Adds the symbol to the input box"""
        self.text += char
        self.__update_text()

    def del_char(self):
        """Removes the symbol from the input box"""
        self.text = self.text[:-1]
        self.__update_text()

    def __update_text(self):
        """Updates the input box every time any changes have been made"""
        self.image.fill(BLACK)
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)
        fen_text = text_font.render(self.text, True, INPUT_FONT_COLOR)
        self.image.blit(fen_text, (9, 9))


class Root(pg.sprite.Sprite):
    """Root main class"""

    def __init__(self, color_order: int, size: int, coordinates: tuple, name: str):
        super().__init__()
        x, y = coordinates
        self.color = ROOT_COLORS[color_order]
        self.root_name = name
        self.image = pg.image.load(IMG_PATH + self.color)
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = pg.Rect(x * size, y * size, size, size)
        self.mark = False
        self.kept = False


class Mark(pg.sprite.Sprite):
    """Root mark class"""

    def __init__(self, root: Root):
        super().__init__()
        picture = pg.image.load(IMG_PATH + OTHER_IMG_PATH + 'mark.png').convert_alpha()
        self.image = pg.transform.scale(picture, (ROOT_SIZE, ROOT_SIZE))
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
