import sys

import pygame
from pygame.locals import *

from app.gui import *

# from .gui import *

NONE = 0
WHITE = 1
BLACK = 2
COLOUR = 0
COORD = 1
TURN = 1
my_colour = NONE
my_map = [
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
    [0] * 15,
]
pygame.init()
surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Omok game")
surface.fill(bg_color)
omok = Omok(surface, my_map=my_map)
menu = Menu(surface)
pygame.display.update()
fps_clock.tick(fps)


def view_map():
    pygame.display.update()
    fps_clock.tick(fps)


def set_colour(colour):
    print("set_colour:", colour)

    global my_colour
    my_colour = colour
    omok.my_turn = my_colour
    if omok.turn == 1:
        menu.draw_menu(my_colour)
    pygame.display.update()
    fps_clock.tick(fps)


def set_stone(x, y, colour):
    print("set_stone:", x, y, colour)
    global my_map
    my_map[x][y] = colour
    try:
        coord = (x * grid_size + 25, y * grid_size + 25)
        print(coord)
        x, y = omok.check_board(coord)
        print(x, y)
    except Exception as e:
        print(e)
    view_map()


def choose_colour():
    print("select_colour")
    menu.draw_color_menu()

    while True:
        try:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    decision = menu.check_color_rect(event.pos)
                    if decision == 1:
                        return BLACK
                    elif decision == 2:
                        return WHITE
                    else:
                        continue
        except Exception as e:
            print(e)
        pygame.display.update()
        fps_clock.tick(fps)


def place_stone():
    print("place_stone")
    x, y = 0, 0
    while True:
        for event in pygame.event.get():
            try:
                if event.type == MOUSEBUTTONUP:
                    xy = omok.check_board1(event.pos)
                    if isinstance(xy, bool):
                        continue
                    else:
                        x = xy[0]
                        y = xy[1]
                        print(x, y)
                        return x, y
            except Exception as e:
                print(e)
        pygame.display.update()
        fps_clock.tick(fps)


def make_decision():
    print("make_decision")
    menu.draw_decision_menu()
    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                decision = menu.check_rect(event.pos)
                if decision == 1:
                    return COLOUR
                elif decision == 2:
                    return COORD
                else:
                    continue
        pygame.display.update()
        fps_clock.tick(fps)

    return COLOUR if input("decision>") == "COLOUR" else COORD


def victory():
    print("victory")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                menu.show_winner_msg(my_colour)
        pygame.display.update()
        fps_clock.tick(fps)


def defeat():
    print("defeat")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            else:
                menu.show_winner_msg(3 - my_colour)
        pygame.display.update()
        fps_clock.tick(fps)
