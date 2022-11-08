from konfig import *
import pygame as pg

class Piece(pg.sprite.Sprite):

    def __init__(self, root_size: int, color: str, root_name: str, file_postfix: str):
        super().__init__()
        image = pg.image.load(IMG_PATH + PIECE_IMG_PATH + color + file_postfix).convert_alpha()
        self.image = pg.transform.scale(image, (root_size, root_size))
        self.rect = self.image.get_rect()
        self._color = color
        self.root_name = root_name

    def move_to_root(self, root):
        self.rect = root.rect.copy()
        self.root_name = root.root_name

class King(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_king.png')


class Queen(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_queen.png')


class Rook(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_rook.png')


class Bishop(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_bishop.png')


class Knight(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_knight.png')


class Pawn(Piece):
    def __init__(self, root_size: int, color: str, root: str):
        super().__init__(root_size, color, root, '_pawn.png')