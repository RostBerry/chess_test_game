from chess_game_module import *


clock = pg.time.Clock()
screen = pg.display.set_mode(WINDOW_SIZE)
screen.fill(BACKGROUND)


chess = Chessboard(screen)


run = True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN:
            chess.mouse_btn_down(event.button, event.pos)
        if event.type == pg.MOUSEBUTTONUP:
            chess.mouse_btn_up(event.button, event.pos)
        if event.type == pg.MOUSEMOTION:
            chess.drag(event.pos)
        if event.type == pg.KEYDOWN:
            chess.keyboard_btn_down(event)
        if event.type == pg.KEYUP:
            chess.keyboard_btn_up(event)
    clock.tick(FPS)
pg.quit()
