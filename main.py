from chess_game_module import *

# pygame, Stockfish and screen init trash is in pieces.py for some reason IDK
clock = pg.time.Clock()

with open('saved_info.json', 'r') as info:
    Common.PALETTE = json.load(info)['color scheme']
renew_colors()

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
                    options.mouse_motion(event.pos)
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
            elif options is not None:
                if options.back:
                    menu = Menu(screen)
                    options = None
            elif chess is not None:
                if chess.back:
                    menu = Menu(screen)
                    chess = None
        clock.tick(FPS)
except KeyboardInterrupt:
    pass
pg.quit()
