import socket
import sys

import pygame
from pygame.locals import *

from rule import *

bg_color = (128, 128, 128)
black = (0, 0, 0)
blue = (0, 50, 255)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)

window_width = 800
window_height = 500
board_width = 500
grid_size = 30

fps = 60
fps_clock = pygame.time.Clock()


def main():
    pygame.init()
    surface = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Omok game")
    surface.fill(bg_color)

    omok = Omok(surface)
    menu = Menu(surface)
    while True:
        run_game(surface, omok, menu)
        menu.is_continue(omok)


def run_game(surface, omok, menu):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                menu.terminate()
            elif event.type == MOUSEBUTTONUP:
                game_type = menu.check_rect(event.pos)
                if game_type == 1:  # 싱글플레이
                    run_single_game(surface, omok, menu)
                elif game_type == 2:  # 멀티플레이
                    run_multi_game(surface, omok, menu)
                elif game_type == 3:  # 멀티플레이 (AI)
                    pass
                else:
                    continue

        pygame.display.update()
        fps_clock.tick(fps)


def run_single_game(surface, omok, menu):
    omok.init_game()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                menu.terminate()
            elif event.type == MOUSEBUTTONUP:
                if omok.check_board(event.pos):
                    if omok.is_gameover:
                        return True

        pygame.display.update()
        fps_clock.tick(fps)


def run_multi_game(surface, omok, menu):
    omok.init_game()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = map(str, input().split())
    server_address = (ip, int(port))
    print(server_address)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                menu.terminate()
            elif event.type == MOUSEBUTTONUP:
                if omok.check_board(event.pos):
                    if omok.is_gameover:
                        return True

        pygame.display.update()
        fps_clock.tick(fps)


class Omok(object):
    def __init__(self, surface):
        self.board = [[0 for i in range(board_size)] for j in range(board_size)]
        self.menu = Menu(surface)
        self.rule = Rule(self.board)
        self.surface = surface
        self.pixel_coords = []
        self.set_coords()
        self.set_image_font()
        self.is_show = True

    def init_game(self):
        self.turn = black_stone
        self.draw_board()
        self.menu.show_msg(empty)
        self.init_board()
        self.coords = []
        self.redos = []
        self.id = 1
        self.is_gameover = False

    def set_image_font(self):
        black_img = pygame.image.load("image/black.png")
        white_img = pygame.image.load("image/white.png")
        self.board_img = pygame.image.load("image/board.png")
        self.font = pygame.font.Font("freesansbold.ttf", 14)
        self.black_img = pygame.transform.scale(black_img, (grid_size, grid_size))
        self.white_img = pygame.transform.scale(white_img, (grid_size, grid_size))

    def init_board(self):
        for y in range(board_size):
            for x in range(board_size):
                self.board[y][x] = 0

    def draw_board(self):
        self.surface.blit(self.board_img, (0, 0))

    def draw_image(self, img_index, x, y):
        img = [self.black_img, self.white_img]
        self.surface.blit(img[img_index], (x, y))

    def draw_stone(self, coord, stone, increase=1):
        x, y = self.get_point(coord)
        self.board[y][x] = stone

        for i in range(len(self.coords)):
            x, y = self.coords[i]
            self.draw_image(i % 2, x, y)

        self.id += increase
        self.turn = 3 - self.turn

    def set_coords(self):
        for y in range(board_size):
            for x in range(board_size):
                self.pixel_coords.append((x * grid_size + 25, y * grid_size + 25))

    def get_coord(self, pos):
        for coord in self.pixel_coords:
            x, y = coord
            rect = pygame.Rect(x, y, grid_size, grid_size)
            if rect.collidepoint(pos):
                return coord
        return None

    def get_point(self, coord):
        x, y = coord
        x = (x - 25) // grid_size
        y = (y - 25) // grid_size
        return x, y

    def check_board(self, pos):
        coord = self.get_coord(pos)
        if not coord:
            return False
        x, y = self.get_point(coord)
        if self.board[y][x] != empty:
            return True

        self.coords.append(coord)
        self.draw_stone(coord, self.turn)
        if self.check_gameover(coord, 3 - self.turn):
            self.is_gameover = True

        return True

    def check_gameover(self, coord, stone):
        x, y = self.get_point(coord)
        if self.id > board_size * board_size:
            self.show_winner_msg(stone)
            return True
        elif 5 <= self.rule.is_gameover(x, y, stone):
            self.show_winner_msg(stone)
            return True
        return False

    def show_winner_msg(self, stone):
        for i in range(3):
            self.menu.show_msg(stone)
            pygame.display.update()
            pygame.time.delay(200)
            self.menu.show_msg(empty)
            pygame.display.update()
            pygame.time.delay(200)
        self.menu.show_msg(stone)


class Menu(object):
    def __init__(self, surface):
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.surface = surface
        self.draw_menu()

    def draw_menu(self):
        top, left = window_height - 30, window_width - 250
        self.new_rect = self.make_text(
            self.font, "New Game", blue, None, top - 90, left
        )
        self.multi_rect = self.make_text(
            self.font, "multi Game", blue, None, top - 60, left
        )
        self.multiAI_rect = self.make_text(
            self.font, "multi Game ai mode", blue, None, top - 30, left
        )
        self.quit_rect = self.make_text(self.font, "Quit Game", blue, None, top, left)

    def show_msg(self, msg_id):
        msg = {
            empty: "                                    ",
            black_stone: "Black win!!!",
            white_stone: "White win!!!",
            tie: "Tie",
        }
        center_x = window_width - (window_width - board_width) // 2
        self.make_text(self.font, msg[msg_id], black, bg_color, 30, center_x, 1)

    def make_text(self, font, text, color, bgcolor, top, left, position=0):
        surf = font.render(text, False, color, bgcolor)
        rect = surf.get_rect()
        if position:
            rect.center = (left, top)
        else:
            rect.topleft = (left, top)
        self.surface.blit(surf, rect)
        return rect

    def check_rect(self, pos):
        if self.new_rect.collidepoint(pos):
            return 1
        elif self.multi_rect.collidepoint(pos):
            return 2
        elif self.multiAI_rect.collidepoint(pos):
            return 3
        elif self.quit_rect.collidepoint(pos):
            self.terminate()
        return False

    def terminate(self):
        pygame.quit()
        sys.exit()

    def is_continue(self, omok):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.terminate()
                elif event.type == MOUSEBUTTONUP:
                    if self.check_rect(event.pos, omok):
                        return
            pygame.display.update()
            fps_clock.tick(fps)


if __name__ == "__main__":
    main()
