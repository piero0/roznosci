#!/usr/bin/python3
"""
    Blind Chess 
    A Text Interface to Stockfish (or any other UCI engine)
"""
import subprocess as sp
from threading import Thread
import logging
import sys
import os
import time
from queue import Queue

Config = { "engineCmd": "E:\\stockfish8\\stockfish_8_x64_popcnt.exe"}
#Config = { "engineCmd": "stockfish"}

class EngineRunner:
    engineCmd = Config["engineCmd"]

    def __init__(self):
        self.eng = None
        self.buf = Queue()

    def start(self):
        logging.info("Starting engine")
        try:
            self.eng = sp.Popen([self.engineCmd], bufsize=0, stdout=sp.PIPE, stdin=sp.PIPE, universal_newlines=True)
        except sp.SubprocessError as e:
            logging.error("%s" % e.msg)
            return

        self.setupReaderThread()

    def setupReaderThread(self):
        self.th = Thread(target=self.readerThread)
        self.th.start()

    def read(self, tag=None):
        logging.info("Reading output")
        out = ""
        while True:
            line = self.buf.get()
            out += line
            if tag is None or line.startswith(tag):
                return out

    def readerThread(self):
        while True:
            line = self.eng.stdout.readline()
            if line:
                self.buf.put(line)
            else:
                break

    def send(self, cmd):
        logging.info("Sending cmd: %s", cmd)
        self.eng.stdin.write("%s\n" % cmd)

    def __enter__(self):
        self.start()
        logging.info("Header: %s" % self.read())
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info("Stopping engine")
        self.send("quit")
        #self.readerThread.isAlive()
        #self.eng.poll()

class UCITalker(EngineRunner):
    def __init__(self):
        super().__init__()
        self.moveTime = 1000
        self.moves = []
        self.puzzle = [
            "8/8/3k4/8/3K4/3Q4/8/8 w - - 0 1",
            "3k4/7Q/3K4/8/8/8/8/8 w - - 0 1",
            "3k4/3Q4/3K4/8/8/8/8/8 b - - 0 1",
            "8/3RKP2/8/8/8/8/8/k7 w - - 0 1",
            "r2qkb1r/pp1n1pp1/2pp1n1p/4pb2/2PP4/2N1PN2/PP2BPPP/R1BQ1RK1 w kq - 0 8"
            ]

    def setup(self):
        self.send("uci")
        self.send("setoption name Skill Level value 0")
        self.send("ucinewgame")
        self.send("position fen %s" % self.puzzle[0])
        print("Black: Kd6\nWhite: Kd4, Qd3\n")
        #self.send("position startpos")

    def getBoard(self):
        data = self.getOutput("d", "Checkers").splitlines()
        self.board = data[1:18]
        self.fen = data[19][5:]
        try:
            self.chk = data[21][10:]
        except IndexError:
            print(data)

    def getOutput(self, cmd, stopTag):
        self.send(cmd)
        return self.read(stopTag)

    def getMove(self, cmd):
        out = self.getOutput(cmd, "bestmove").splitlines()
        move = ""
        try:
            move = out[-1].split()[1]
        except IndexError:
            logging.error("getMove error")
            return
        
        logging.info("getMove: %s" % move)

        if move != "(none)":
            return move
        return None

    def checkMove(self, move):
        cmd = "go searchmoves %s" % move
        return self.getMove(cmd)

    def getUserMove(self, move):
        if not self.checkMove(move):
            return
        self.moves.append(move)
        self.send("position fen %s moves %s" % (self.fen, move))
        return move

    def getCpuMove(self):
        move = self.getMove("go movetime %i" % self.moveTime)
        if not move:
            return
        self.moves.append(move)
        self.send("position fen %s moves %s" % (self.fen, move))
        return move

    def long2pgn(self, move):
        """ 
            It isn't a real pgn, only start loc is translatated 
            to piece name.
            TODO: 
            Distinction when two pieces in the same row/col
            castling/checks/captures
        """
        start = move[:2]
        stop = move[2:]

        col = 4*(ord(start[0]) - ord('a')) + 3
        row = 2*(9 - int(start[1])) - 1

        c = self.board[row][col].upper()
        if c == "P":
            c = ""

        return " %s%s " % (c, stop)

    def parseCommand(self, cmd):
        self.getBoard()

        if cmd == "d":
            self.getBoard()
            print("\n".join(self.board))
        elif cmd == "e":
            print(self.getOutput("eval", "Total Eval"))
        elif cmd == "clr":
            os.system("clear" if sys.platform == "linux" else "cls")
        elif cmd == "quit":
            return False
        elif 4 <= len(cmd) <= 5:
            usermove = cmd

            if self.getUserMove(usermove) is None:
                print("Invalid move")
                return True

            self.getBoard()
            
            cpumove = self.getCpuMove()
            if cpumove is None:
                print("Mate")
                self.send("stop")
                return True
            else:
                print("\t%s (%s)" %  (cpumove, self.long2pgn(cpumove)))
        else:
            self.send(cmd)
            print(self.read())

        return True

    def loop(self):
        self.setup()
        self.getBoard()

        running = True
        while running:
            running = self.parseCommand(input("> "))

        print(self.moves)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    with UCITalker() as eng:
        eng.loop()
