import pygame

from chess_game_module import *


pg.init()

clock = pg.time.Clock()
screen = pg.display.set_mode(WINDOW_SIZE)

header_img = Image.open(IMG_PATH + PIECE_IMG_PATH + 'w_queen.png').resize((32, 32))
pg.display.set_icon(pg.image.fromstring(header_img.tobytes(),header_img.size, header_img.mode))

pg.mixer.music.load(MUSIC_PATH + BACKGROUND_MUSIC)
pg.mixer.music.set_volume(0.3)
pg.mixer.music.play(-1)

chess = None
options = None
menu = Menu(screen)


run = True
try:
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if menu is not None:
                    menu.mouse_btn_down(event.button, event.pos)
                elif options is not None:
                    options.mouse_btn_down(event.button, event.pos)
                elif chess is not None:
                    chess.mouse_btn_down(event.button, event.pos)
            if event.type == pg.MOUSEBUTTONUP:
                if menu is not None:
                    pass
                elif options is not None:
                    pass
                elif chess is not None:
                    chess.mouse_btn_up(event.button, event.pos)
            if event.type == pg.MOUSEMOTION:
                if menu is not None:
                    menu.mouse_motion(event.pos)
                elif options is not None:
                    pass
                elif chess is not None:
                    chess.drag(event.pos)
            if event.type == pg.KEYDOWN:
                if menu is not None:
                    pass
                elif options is not None:
                    pass
                elif chess is not None:
                    chess.keyboard_btn_down(event)
            if event.type == pg.KEYUP:
                if menu is not None:
                    pass
                elif options is not None:
                    pass
                elif chess is not None:
                    chess.keyboard_btn_up(event)

            if menu is not None:
                if menu.is_game_started:
                    chess = Chessboard(screen)
                    menu = None
                elif menu.is_options_started:
                    options = Options(screen)
                    menu = None
                elif menu.is_quit:
                    run = False
        clock.tick(FPS)
except KeyboardInterrupt:
    pass
pg.quit()
