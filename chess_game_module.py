from pieces import *
import pyperclip as clip
import board_data
from konfig import *
from common import *
import random


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

    def __play_move_sound(self):
        """Activates when a piece have been moved"""
        sound = pg.mixer.Sound(MUSIC_PATH + MOVE_SOUND + str(random.randint(1, 7)) + '.ogg')
        sound.play()

    def __prepare_screen(self):
        """Draws background"""
        background_img = Image.open(IMG_PATH + STATIC_IMG_PATH + BACKGROUND_IMG).resize(WINDOW_SIZE)
        background_img = pg.image.fromstring(background_img.tobytes(),
                                             background_img.size,
                                             background_img.mode)
        self.__screen.blit(background_img, (0, 0))

    def __draw_play_board(self):
        """Draws play board"""
        total_width = self.__count * self.__size
        # Creating main board objects
        num_fields = self.__create_num_fields()
        Common.all_roots = self.__create_all_roots()
        num_fields_depth = num_fields[0].get_width()
        play_board_view = pg.Surface((2 * num_fields_depth + total_width,
                                     2 * num_fields_depth + total_width), pg.SRCALPHA).convert_alpha()

        board_background_img = Image.open(IMG_PATH +
                                          STATIC_IMG_PATH +
                                          BOARD_BACKGROUND_IMG).resize((play_board_view.get_width(),
                                                                        play_board_view.get_height()))
        board_background_img = pg.image.fromstring(board_background_img.tobytes(),
                                                   board_background_img.size,
                                                   board_background_img.mode)

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
        for piece in Common.all_pieces:
            for root in Common.all_roots:
                # Places the piece on the root
                if piece.root_name[0] == root.root_name[0]:
                    piece.rect = root.rect.copy()
                    root.kept = True
        self.write_piece_positions()

    def __setup_board_with_fen(self):
        """Decodes the Forsyth Edwards Notation and setups new board konfig"""
        # Separating the fen string to pieces placement and additional info
        pieces_and_other_map = self.__input_box.text.split(' ')
        Common.pieces_map = pieces_and_other_map[0].split('/')
        Common.other_map = pieces_and_other_map[1:]
        # Replacing the board data with new pieces placement
        for row in range(len(self.__board_data)):  # Running through board data rows
            value = 0
            piece_map_offset = 0
            while value < len(self.__board_data[row]):  # Running through board data values in rows
                offset = 0
                try:
                    for i in range(int(Common.pieces_map[row][value - piece_map_offset])):  # Placing the empty
                        self.__board_data[row][value + i] = 0                              # roots if those have
                        offset = i                                                        # been found
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

        Common.all_pieces.empty()
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

        for info in Common.other_map:
            fen_string += ' ' + info

        self.__input_box.text = fen_string  # Putting the fen string to the input bar
        self.__input_box.put_char('')  # Updating the text

    def __create_piece(self, piece_sym: str, board_data_coord: tuple):
        """Creates a single piece"""
        root_name = self.__to_root_name(board_data_coord)
        piece_tuple = self.__pieces[piece_sym]
        class_name = globals()[piece_tuple[0]]
        return class_name(piece_tuple[1], root_name, self.roots_dict)

    def write_piece_positions(self):
        pieces_root_names = []
        for piece in Common.all_pieces:
            pieces_root_names.append((piece.root_name, piece.color))
        for piece in Common.all_pieces:
            piece.pieces_positions = tuple(pieces_root_names)
            piece.all_roots = Common.all_roots

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

    def __get_piece_on_click(self, root):
        """Returns the clicked piece"""
        for piece in Common.all_pieces:
            if piece.root_name[0] == root.root_name[0]:
                if piece.color == self.__turn and self.__selected_piece is None:
                    if self.__taken_piece is None:
                        return piece
                    else:
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
        piece.movable_roots = []
        piece.takeable_roots = []
        piece.check_movables()
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
                self.__after_move_preps(self.__taken_piece, root)
            else:
                self.__select_root(self.__pressed_root)
                root.is_selected ^= True
                self.__selected_piece = self.__taken_piece
            self.__taken_piece = None
        elif self.__selected_piece is not None:
            self.__unmark_all_marks()
            if root.root_name[1] in self.__selected_piece.movable_roots + self.__selected_piece.takeable_roots:
                for piece in Common.all_pieces:
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
        Common.all_pieces.remove(piece)

    def __write_to_board_data(self, piece):
        value = letters.find(piece.root_name[0][0])
        row = self.__count - int(piece.root_name[0][1])
        print(piece.prev_root_name)
        prev_value = letters.find(piece.prev_root_name[0][0])
        prev_row = self.__count - int(piece.prev_root_name[0][1])
        self.__board_data[prev_row][prev_value] = 0
        self.__board_data[row][value] = piece.piece_name

        self.__write_fen_from_board()

    def __after_move_preps(self, piece, root):
        self.__play_move_sound()
        self.__unmark_all_marks()
        self.__pressed_root.kept = False
        root.kept = True
        Common.other_map[2] = '-'

        if piece.piece_name in ['p', 'P']:
            self.__pawns_after_move_logic(piece)

        if piece.piece_name in ['k', 'K']:
            self.__kings_after_move_logic(piece)

        if piece.piece_name in ['R', 'r']:
            self.__rooks_after_move_logic(piece)

        if Common.other_map[1] == '':
            Common.other_map[1] = '-'
        piece.first_move = False
        self.__check_check(piece)
        self.write_piece_positions()
        self.__change_turn()
        self.__write_to_board_data(piece)

    def __pawns_after_move_logic(self, pawn: Pawn):
        if pawn.root_name[1] == pawn.taking_on_the_pass:
            self.kill_piece(self.__get_piece_by_piece_pos(pawn.passing_pawn_pos))
        if pawn.first_move and pawn.root_name[1][1] - pawn.prev_root_name[1][1] in [2, -2]:
            Common.other_map[2] = pawn.root_name[0]
        pawn.taking_ont_the_pass = None
        pawn.passing_pawn_pos = None

    def __kings_after_move_logic(self, king: King):
        king.is_long_castling_possible = False
        king.is_short_castling_possible = False
        Common.other_map[1] = Common.other_map[1].replace('KQ' if king.color == 'w' else 'kq', '')
        if king.root_name[1] in king.castling_roots:
            self.__do_castle(king, 'Long' if king.castling_roots[0][0] -
                             king.prev_root_name[1][0] < 0 else 'Short')
        king.castling_roots = []

    def __rooks_after_move_logic(self, rook: Rook):
        king_pos = self.__get_piece_pos_by_name('K' if rook.color == 'w' else 'k')
        if king_pos is not None:
            if (rook.first_move and
                    rook.root_name[1][0] -
                    king_pos[0] > 0):
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
            print('prob rook coords', piece.root_name, piece.piece_name)
            print('prev', king.prev_root_name)
            if (piece.piece_name == ('R' if king.color == 'w' else 'r')
                    and (piece.root_name[1][0] - king.prev_root_name[1][0] < 0
                         if castling_type == 'Long'
                         else piece.root_name[1][0] - king.prev_root_name[1][0] > 0)):
                print('found')
                rook = piece
        castling_root = self.__get_root_by_pos((king.root_name[1][0] +
                                                (-1 if castling_type == 'Short' else 1),
                                                king.root_name[1][1]))
        if rook is not None:
            rook.move_to_root(castling_root)
            self.__write_to_board_data(rook)

    def __check_check(self, piece):
        piece.check_movables()
        king_pos = self.__get_piece_pos_by_name('K' if piece.color == 'b' else 'k')
        if king_pos in piece.movable_roots:
            self.__check_logic()

    def __check_logic(self):
        print('Check')

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

    def __grand_update(self):
        """Refreshes the whole scene on the screen"""
        Common.all_roots.draw(self.__screen)
        self.__all_input_boxes.draw(self.__screen)
        self.__all_selects.draw(self.__screen)
        self.__all_checks.draw(self.__screen)
        Common.all_marks.draw(self.__screen)
        Common.all_pieces.draw(self.__screen)
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
        image = Image.open(IMG_PATH + self.color).resize((size, size))
        self.image = pg.image.fromstring(image.tobytes(), image.size, image.mode)
        self.rect = pg.Rect(x * size, y * size, size, size)
        self.mark = False
        self.is_selected = False
        self.kept = False


class Mark(pg.sprite.Sprite):
    """Root mark class"""

    def __init__(self, root: Root, mark_type):
        super().__init__()
        picture = Image.open(IMG_PATH + OTHER_IMG_PATH + mark_type + '.png').resize((ROOT_SIZE, ROOT_SIZE))
        self.image = (pg.image.fromstring(picture.tobytes(), picture.size, picture.mode).convert_alpha())
        if mark_type in ['available', 'takeable']:
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
