from konfig import *
from common import *
from PIL import Image


# noinspection PyTypeChecker
class Piece(pg.sprite.Sprite):
    """Main piece class"""

    def __init__(self, color: str, root_name: str, file_postfix: str, roots_dict: dict):
        super().__init__()
        image = Image.open(IMG_PATH +
                           PIECE_IMG_PATH +
                           color +
                           file_postfix).resize((ROOT_SIZE, ROOT_SIZE))
        self.rect = image.size
        self.image = pg.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()
        self.color = color
        self.prev_root_name = None
        self.root_name = root_name
        self.row = self.root_name[1][1]
        self.column = self.root_name[1][0]
        self.is_moved = False
        self.first_move = True
        self.movable_roots_r = [(-1, 0), (1, 0),  # Left/Right
                                (0, 1), (0, -1)]  # Up/Down
        self.movable_roots_b = [(-1, -1), (1, -1),  # Up
                                (-1, 1), (1, 1)]  # Down
        self.movable_roots = []
        self.all_possible_roots = []
        self.takeable_roots = []
        self.all_possible_takeable_roots = []
        self.prob_check_roots = []
        self.all_roots = Common.all_roots
        self.piece_color_break_check = False
        self.roots_dict = roots_dict
        self.roots_dict_keys = list(self.roots_dict.keys())
        self.roots_dict_values = list(self.roots_dict.values())

    def move_to_root(self, root):
        """Moves the piece to the root"""
        root_copy = root.rect.copy()
        self.rect = root_copy
        if self.root_name != root.root_name:
            self.is_moved = True
            self.prev_root_name = self.root_name
            self.root_name = root.root_name
            self.row = self.root_name[1][1]
            self.column = self.root_name[1][0]
        else:
            self.is_moved = False

    def annul_roots(self):
        self.movable_roots = []
        self.takeable_roots = []
        self.all_possible_roots = []
        self.all_possible_takeable_roots = []
        self.prob_check_roots = []

    def movables_checking_loop(self, movables):
        for prob_movable in movables:
            offset = (self.column + prob_movable[0], self.row + prob_movable[1])
            if offset in self.roots_dict.values():
                self.all_possible_roots.append(offset)
                if self.piece_color_check(offset):
                    self.movable_roots.append(offset)
        new_movables = self.movable_roots.copy()
        for root in self.movable_roots:
            for piece in Common.all_pieces:
                if piece.root_name[1] == root and piece.color != self.color:
                    self.takeable_roots.append(root)
                    new_movables.remove(root)
        self.movable_roots = new_movables

        for root in self.all_possible_roots:
            for piece in Common.all_pieces:
                if piece.root_name[1] == root:
                    self.all_possible_takeable_roots.append(root)

    def movable_checking_loop_with_continuing(self, movable_roots):
        for movable in movable_roots:
            offset = (self.column + movable[0], self.row + movable[1])
            while True:
                if offset in self.roots_dict_values:
                    if self.piece_color_check(offset):
                        self.movable_roots.append(offset)
                        if self.piece_color_break_check:
                            self.movable_roots.remove(offset)
                            self.takeable_roots.append(offset)
                            self.piece_color_break_check = False
                            break
                    else:
                        break
                else:
                    break
                offset = (offset[0] + movable[0], offset[1] + movable[1])

            offset = (self.column + movable[0], self.row + movable[1])
            while True:
                if offset in self.roots_dict_values:
                    self.all_possible_roots.append(offset)
                    if self.piece_check_on_path(offset):
                        self.all_possible_takeable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable[0], offset[1] + movable[1])

            collision_check = 0
            offset = (self.column + movable[0], self.row + movable[1])
            while True:
                if offset in self.roots_dict_values:
                    self.piece_check_through_one(offset)
                    if self.piece_color_break_check:
                        if collision_check == 1:
                            self.prob_check_roots.append(offset)
                        self.piece_color_break_check = False
                        collision_check += 1
                else:
                    break
                offset = (offset[0] + movable[0], offset[1] + movable[1])

    def __check_check(self, offset):
        pass

    def piece_color_check(self, offset):
        for piece in Common.all_pieces:  # piece_pos looks like ((a1, (1, 1)), w)
            if piece.root_name[1] == offset:
                if piece.color != self.color:
                    self.piece_color_break_check = True
                else:
                    return False
        return True

    def piece_check_through_one(self, offset):
        for piece in Common.all_pieces:  # piece_pos looks like ((a1, (1, 1)), w)
            if piece.root_name[1] == offset:
                self.piece_color_break_check = True

    def piece_check_on_path(self, offset):
        for piece in Common.all_pieces:
            if piece.root_name[1] != offset:
                return True
        return False

    def specific_move_check(self, offset):
        for root in Common.all_roots:
            if root.root_name[1] == offset:
                for piece in Common.all_pieces:
                    if piece.root_name[1] == root.root_name[1]:
                        return False
        return True

    def remove_duplicates_in_movables(self):
        # self.movable_roots = list(dict.fromkeys(self.movable_roots))
        # self.takeable_roots = list(dict.fromkeys(self.takeable_roots))
        # self.all_possible_roots = list(dict.fromkeys(self.all_possible_roots))
        # self.all_possible_takeable_roots = list(dict.fromkeys(self.all_possible_takeable_roots))
        print('prob check roots:', self.prob_check_roots)

    def remove_future_checked_movables(self):
        old_position = self.root_name
        new_movables, new_takeables = self.movable_roots, self.takeable_roots
        for movable in self.movable_roots + self.takeable_roots:
            self.root_name = (self.root_name[0], movable)
            for piece in Common.all_pieces:
                if piece.color == ('w' if self.color == 'b' else 'b'):
                    piece.check_movables(False)
                    if piece.root_name[1] != self.root_name[1]:
                        for prob_king in Common.all_pieces:
                            if prob_king.piece_name == ('k' if self.color == 'b' else 'K'):
                                if prob_king.root_name[1] in piece.takeable_roots:
                                    (new_movables
                                     if movable in new_movables
                                     else new_takeables).remove(movable)

        self.root_name = old_position
        self.movable_roots = new_movables


# noinspection PyTypeChecker
class King(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_king.png', roots_dict)
        self.piece_name = 'K' if color == 'w' else 'k'
        self.is_short_castling_possible = True
        self.is_long_castling_possible = True
        self.castling_roots = []

    def check_castling(self, move, castling_move):
        if castling_move == (self.column - 2, self.row):
            long_castling_check = self.specific_move_check((self.column - 3, self.row))
        else:
            long_castling_check = True

        if (move in self.movable_roots and
                self.is_long_castling_possible and
                long_castling_check and
                castling_move in self.roots_dict.values()
                and self.piece_color_check(castling_move)):
            self.movable_roots.append(castling_move)
            self.castling_roots.append(castling_move)

    def check_movables(self, do_check_checking):
        self.annul_roots()

        self.movables_checking_loop(self.movable_roots_r + self.movable_roots_b)

        self.check_castling((self.column - 1, self.row), (self.column - 2, self.row))
        self.check_castling((self.column + 1, self.row), (self.column + 2, self.row))

        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()


# noinspection PyTypeChecker
class Queen(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_queen.png', roots_dict)
        self.piece_name = 'Q' if color == 'w' else 'q'

    def check_movables(self, do_check_checking):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_b + self.movable_roots_r)
        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()


# noinspection PyTypeChecker
class Rook(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_rook.png', roots_dict)
        self.piece_name = 'R' if color == 'w' else 'r'
        self.castling_pos = None

    def check_movables(self, do_check_checking):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_r)
        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()


# noinspection PyTypeChecker
class Bishop(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_bishop.png', roots_dict)
        self.piece_name = 'B' if color == 'w' else 'b'

    def check_movables(self, do_check_checking):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_b)
        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()


# noinspection PyTypeChecker
class Knight(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_knight.png', roots_dict)
        self.piece_name = 'N' if color == 'w' else 'n'
        self.movable_roots_n = [(-1, -2), (1, -2), (-2, -1), (2, -1),  # Up
                                (-2, 1), (2, 1), (-1, 2), (1, 2)]  # Down

    def check_movables(self, do_check_checking):
        self.annul_roots()
        self.movables_checking_loop(self.movable_roots_n)
        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()


# noinspection PyTypeChecker
class Pawn(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_pawn.png', roots_dict)
        self.piece_name = 'P' if color == 'w' else 'p'
        self.taking_on_the_pass_move = None
        self.passing_pawn_pos = None
        self.regular_move = None
        self.long_move = None
        self.taking_moves = []

    def annul_roots(self):
        self.movable_roots = []
        self.takeable_roots = []
        self.all_possible_roots = []
        self.all_possible_takeable_roots = []
        self.taking_on_the_pass_move = None
        self.passing_pawn_pos = None
        self.regular_move = None
        self.long_move = None
        self.taking_moves = []

    def __add_regular_move(self):
        if (self.regular_move in self.roots_dict.values()
                and self.specific_move_check(self.regular_move)):
            self.movable_roots.append(self.regular_move)

    def __add_long_move(self):
        if (self.first_move and self.long_move in self.roots_dict.values()
                and self.specific_move_check(self.regular_move)
                and self.specific_move_check(self.long_move)):
            self.movable_roots.append(self.long_move)

    def en_passant_check(self, passing_pawn, move):
        if passing_pawn.root_name[1] == (move[0], move[1] + (1 if self.color == 'w' else -1)):
            return True
        return False

    def __add_taking_and_passing_moves(self):
        for index, move in enumerate(self.taking_moves):
            passing_pawn = None
            for piece in Common.all_pieces:
                if piece.piece_name == ('p' if self.color == 'w' else 'P'):
                    if piece.root_name[0] == Common.other_map[2]:
                        passing_pawn = piece
                        break
            pawn_passing_check = (passing_pawn is not None
                                  and self.en_passant_check(passing_pawn, move))
            if (move in self.roots_dict.values()
                    and (not self.specific_move_check(move)
                         or pawn_passing_check)
                    and self.piece_color_check(move)):
                self.takeable_roots.append(move)
                if pawn_passing_check:
                    self.taking_on_the_pass_move = move
                    self.passing_pawn_pos = passing_pawn.root_name[1]

    def __get_moves(self):
        self.regular_move = (self.column, self.row - 1) if self.color == 'w' else (self.column, self.row + 1)
        self.long_move = (self.column, self.row - 2) if self.color == 'w' else (self.column, self.row + 2)
        self.taking_moves = [(self.column + 1, self.row - 1)
                             if self.color == 'w'
                             else (self.column - 1, self.row + 1),

                             (self.column - 1, self.row - 1)
                             if self.color == 'w'
                             else (self.column + 1, self.row + 1)]

    def check_movables(self, do_check_checking):
        self.annul_roots()
        self.__get_moves()

        self.__add_regular_move()

        self.__add_long_move()

        self.__add_taking_and_passing_moves()

        self.remove_duplicates_in_movables()
        if do_check_checking:
            self.remove_future_checked_movables()
