from konfig import *
import chess_game_module
import pygame as pg


class Piece(pg.sprite.Sprite):
    """Main piece class"""

    def __init__(self, root_size: int, color: str, root_name: str, file_postfix: str, roots_dict: dict):
        super().__init__()
        image = pg.image.load(IMG_PATH + PIECE_IMG_PATH + color + file_postfix).convert_alpha()
        self.image = pg.transform.scale(image, (root_size, root_size))
        self.rect = self.image.get_rect()
        self.color = color
        self.prev_root_name = None
        self.root_name = root_name
        self.is_moved = False
        self.first_move = True
        self.is_short_castling_possible = True
        self.is_long_castling_possible = True
        self.movable_roots_r = [-8, -1, 1, 8]
        self.movable_roots_b = [-9, -7, 7, 9]
        self.movable_roots = []
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
        else:
            self.is_moved = False

    def remove_leak_movables(self):
        self.remove_duplicates_in_movables()
        print(self.movable_roots)
        movable = 0
        print(self.pieces_positions)
        while movable < len(self.movable_roots) - 1:
            for piece_pos in self.pieces_positions:
                if (self.roots_dict[self.root_name] + self.movable_roots[movable]
                        == self.roots_dict[piece_pos[0]]):
                    if piece_pos[1] == self.color:
                        self.movable_roots.remove(self.movable_roots[movable])
                        movable -= 1
                        print(self.movable_roots)
            movable += 1

    def remove_duplicates_in_movables(self):
        self.movable_roots = list(dict.fromkeys(self.movable_roots))


class King(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_king.png', roots_dict)
        self.piece_name = 'K' if color == 'w' else 'k'

    def check_movables(self):
        for pos in self.movable_roots_r + self.movable_roots_b:
            if self.roots_dict[self.root_name] + pos in self.roots_dict.values():
                self.movable_roots.append(pos)
        if self.color == 'w':
            if (self.roots_dict[self.root_name] + 2 in self.roots_dict.values()
                    and self.is_short_castling_possible):
                self.movable_roots.append(2)
            if (self.roots_dict[self.root_name] - 2 in self.roots_dict.values()
                    and self.is_long_castling_possible):
                self.movable_roots.append(-2)
        else:
            if (self.roots_dict[self.root_name] - 2 in self.roots_dict.values()
                    and self.is_short_castling_possible):
                self.movable_roots.append(-2)
            if (self.roots_dict[self.root_name] + 2 in self.roots_dict.values()
                    and self.is_long_castling_possible):
                self.movable_roots.append(2)
        self.remove_leak_movables()


class Queen(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_queen.png', roots_dict)
        self.piece_name = 'Q' if color == 'w' else 'q'

    def check_movables(self):
        not_calculated = True
        break_check1 = False
        break_check2 = False
        index = 1
        while not_calculated:
            for pos in self.movable_roots_b + self.movable_roots_r:
                if self.roots_dict[self.root_name] + pos * index in self.roots_dict.values():
                    self.movable_roots.append(pos * index)
                elif pos in self.movable_roots_b:
                    break_check1 = True
                elif pos in self.movable_roots_r:
                    break_check2 = True
            index += 1
            if break_check1 and break_check2:
                not_calculated = False
        self.remove_leak_movables()


class Rook(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_rook.png', roots_dict)
        self.piece_name = 'R' if color == 'w' else 'r'

    def check_movables(self):
        not_calculated = True
        break_check = False
        index = 1
        while not_calculated:
            movables_length = len(self.movable_roots)
            for pos in self.movable_roots_r:
                if self.roots_dict[self.root_name] + pos * index in self.roots_dict.values():
                    self.movable_roots.append(pos * index)
                if len(self.movable_roots) == movables_length:
                    break_check = True
            index += 1
            if break_check:
                not_calculated = False
        self.remove_leak_movables()


class Bishop(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_bishop.png', roots_dict)
        self.piece_name = 'B' if color == 'w' else 'b'

    def check_movables(self):
        not_calculated = True
        break_check = False
        index = 1
        while not_calculated:
            movables_length = len(self.movable_roots)
            for pos in self.movable_roots_b:
                if self.roots_dict[self.root_name] + pos * index in self.roots_dict.values():
                    if int((self.roots_dict_keys[self.roots_dict_values.index(self.roots_dict[self.root_name]
                                                                              + pos * index)][1]) != self.roots_dict[
                               self.root_name] + pos * (index - 1)):
                        self.movable_roots.append(pos * index)
            if len(self.movable_roots) == movables_length:
                break_check = True
            index += 1
            if break_check:
                not_calculated = False
        self.remove_leak_movables()


class Knight(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_knight.png', roots_dict)
        self.piece_name = 'N' if color == 'w' else 'n'
        self.movable_roots_n = [-17, -15, -10, -6, 6, 10, 15, 17]

    def check_movables(self):
        for pos in self.movable_roots_n:
            print(self.roots_dict[self.root_name] + pos)
            if self.roots_dict[self.root_name] + pos in self.roots_dict.values():
                if pos in [-6, 6]:
                    if (self.roots_dict_keys[self.roots_dict_values.index(self.roots_dict[self.root_name] +
                                                                          pos)][1] != self.root_name[1]):
                        self.movable_roots.append(pos)
                    continue
                self.movable_roots.append(pos)
        self.remove_leak_movables()


class Pawn(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_pawn.png', roots_dict)
        self.able_to_destroy_left = False
        self.able_to_destroy_right = False
        self.piece_name = 'P' if color == 'w' else 'p'

    def check_movables(self):
        if self.color == 'w':
            if self.roots_dict[self.root_name] - 8 in self.roots_dict.values():
                self.movable_roots += [-8]
            if self.able_to_destroy_left and self.roots_dict[self.root_name] - 9 in self.roots_dict.values():
                self.movable_roots += [-9]
            if self.able_to_destroy_right and self.roots_dict[self.root_name] - 7 in self.roots_dict.values():
                self.movable_roots += [-7]
        else:
            if self.roots_dict[self.root_name] + 8 in self.roots_dict.values():
                self.movable_roots += [8]
            if self.able_to_destroy_right and self.roots_dict[self.root_name] + 9 in self.roots_dict.values():
                self.movable_roots += [9]
            if self.able_to_destroy_left and self.roots_dict[self.root_name] + 7 in self.roots_dict.values():
                self.movable_roots += [7]
        if self.first_move and (self.roots_dict[self.root_name] + 16 if self.color == 'b'
        else self.roots_dict[self.root_name] - 16) in self.roots_dict.values():
            self.movable_roots.append(16 if self.color == 'b' else -16)
        self.remove_leak_movables()
