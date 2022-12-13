from chess_game_module import *


pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_icon(pg.transform.scale(pg.image.load('assets/images/pieces/w_queen.png').convert_alpha(),
                                       (32, 32)))

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
                    menu.is_game_started = True
                elif options is not None:
                    pass
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
                    pass
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
        clock.tick(FPS)
except KeyboardInterrupt:
    pass
pg.quit()
