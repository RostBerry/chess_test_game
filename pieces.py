from konfig import *
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
        self.row = self.root_name[1][1]
        self.column = self.root_name[1][0]
        self.is_moved = False
        self.movable_roots_r = [(-1, 0), (1, 0),  # Left/Right
                                (0, 1), (0, -1)]  # Up/Down
        self.movable_roots_b = [(-1, -1), (1, -1),  # Up
                                (-1, 1), (1, 1)]  # Down
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
            self.row = self.root_name[1][1]
            self.column = self.root_name[1][0]
        else:
            self.is_moved = False

    def remove_leak_movables(self):
        self.remove_duplicates_in_movables()
        print(self.movable_roots)
        movable = 0
        print(self.pieces_positions)
        while movable < len(self.movable_roots):
            for piece_pos in self.pieces_positions:
                if (self.roots_dict[self.root_name[0]] + self.movable_roots[movable]
                        == self.roots_dict[piece_pos[0][0]]):
                    if piece_pos[0][1] == self.color:
                        self.movable_roots.remove(self.movable_roots[movable])
                        movable -= 1
                        print(self.movable_roots)
            movable += 1

    def remove_duplicates_in_movables(self):
        self.movable_roots = list(dict.fromkeys(self.movable_roots))


# noinspection PyTypeChecker
class King(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_king.png', roots_dict)
        self.piece_name = 'K' if color == 'w' else 'k'
        self.is_short_castling_possible = True
        self.is_long_castling_possible = True

    def check_movables(self):
        for movable_root in self.movable_roots_b:
            if (self.column + movable_root[0], self.row + movable_root[1]) in self.roots_dict.values():
                self.movable_roots.append((self.column + movable_root[0], self.row + movable_root[1]))
        for movable_root in self.movable_roots_r:
            if (self.column + movable_root[0], self.row + movable_root[1]) in self.roots_dict.values():
                self.movable_roots.append((self.column + movable_root[0], self.row + movable_root[1]))
        self.remove_leak_movables()


class Queen(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_queen.png', roots_dict)
        self.piece_name = 'Q' if color == 'w' else 'q'

    def check_movables(self):
        for movable_root in self.movable_roots_b:
            prev_movables = self.movable_roots.copy()
            print(prev_movables)
            offset = (self.column + movable_root[0], self.row + movable_root[1])
            while True:
                print(offset)
                if offset in self.roots_dict.values():
                    self.movable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable_root[0], offset[1] + movable_root[1])
        for movable_root in self.movable_roots_r:
            prev_movables = self.movable_roots.copy()
            print(prev_movables)
            offset = (self.column + movable_root[0], self.row + movable_root[1])
            while True:
                print(offset)
                if offset in self.roots_dict.values():
                    self.movable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable_root[0], offset[1] + movable_root[1])
        self.remove_leak_movables()


class Rook(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_rook.png', roots_dict)
        self.piece_name = 'R' if color == 'w' else 'r'

    def check_movables(self):
        for movable_root in self.movable_roots_r:
            prev_movables = self.movable_roots.copy()
            print(prev_movables)
            offset = (self.column + movable_root[0], self.row + movable_root[1])
            while True:
                print(offset)
                if offset in self.roots_dict.values():
                    self.movable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable_root[0], offset[1] + movable_root[1])
        self.remove_leak_movables()


# noinspection PyTypeChecker
class Bishop(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_bishop.png', roots_dict)
        self.piece_name = 'B' if color == 'w' else 'b'

    def check_movables(self):
        for movable_root in self.movable_roots_b:
            prev_movables = self.movable_roots.copy()
            print(prev_movables)
            offset = (self.column + movable_root[0], self.row + movable_root[1])
            while True:
                print(offset)
                if offset in self.roots_dict.values():
                    self.movable_roots.append(offset)
                else:
                    break
                offset = (offset[0] + movable_root[0], offset[1] + movable_root[1])
        self.remove_leak_movables()


# noinspection PyTypeChecker
class Knight(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_knight.png', roots_dict)
        self.piece_name = 'N' if color == 'w' else 'n'
        self.movable_roots_n = [(-1, -2), (1, -2), (-2, -1), (2, -1),  # Up
                                (-2, 1), (2, 1), (-1, 2), (1, 2)]  # Down

    def check_movables(self):
        for movable_root in self.movable_roots_n:
            if (self.column + movable_root[0], self.row + movable_root[1]) in self.roots_dict.values():
                self.movable_roots.append((self.column + movable_root[0], self.row + movable_root[1]))


# noinspection PyTypeChecker
class Pawn(Piece):
    def __init__(self, root_size: int, color: str, root: str, roots_dict):
        super().__init__(root_size, color, root, '_pawn.png', roots_dict)
        self.able_to_destroy_left = False
        self.able_to_destroy_right = False
        self.first_move = True
        self.piece_name = 'P' if color == 'w' else 'p'

    def check_movables(self):
        if self.color == 'w':
            if (self.column, self.row - 1) in self.roots_dict.values():
                self.movable_roots.append((self.column, self.row - 1))
            if self.first_move and (self.column, self.row - 2) in self.roots_dict.values():
                self.movable_roots.append((self.column, self.row - 2))
            if self.able_to_destroy_right and (self.column + 1, self.row - 1) in self.roots_dict.values():
                self.movable_roots.append((self.column + 1, self.row - 1))
            if self.able_to_destroy_left and (self.column - 1, self.row - 1) in self.roots_dict.values():
                self.movable_roots.append((self.column - 1, self.row - 1))
        else:
            if (self.column, self.row + 1) in self.roots_dict.values():
                self.movable_roots.append((self.column, self.row + 1))
            if self.first_move and (self.column, self.row + 2) in self.roots_dict.values():
                self.movable_roots.append((self.column, self.row + 2))
            if self.able_to_destroy_right and (self.column - 1, self.row + 1) in self.roots_dict.values():
                self.movable_roots.append((self.column - 1, self.row + 1))
            if self.able_to_destroy_left and (self.column + 1, self.row + 1) in self.roots_dict.values():
                self.movable_roots.append((self.column + 1, self.row + 1))
        self.remove_leak_movables()
