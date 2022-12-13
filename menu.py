import pygame as pg
from konfig import *


class Menu:
    """Main menu class"""
    def __init__(self, screen: pg.Surface):
        pg.display.set_caption('Main menu')
        self.__screen = screen
        self.__prepare_screen()

    def __prepare_screen(self):
        self.__screen.fill(BLACK)
