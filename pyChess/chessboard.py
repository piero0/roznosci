#!/usr/bin/python3
import pygame
from util import Colors

class Chessboard:
    def __init__(self, x, y):
        self.position = (x, y)
        self.square_size = 80
        self.board_size = 8 * self.square_size
        self.surface = pygame.Surface((self.board_size ,self.board_size))
        self.pieces = []
        self.dragging = None

    def drawBoard(self, screen):
        color = None
        for i in range(8):                        
            for j in range(8):                        
                color = Colors.Light.value if (i+j)%2==0 else Colors.Dark.value
                pygame.draw.rect(self.surface, color, (i * self.square_size, j * self.square_size, self.square_size, self.square_size))

        self.drawPieces()
        self.drawSpecial()
        screen.blit(self.surface, self.position)

    def setPieces(self, pieces):
        self.pieces = pieces

    def drawPieces(self):
        for p in self.pieces:
            pos = self.squareNameToXY(p.pos)
            p.draw(self.surface, pos)

    def drawSpecial(self):
        #pygame.draw.rect(self.surface, color, (i * self.square_size, j * self.square_size, self.square_size, self.square_size))
        pass

    def squareNameToXY(self, position):
        col, row = position
        col = ord(col) - ord('a')
        row = 8 - int(row)
        return (col * self.square_size, row * self.square_size)

    def XYToSquareName(self, xy):
        cols = 'abcdefgh'
        x,y = xy
        return f'{cols[x]}{8-y}'

    def mousePositionToXY(self, pos):
        x,y = pos
        x -= self.position[0]
        y -= self.position[1]
        col = x//self.square_size
        row = y//self.square_size
        return (col, row)

    def mousePositionToSquareName(self, pos):
        return self.XYToSquareName(self.mousePositionToXY(pos))

    def findPieceOn(self, pos):
        for p in self.pieces:
            if p.pos == pos:
                return p
        return None

    def processEvent(self, event):
        #check if pos in board
        pos = self.mousePositionToSquareName(event.pos)
        print(pos)
        p = self.findPieceOn(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if p is not None:
                self.dragging = p
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging is not None:
            if p is not None and p != self.dragging: #dest square not empty and src pos != dst pos
                self.pieces.remove(p)
            self.dragging.pos = pos
            self.dragging = None