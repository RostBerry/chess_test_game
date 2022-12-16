FPS = 60
WINDOW_SIZE = (1280, 720)
MENU_WINDOW_SIZE = (1280, 720)
MAIN_BTN_SIZE = (300, 100)
ROOT_COUNT = 8
ROOT_SIZE = 70
ROOT_SUBSCRIPT = True
FONT_CHESSBOARD_PATH = 'assets/fonts/arial_black.ttf'
FONT_CHESSBOARD_SIZE = 22
FONT_TEXT_PATH = 'assets/fonts/NotCourierSans.ttf'
FONT_TEXT_SIZE = 18
FONT_INPUT_BOX_SIZE = 18
FONT_MAIN_GAME_SIZE = 96
FONT_MAIN_BUTTONS_SIZE = 70
FONT_HEADER_SIZE = 64
INPUT_FONT_COLOR = (50, 255, 50)
INPUT_BOX_SIZE = 40
IMG_PATH = 'assets/images/'
STATIC_IMG_PATH = 'static images/'
OTHER_IMG_PATH = 'other images/'
BACKGROUND_IMG = 'wood_planks.jpg'
BOARD_BACKGROUND_IMG = 'black_root.jpg'
MUSIC_PATH = 'assets/music/'
BACKGROUND_MUSIC = 'back/kalinka_not_russian.mp3'
MOVE_SOUND = 'effects/move'

PIECE_IMG_PATH = 'pieces/'
letters = 'abcdefghijklmnopqrstuvwxyz'
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
PALETTES = {'Cyan': ((204, 216, 216), (165, 189, 191), (88, 138, 135), (65, 102, 100)),
            'Gray': ((227, 231, 230), (211, 220, 215), (182, 197, 190), (145, 158, 152)),
            'Pink': ((242, 224, 222), (240, 206, 195), (237, 169, 148), (199, 141, 123)),
            'Orange': ((237, 224, 205), (233, 209, 169), (226, 174, 98), (189, 146, 81)),
            'Green': ((241, 249, 241), (197, 231, 200), (98, 158, 104), (74, 120, 79))}
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
ACTIVE_ROOT_COLOR = (0, 180, 0, 50)
CHECK_ROOT_COLOR = (255, 0, 0, 80)
LETTERS_COLOR = WHITE
NUMBERS_COLOR = WHITE
ROOT_SUBSCRIPT_COLOR = WHITE
PIECES_DICT = {
    'K': ("King", "w"), 'k': ("King", "b"),
    'Q': ("Queen", "w"), 'q': ("Queen", "b"),
    'R': ("Rook", "w"), 'r': ("Rook", "b"),
    'B': ("Bishop", "w"), 'b': ("Bishop", "b"),
    'N': ("Knight", "w"), 'n': ("Knight", "b"),
    'P': ("Pawn", "w"), 'p': ("Pawn", "b"),
}
HOST = '192.168.1.85'
PORT = 14
