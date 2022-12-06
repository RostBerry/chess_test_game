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
        self.all_roots = Common.all_roots
        self.piece_color_break_check = False
        self.roots_dict = roots_dict
        self.pieces_positions = None
        self.roots_dict_keys = list(self.roots_dict.keys())
        self.roots_dict_values = list(self.roots_dict.values())

    def move_to_root(self, root):
        """Moves the piece to the root"""
        root_copy = root.rect.copy()
        self.rect.center = root_copy.center
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

        new_possible_movables = self.all_possible_roots.copy()
        for root in self.all_possible_roots:
            for piece in Common.all_pieces:
                if piece.root_name[1] == root:
                    self.all_possible_takeable_roots.append(root)
                    new_possible_movables.remove(root)
        self.all_possible_roots = new_possible_movables

    def movable_checking_loop_with_continuing(self, movable_roots):
        for movable in movable_roots:

            offset = (self.column + movable[0], self.row + movable[1])
            while True:
                if offset in self.roots_dict_values:
                    self.all_possible_roots.append(offset)
                    if self.piece_check_on_path(offset):
                        self.all_possible_takeable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable[0], offset[1] + movable[1])

    def __check_check(self, offset):
        pass

    def piece_color_check(self, offset):
        for root in Common.all_roots:
            if root.root_name[1] == offset:
                for piece_pos in self.pieces_positions:
                    if piece_pos[0][0] == root.root_name[0]:
                        if piece_pos[1] != self.color:
                            self.piece_color_break_check = True
                        else:
                            return False
        return True

    def piece_color_check_in_loop(self, offset):
        for root in Common.all_roots:
            if root.root_name[1] == offset:
                for piece_pos in self.pieces_positions:
                    if piece_pos[0][0] == root.root_name[0]:
                        if piece_pos[1] == self.color:
                            return False
        return True

    def piece_check_on_path(self, offset):
        for root in Common.all_roots:
            if root.root_name[1] == offset:
                for piece in self.pieces_positions:
                    if piece[0][0] == root.root_name[0]:
                        self.piece_color_break_check = True
                    else:
                        return True
        return False

    def specific_move_check(self, offset):
        for root in Common.all_roots:
            if root.root_name[1] == offset:
                for piece in self.pieces_positions:
                    if piece[0][0] == root.root_name[0]:
                        return False
        return True

    def remove_duplicates_in_movables(self):
        pass
        # self.movable_roots = list(dict.fromkeys(self.movable_roots))
        # self.takeable_roots = list(dict.fromkeys(self.takeable_roots))
        # self.all_possible_roots = list(dict.fromkeys(self.all_possible_roots))
        # self.all_possible_takeable_roots = list(dict.fromkeys(self.all_possible_takeable_roots))
        # print(self.all_possible_roots, self.all_possible_takeable_roots)


# noinspection PyTypeChecker
class King(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_king.png', roots_dict)
        self.piece_name = 'K' if color == 'w' else 'k'
        self.is_short_castling_possible = True
        self.is_long_castling_possible = True
        self.castling_roots = []

    def check_movables(self):
        self.annul_roots()

        self.movables_checking_loop(self.movable_roots_r + self.movable_roots_b)

        if ((self.column - 1, self.row) in self.movable_roots and
                self.is_long_castling_possible and
                self.specific_move_check((self.column - 3, self.row)) and
                (self.column - 2, self.row) in self.roots_dict.values()
                and self.piece_color_check((self.column - 2, self.row))):
            self.movable_roots.append((self.column - 2, self.row))
            self.castling_roots.append((self.column - 2, self.row))

        if ((self.column + 1, self.row) in self.movable_roots and
                self.is_short_castling_possible and
                (self.column + 2, self.row) in self.roots_dict.values()
                and self.piece_color_check((self.column + 2, self.row))):
            self.movable_roots.append((self.column + 2, self.row))
            self.castling_roots.append((self.column + 2, self.row))

        self.remove_duplicates_in_movables()


# noinspection PyTypeChecker
class Queen(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_queen.png', roots_dict)
        self.piece_name = 'Q' if color == 'w' else 'q'

    def check_movables(self):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_b + self.movable_roots_r)
        self.remove_duplicates_in_movables()


# noinspection PyTypeChecker
class Rook(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_rook.png', roots_dict)
        self.piece_name = 'R' if color == 'w' else 'r'
        self.castling_pos = None

    def check_movables(self):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_r)
        self.remove_duplicates_in_movables()


# noinspection PyTypeChecker
class Bishop(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_bishop.png', roots_dict)
        self.piece_name = 'B' if color == 'w' else 'b'

    def check_movables(self):
        self.annul_roots()
        self.movable_checking_loop_with_continuing(self.movable_roots_b)
        self.remove_duplicates_in_movables()


# noinspection PyTypeChecker
class Knight(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_knight.png', roots_dict)
        self.piece_name = 'N' if color == 'w' else 'n'
        self.movable_roots_n = [(-1, -2), (1, -2), (-2, -1), (2, -1),  # Up
                                (-2, 1), (2, 1), (-1, 2), (1, 2)]  # Down

    def check_movables(self):
        self.annul_roots()
        self.movables_checking_loop(self.movable_roots_n)
        self.remove_duplicates_in_movables()


# noinspection PyTypeChecker
class Pawn(Piece):
    def __init__(self, color: str, root: str, roots_dict):
        super().__init__(color, root, '_pawn.png', roots_dict)
        self.piece_name = 'P' if color == 'w' else 'p'
        self.taking_on_the_pass = None
        self.passing_pawn_pos = None

    def check_movables(self):
        self.annul_roots()

        move = (self.column, self.row - 1) if self.color == 'w' else (self.column, self.row + 1)
        if (move in self.roots_dict.values()
                and self.specific_move_check(move)):
            self.movable_roots.append(move)

        move = (self.column, self.row - 2) if self.color == 'w' else (self.column, self.row + 2)
        if (self.first_move and move in self.roots_dict.values()
                and self.specific_move_check(move)
                and self.piece_color_check((move[0], move[1] + (1 if self.color == 'w' else -1)))):
            self.movable_roots.append(move)

        move = (self.column + 1, self.row - 1) if self.color == 'w' else (self.column - 1, self.row + 1)
        pawn_passing_move = (move[0], move[1] + (1 if self.color == 'w' else -1))
        pawn_passing_check = (not self.specific_move_check(pawn_passing_move)
                              and self.piece_color_check(pawn_passing_move)
                              and Common.other_map[2] != '-')
        if (move in self.roots_dict.values()
                and (not self.specific_move_check(move)
                     or pawn_passing_check)
                and self.piece_color_check(move)):
            self.takeable_roots.append(move)
            if pawn_passing_check:
                self.taking_on_the_pass = move
                self.passing_pawn_pos = pawn_passing_move

        move = (self.column - 1, self.row - 1) if self.color == 'w' else (self.column + 1, self.row + 1)
        pawn_passing_move = (move[0], move[1] + (1 if self.color == 'w' else -11))
        pawn_passing_check = (not self.specific_move_check(pawn_passing_move)
                              and self.piece_color_check(pawn_passing_move)
                              and Common.other_map[2] != '-')
        if (move in self.roots_dict.values()
                and (not self.specific_move_check(move)
                     or pawn_passing_check)
                and self.piece_color_check(move)):
            self.takeable_roots.append(move)
            if pawn_passing_check:
                self.taking_on_the_pass = move
                self.passing_pawn_pos = pawn_passing_move

        self.remove_duplicates_in_movables()
