#!/usr/bin/python3
import pygame
from util import Colors
from chessboard import Chessboard
from piece import PieceFactory, Piece

class App:
    def __init__(self):
        self.screen = None
        self.width, self.height = 1500, 800
        self.p = None
        self.board = None
        self.pieceFactory = None

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("pyChess")

        self.board = Chessboard(x=50, y=50)
        self.pieceFactory = PieceFactory()
        self.chessSet = self.pieceFactory.getChessSet()
        self.board.setPieces(self.chessSet)

    def processEvents(self):
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
            elif evt.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                self.board.processEvent(evt)
            elif evt.type == pygame.KEYUP and evt.key == pygame.K_r:
                self.chessSet = self.pieceFactory.getChessSet()
                self.board.setPieces(self.chessSet)
        return True

    def main(self):
        self.init()

        while True:
            if not self.processEvents():
                break

            self.screen.fill(Colors.Black.value)

            self.board.drawBoard(self.screen)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    App().main()