import pygame as pg


class Common:
    all_pieces = pg.sprite.Group()
    all_roots = pg.sprite.Group()
    all_marks = pg.sprite.Group()
    all_choosing_pieces = pg.sprite.Group()
    all_choosing_cells = pg.sprite.Group()
    pieces_map = []
    other_map = []
    pieces_positions = ()
