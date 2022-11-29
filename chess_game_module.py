from pieces import *
import pyperclip as clip
import pygame as pg
import board_data
from konfig import *


class Chessboard:
    """Main chessboard class"""

    def __init__(self, parent_surface: pg.Surface, root_count: int = ROOT_COUNT, root_size: int = ROOT_SIZE):
        # Defining constants from the konfig or __init__ params
        self.__screen = parent_surface
        self.__count = root_count
        self.__board_data = board_data.board
        self.__size = root_size
        self.__pieces = PIECES_DICT
        self.__input_box_font_size = FONT_TEXT_SIZE
        self.__chessboard_font_size = FONT_CHESSBOARD_SIZE
        self.__chessboard_font = pg.font.Font(FONT_CHESSBOARD_PATH, self.__chessboard_font_size)
        self.__text_font = pg.font.Font(FONT_TEXT_PATH, FONT_TEXT_SIZE)
        # Defining sprite groups
        self.__all_roots = pg.sprite.Group()
        self.__all_pieces = pg.sprite.Group()
        self.__all_pieces_list = []
        self.__all_selects = pg.sprite.Group()
        self.__all_checks = pg.sprite.Group()
        self.__all_input_boxes = pg.sprite.Group()
        self.__all_marks = pg.sprite.Group()
        # Defining interactive objects or variables
        self.roots_dict = {}
        self.__input_box = None
        self.__pressed_input_box = None
        self.__pressed_root = None
        self.__released_root = None
        self.__selected_piece = None
        self.__taken_piece = None
        self.__clicked = False
        self.__can_drag = False
        self.__turn = None
        # Dictionaries
        self.__func_keys = [pg.K_LCTRL, pg.K_RCTRL, pg.K_v, pg.K_RETURN, pg.K_BACKSPACE]
        self.__hotkey = {pg.K_LCTRL: False, pg.K_RCTRL: False, pg.K_v: False}
        # Initialization methods
        self.__prepare_screen()
        self.__draw_play_board()
        self.__setup_board_with_fen()
        self.__prepare_music()
        self.__grand_update()

    def __prepare_music(self):
        """Creates a nice soundtrack"""
        pg.mixer.music.load(MUSIC_PATH + BACKGROUND_MUSIC)
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

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
        self.__clipped_area = pg.rect.Rect(roots_coord_offset,
                                           (total_width,
                                            total_width))

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
            letter = self.__chessboard_font.render(letters[i].upper(), True, LETTERS_COLOR)
            number = self.__chessboard_font.render(str(self.__count - i), True, NUMBERS_COLOR)
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
                root_name = self.__to_root_name((y, x))
                self.roots_dict[root_name[0]] = root_name[1]
                root = Root(root_color_order,
                            self.__size,
                            (x, y),
                            root_name)
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
        """Draws the pieces on the roots from board_data"""
        self.__all_pieces_list = []
        for j in range(len(self.__board_data)):
            for i, root_value in enumerate(self.__board_data[j]):
                if root_value != 0:
                    # Creating a piece based on board_data and adding it to the group
                    piece = self.__create_piece(root_value, (j, i))
                    self.__all_pieces.add(piece)
        for piece in self.__all_pieces:
            for root in self.__all_roots:
                # Places the piece on the root
                if piece.root_name[0] == root.root_name[0]:
                    piece.rect = root.rect.copy()
                    root.kept = True
        self.write_piece_positions()

    def __setup_board_with_fen(self):
        """Decodes the Forsyth Edwards Notation and setups new board konfig"""
        # Separating the fen string to pieces placement and additional info
        pieces_and_other_map = self.__input_box.text.split(' ')
        self.__pieces_map = pieces_and_other_map[0].split('/')
        self.__other_map = pieces_and_other_map[1:]
        # Replacing the board data with new pieces placement
        for row in range(len(self.__board_data)):  # Running through board data rows
            value = 0
            piece_map_offset = 0
            while value < len(self.__board_data[row]):  # Running through board data values in rows
                offset = 0
                try:
                    for i in range(int(self.__pieces_map[row][value - piece_map_offset])):  # Placing the empty
                        self.__board_data[row][value + i] = 0                              # roots if those have
                        offset = i                                                        # been found
                    value += offset
                    piece_map_offset += offset
                except ValueError:  # Placing regular piece if the value in pieces map isn't an integer
                    self.__board_data[row][value] = self.__pieces_map[row][value - piece_map_offset]
                value += 1

        # Saving additional info
        self.__turn = self.__other_map[0]
        print("White's turn" if self.__other_map[0] == 'w' else "Black's turn")
        self.__castling_logic()
        print('The last pawn move is: {}'.format('None' if '-' in self.__other_map[2] else self.__other_map[2]))

        print(f'Halfmoves done: {self.__other_map[3]}')

        endings = {'1': 'st', '2': 'nd', '3': 'rd'}
        print(  # What move is it
            f'{self.__other_map[4]}{endings[self.__other_map[4]] if self.__other_map[4] in endings else "th"} move '
        )

        self.__all_pieces.empty()
        self.__setup_board()
        self.__grand_update()

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

        for info in self.__other_map:
            fen_string += ' ' + info

        self.__input_box.text = fen_string  # Putting the fen string to the input bar
        self.__input_box.put_char('')  # Updating the text

    def __create_piece(self, piece_sym: str, board_data_coord: tuple):
        """Creates a single piece"""
        root_name = self.__to_root_name(board_data_coord)
        piece_tuple = self.__pieces[piece_sym]
        class_name = globals()[piece_tuple[0]]
        return class_name(self.__size, piece_tuple[1], root_name, self.roots_dict)

    def write_piece_positions(self):
        pieces_root_names = []
        for piece in self.__all_pieces:
            pieces_root_names.append((piece.root_name, piece.color))
        for piece in self.__all_pieces:
            piece.pieces_positions = tuple(pieces_root_names)
            piece.all_roots = self.__all_roots

    def __to_root_name(self, board_data_coord: tuple):
        """Returns the name of the root"""
        return (letters[board_data_coord[1]] + str(self.__count - board_data_coord[0]),
                (board_data_coord[1] + 1, board_data_coord[0] + 1))

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
            if piece.root_name[0] == root.root_name[0]:
                print('Piece color:', piece.color, 'Turn:', self.__turn)
                if piece.color == self.__turn and self.__selected_piece is None:
                    if self.__taken_piece is None:
                        return piece
                    else:
                        self.__taken_piece.move_to_root(self.__pressed_root)
                        return piece
        return None

    def __get_piece_pos_by_name(self, name):
        for finding_piece in self.__all_pieces:
            if finding_piece.piece_name == name:
                return finding_piece.root_name[1]

    def __get_piece_by_piece_pos(self, piece_pos):
        for piece in self.__all_pieces:
            if piece.root_name[1] == piece_pos:
                return piece

    def __fits_in_border(self, piece, pos):
        """Checks if the mouse isn't outside the borders"""
        if (self.__clipped_area.collidepoint(pos[0] - piece.rect.width // 4,
                                             pos[1] - piece.rect.height // 2)
            and self.__clipped_area.collidepoint(pos[0] + piece.rect.width // 4,
                                                 pos[1] + piece.rect.height // 2)):
            return True
        return False

    def drag(self, pos: tuple):
        """Works when the mouse is moving"""
        if self.__taken_piece is not None:
            # Checks if the piece isn't moving outside the clipped area and moves it
            if self.__fits_in_border(self.__taken_piece, pos):
                self.__taken_piece.rect.center = pos
            else:
                self.__clicked = False  # Statement needed to correct root selection
                self.__move_or_select_piece(self.__pressed_root)
        elif self.__selected_piece is not None:
            if self.__can_drag:
                if self.__fits_in_border(self.__selected_piece, pos):
                    self.__selected_piece.rect.center = pos
                else:
                    self.__clicked = False  # Statement needed to correct root selection
                    self.__move_or_select_piece(self.__pressed_root)
        self.__grand_update()

    def mouse_btn_down(self, button_type: int, pos: tuple):
        """Works when the mouse btn is clicked"""
        self.__clicked = True  # Statement needed to correct root selection
        # Checking if the user clicked on root or input box
        if button_type == 1:
            self.__pressed_root = (self.__get_root(pos)
                                   if self.__selected_piece is None
                                   else self.__pressed_root)
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
                    self.__select_root(self.__pressed_root)
                    self.__pressed_root.is_selected ^= True
                    self.__draw_available_roots(self.__taken_piece)
                    # Checking if the piece wouldn't move outside the clipped area
                    if self.__fits_in_border(self.__taken_piece, pos):
                        self.__taken_piece.rect.center = pos
                    else:
                        pass

                elif self.__selected_piece is not None:
                    if self.__fits_in_border(self.__selected_piece, pos):
                        self.__selected_piece.rect.center = pos
                        self.__can_drag = True

                else:
                    self.__unmark_all_marks()

            elif button_type == 3:
                if self.__selected_piece is not None or self.__taken_piece is not None:
                    self.__move_or_select_piece(self.__pressed_root)
            self.__grand_update()

    def mouse_btn_up(self, button_type: int, pos: tuple):
        """Works when the mouse btn is released"""
        self.__released_root = self.__get_root(pos)
        if self.__released_root is not None:
            if button_type == 3:  # RMB
                self.__mark_root(self.__released_root)
            if button_type == 1:  # LMB
                self.__can_drag = False
                if self.__clicked:
                    self.__move_or_select_piece(self.__released_root)
            if self.__taken_piece is not None:
                pass
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

    def __mark_root(self, root):
        """Draws a green circle on the clicked root"""
        if not root.mark:
            mark = Mark(root, 'mark')
            self.__all_marks.add(mark)
        else:
            for mark in self.__all_marks:
                if mark.root_name[0] == root.root_name[0]:
                    mark.kill()
                    break
        root.mark ^= True

    def __select_root(self, root):
        """Selects the root and colors it to the transparent green"""
        select = Select(root)
        self.__all_selects.add(select)

    def __draw_available_roots(self, piece: Piece):
        piece.movable_roots = []
        piece.check_movables()
        for available in piece.movable_roots:
            print('piece root name:', piece.root_name[1], 'available:', available)
            moving_dist = (available[0], available[1])
            for root in self.__all_roots:
                if root.root_name[1] == moving_dist:
                    available_root = Mark(root, 'available')
                    self.__all_marks.add(available_root)

    def __move_or_select_piece(self, root):
        self.__unselect_all_roots()
        if self.__taken_piece is not None:
            if root.root_name[1] in self.__taken_piece.movable_roots:
                for piece in self.__all_pieces:
                    if piece.root_name == root.root_name:
                        self.kill_piece(piece)
                self.__taken_piece.move_to_root(root)
            else:
                self.__taken_piece.move_to_root(self.__pressed_root)
            if self.__taken_piece.is_moved:
                self.__after_move_preps(self.__taken_piece, root)
            else:
                self.__select_root(self.__pressed_root)
                root.is_selected ^= True
                self.__selected_piece = self.__taken_piece
            self.__taken_piece = None
        elif self.__selected_piece is not None:
            self.__unmark_all_marks()
            if root.root_name[1] in self.__selected_piece.movable_roots:
                for piece in self.__all_pieces:
                    if piece.root_name == root.root_name:
                        self.kill_piece(piece)
                self.__selected_piece.move_to_root(root)
            else:
                self.__selected_piece.move_to_root(self.__pressed_root)
            if self.__selected_piece.is_moved:
                self.__after_move_preps(self.__selected_piece, root)
            self.__selected_piece = None

    def kill_piece(self, piece):
        piece.kill()
        self.__all_pieces.remove(piece)

    def __write_to_board_data(self, piece):
        value = letters.find(piece.root_name[0][0])
        row = self.__count - int(piece.root_name[0][1])
        prev_value = letters.find(piece.prev_root_name[0][0])
        prev_row = self.__count - int(piece.prev_root_name[0][1])
        self.__board_data[prev_row][prev_value] = 0
        self.__board_data[row][value] = piece.piece_name

        self.__write_fen_from_board()

    def __after_move_preps(self, piece, root):
        self.__unmark_all_marks()
        self.__pressed_root.kept = False
        root.kept = True
        self.__other_map[2] = '-'

        if piece.piece_name in ['p', 'P']:
            self.__pawns_after_move_logic(piece)

        if piece.piece_name in ['k', 'K']:
            self.__kings_after_move_logic(piece)

        if piece.piece_name in ['R', 'r']:
            self.__rooks_after_move_logic(piece)

        if self.__other_map[1] == '':
            self.__other_map[1] = '-'
        piece.first_move = False
        self.__check_check(piece)
        self.write_piece_positions()
        self.__change_turn()
        self.__write_to_board_data(piece)

    def __pawns_after_move_logic(self, piece):
        if piece.first_move and piece.root_name[1][1] - piece.prev_root_name[1][1] in [2, -2]:
            self.__other_map[2] = piece.root_name[0]

    def __kings_after_move_logic(self, piece):
        piece.is_long_castling_possible = False
        piece.is_short_castling_possible = False
        self.__other_map[1] = self.__other_map[1].replace('KQ' if piece.color == 'w' else 'kq', '')

    def __rooks_after_move_logic(self, piece):
        if (piece.first_move and
                piece.root_name[1][0] - self.__get_piece_pos_by_name('K' if piece.color == 'w'
                                                                 else 'k') > 0):
            self.__other_map[1] = self.__other_map[1].replace('K' if piece.color == 'w' else 'k', '')
        else:
            self.__other_map[1] = self.__other_map[1].replace('Q' if piece.color == 'w' else 'q', '')

    def __castling_logic(self):
        colors = {'whites': ('KQ', 'K', 'Q'), 'blacks': ('kq', 'k', 'q')}
        for i in colors:  # What castlings can be done
            print(f'Both castlings possible for {i}' if colors[i][0] in self.__other_map[1]
                  else f'Short castling for {i}' if colors[i][1] in self.__other_map[1]
                  else f'Long castling for {i}' if colors[i][2] in self.__other_map[1]
                  else f'No possible castlings for {i}')

    def __check_check(self, piece):
        piece.check_movables()
        king_pos = self.__get_piece_pos_by_name('K' if piece.color == 'b' else 'k')
        if king_pos in piece.movable_roots:
            self.__check_logic(king_pos)

    def __check_logic(self, king_coords):
        print('Check')
        check = Check(self.__get_piece_by_piece_pos(king_coords))
        self.__all_checks.add(check)

    def __change_turn(self):
        self.__turn = 'w' if self.__turn == 'b' else 'b'
        self.__other_map[0] = self.__turn

    def __unmark_all_marks(self):
        """Removes all marks from roots"""
        self.__all_marks.empty()
        for root in self.__all_roots:
            root.mark = False

    def __unselect_all_roots(self):
        """Removes all selects from roots"""
        self.__all_selects.empty()
        self.__all_checks.empty()

    def __grand_update(self):
        """Refreshes the whole scene on the screen"""
        self.__all_roots.draw(self.__screen)
        self.__all_input_boxes.draw(self.__screen)
        self.__all_selects.draw(self.__screen)
        self.__all_checks.draw(self.__screen)
        self.__all_marks.draw(self.__screen)
        self.__all_pieces.draw(self.__screen)
        pg.display.update()


class InputBox(pg.sprite.Sprite):
    """All the input boxes main class"""
    def __init__(self, board_rect: pg.Rect):
        super().__init__()
        x, y = board_rect.x, board_rect.y
        width, height = board_rect.width, board_rect.height
        self.input_box_font_size = FONT_INPUT_BOX_SIZE
        self.input_box_font = pg.font.Font(FONT_TEXT_PATH, self.input_box_font_size)
        self.text = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.__fen_text = None
        self.active = False
        self.image = pg.Surface((width, INPUT_BOX_SIZE)).convert_alpha()
        self.image.fill(BLACK)
        self.rect = pg.Rect(x, 2 * y + height, width, INPUT_BOX_SIZE)
        self.__update_text()

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
        """Updates the input box if any changes have been made"""
        self.image.fill(BLACK)
        pg.draw.rect(self.image,
                     INPUT_FONT_COLOR if self.active else WHITE,
                     (0, 0, self.rect.width, self.rect.height), 2)
        self.__fen_text = self.input_box_font.render(self.text, True, INPUT_FONT_COLOR)
        self.__adapt_text()
        self.image.blit(self.__fen_text, (9, 9))

    def __adapt_text(self):
        if (self.__fen_text.get_rect().width + 14 > self.rect.width or
                self.__fen_text.get_rect().height + 14 > self.rect.height):
            self.input_box_font_size -= 1
            self.input_box_font = pg.font.Font(FONT_TEXT_PATH, self.input_box_font_size)
            self.__fen_text = self.input_box_font.render(self.text, True, INPUT_FONT_COLOR)


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
        self.is_selected = False
        self.kept = False


class Mark(pg.sprite.Sprite):
    """Root mark class"""

    def __init__(self, root: Root, mark_type):
        super().__init__()
        picture = (pg.image.load(IMG_PATH + OTHER_IMG_PATH + 'mark.png').convert_alpha()
                   if mark_type == 'mark' else
                   pg.image.load(IMG_PATH + OTHER_IMG_PATH + 'available.png').convert_alpha())
        self.image = pg.transform.scale(picture, (ROOT_SIZE, ROOT_SIZE))
        if mark_type == 'available':
            self.image.set_alpha(120)
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


class Check(pg.sprite.Sprite):
    """Root selection class"""

    def __init__(self, root: Root):
        super().__init__()
        self.image = pg.Surface((ROOT_SIZE, ROOT_SIZE)).convert_alpha()
        self.image.fill(CHECK_ROOT_COLOR)
        self.rect = pg.Rect((root.rect.x, root.rect.y), (ROOT_SIZE, ROOT_SIZE))
        self.root_name = root.root_name
