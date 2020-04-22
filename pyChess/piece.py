#!/usr/bin/python3
import pygame
from enum import Enum

class PieceType(Enum):
    King = 1
    Queen = 2
    Rook = 3
    Bishop = 4
    Knight = 5
    Pawn = 6

class PieceColor(Enum):
    White = 1
    Black = 2

class ImageLoader:
    def __init__(self):
        self.typeMap = {
            'K': PieceType.King,
            'Q': PieceType.Queen,
            'B': PieceType.Bishop,
            'N': PieceType.Knight,
            'R': PieceType.Rook,
            'P': PieceType.Pawn,
        }
        self.colorMap = {
            'w': PieceColor.White,
            'b': PieceColor.Black,
        }
        self.imageMap = { t: { c: None for c in PieceColor } for t in self.typeMap.values() }

    def loadImages(self):
        for c in self.colorMap:
            for t in self.typeMap:
                img = pygame.image.load(f'img/{c}{t}.png')
                self.imageMap[self.typeMap[t]][self.colorMap[c]] = img

    def getImage(self, type, color):
        return self.imageMap[type][color]

class Piece:
    def __init__(self, type, color, position, image):
        self.pos = position
        self.type = type
        self.color = color
        self.image = image

    def draw(self, surface, pos):
        surface.blit(self.image, pos)

class PieceFactory:
    def __init__(self):
        self.imageLoader = ImageLoader()
        self.imageLoader.loadImages()

    def getPiece(self, type, color, position=''):
        return Piece(type, color, position, image=self.imageLoader.getImage(type, color))

    def getChessSet(self):
        chessSet = []
        cols = 'abcdefgh'
        pieces = [
            PieceType.Rook, 
            PieceType.Knight, 
            PieceType.Bishop, 
            PieceType.Queen, 
            PieceType.King, 
            PieceType.Bishop, 
            PieceType.Knight, 
            PieceType.Rook, 
        ]
        for c in PieceColor:
            row = '2' if c == PieceColor.White else '7'
            for p in range(8):
                chessSet.append(self.getPiece(PieceType.Pawn, c, position=f'{cols[p]}{row}'))
            
            row = '1' if c == PieceColor.White else '8'
            i = 0
            for p in pieces:
                chessSet.append(self.getPiece(p, c, position=f'{cols[i]}{row}'))
                i += 1

        return chessSet
