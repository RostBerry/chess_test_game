from konfig import *
import pygame as pg


class Piece(pg.sprite.Sprite):
    """Main piece class"""

    def __init__(self, root_size: int, color: str, root_name: str, file_postfix: str):
        super().__init__()
        image = pg.image.load(IMG_PATH + PIECE_IMG_PATH + color + file_postfix).convert_alpha()
        self.image = pg.transform.scale(image, (root_size, root_size))
        self.rect = self.image.get_rect()
        self.color = color
        self.prev_root_name = None
        self.root_name = root_name
        self.is_moved = False
        self.movable_roots_r = [-8, -1, 0, 1, 8]
        self.movable_roots_b = [-9, -7, 0, 7, 9]
        self.movable_roots = []

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


class King(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_king.png')
        self.piece_name = 'K' if color == 'w' else 'k'

    def check_movables(self, roots_dict: dict):
        for pos in self.movable_roots_r + self.movable_roots_b:
            if roots_dict[self.root_name] + pos in roots_dict.values():
                self.movable_roots.append(pos)


class Queen(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_queen.png')
        self.piece_name = 'Q' if color == 'w' else 'q'

    def check_movables(self, roots_dict: dict):
        not_calculated = True
        break_check1 = False
        break_check2 = False
        index = 1
        while not_calculated:
            for pos in self.movable_roots_b + self.movable_roots_r:
                if roots_dict[self.root_name] + pos * index in roots_dict.values():
                    self.movable_roots.append(pos * index)
                elif pos in self.movable_roots_b:
                    break_check1 = True
                elif pos in self.movable_roots_r:
                    break_check2 = True
            index += 1
            if break_check1 and break_check2:
                not_calculated = False


class Rook(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_rook.png')
        self.piece_name = 'R' if color == 'w' else 'r'

    def check_movables(self, roots_dict: dict):
        not_calculated = True
        break_check = False
        index = 1
        while not_calculated:
            for pos in self.movable_roots_r:
                if roots_dict[self.root_name] + pos * index in roots_dict.values():
                    self.movable_roots.append(pos * index)
                else:
                    break_check = True
            index += 1
            if break_check:
                not_calculated = False


class Bishop(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_bishop.png')
        self.piece_name = 'B' if color == 'w' else 'b'

    def check_movables(self, roots_dict: dict):
        not_calculated = True
        break_check = False
        index = 1
        prev_movable_roots = []
        while not_calculated:
            for pos in self.movable_roots_b:
                if roots_dict[self.root_name] + pos * index in roots_dict.values():
                    self.movable_roots.append(pos * index)
            if len(self.movable_roots) == len(prev_movable_roots):
                break_check = True
            index += 1
            prev_movable_roots = self.movable_roots
            if break_check:
                not_calculated = False


class Knight(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_knight.png')
        self.piece_name = 'N' if color == 'w' else 'n'
        self.movable_roots_n = [-17, -15, -10, -6, 0, 6, 10, 15, 17]

    def check_movables(self, roots_dict: dict):
        for pos in self.movable_roots_n:
            if roots_dict[self.root_name] + pos in roots_dict.values():
                self.movable_roots.append(pos)


class Pawn(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_pawn.png')
        self.able_to_destroy_left = True
        self.able_to_destroy_right = True
        self.piece_name = 'P' if color == 'w' else 'p'

    def check_movables(self, roots_dict: dict):
        if self.color == 'w':
            if roots_dict[self.root_name] - 8 in roots_dict.values():
                self.movable_roots += [-8]
            if self.able_to_destroy_left and roots_dict[self.root_name] - 9 in roots_dict.values():
                self.movable_roots += [-9]
            if self.able_to_destroy_right and roots_dict[self.root_name] - 7 in roots_dict.values():
                self.movable_roots += [-7]
        else:
            if roots_dict[self.root_name] + 8 in roots_dict.values():
                self.movable_roots += [8]
            if self.able_to_destroy_right and roots_dict[self.root_name] + 9 in roots_dict.values():
                self.movable_roots += [9]
            if self.able_to_destroy_left and roots_dict[self.root_name] + 7 in roots_dict.values():
                self.movable_roots += [7]
