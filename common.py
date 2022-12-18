import pygame as pg
from konfig import *


class Common:
    mode = None
    is_flipped = False
    all_pieces = pg.sprite.Group()
    all_roots = pg.sprite.Group()
    all_marks = pg.sprite.Group()
    all_choosing_pieces = pg.sprite.Group()
    all_choosing_cells = pg.sprite.Group()
    all_buttons = pg.sprite.Group()
    roots_dict = {}
    pieces_map = []
    other_map = []
    pieces_positions = ()
    PALETTE = 'Green'
    DARK_ROOT_COLOR = PALETTES[PALETTE][2]
    LIGHT_ROOT_COLOR = PALETTES[PALETTE][0]
    BOARD_BACKGROUND_COLOR = PALETTES[PALETTE][3]
    BACKGROUND = PALETTES[PALETTE][1]
    ROOT_COLORS = [LIGHT_ROOT_COLOR, DARK_ROOT_COLOR]
    MAIN_COLOR = PALETTES[PALETTE][0]
    MAIN_STROKE_COLOR = PALETTES[PALETTE][3]
    SELECTED_COLOR = PALETTES[PALETTE][2]
    TEXT_COLOR = PALETTES[PALETTE][2]
    BOARD_TEXT_COLOR = PALETTES[PALETTE][1]

def renew_colors():
    Common.DARK_ROOT_COLOR = PALETTES[Common.PALETTE][2]
    Common.LIGHT_ROOT_COLOR = PALETTES[Common.PALETTE][0]
    Common.BOARD_BACKGROUND_COLOR = PALETTES[Common.PALETTE][3]
    Common.BACKGROUND = PALETTES[Common.PALETTE][1]
    Common.ROOT_COLORS = [Common.LIGHT_ROOT_COLOR, Common.DARK_ROOT_COLOR]
    Common.MAIN_COLOR = PALETTES[Common.PALETTE][0]
    Common.MAIN_STROKE_COLOR = PALETTES[Common.PALETTE][3]
    Common.SELECTED_COLOR = PALETTES[Common.PALETTE][2]
    Common.TEXT_COLOR = PALETTES[Common.PALETTE][2]
    Common.BOARD_TEXT_COLOR = PALETTES[Common.PALETTE][1]
