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
import json
import re

class EngineRunner:
    def __init__(self, config):
        self.eng = None
        self.buf = Queue()
        self.config = config
        self.engineCmd = self.config["engineCmd"]

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
    def __init__(self, config):
        super().__init__(config)
        self.moveTime = 1000
        self.moves = []

    def setup(self):
        self.send("uci")
        self.send("setoption name Skill Level value %i" % self.config["Skill Level"])
        self.send("ucinewgame")
        #self.send("position fen %s" % self.puzzle[0])
        #print("Black: Kd6\nWhite: Kd4, Qd3\n")
        #self.send("position startpos")

    def getBoard(self):
        data = self.getOutput(cmd="d", stopTag="Checkers").splitlines()
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
        out = self.getOutput(cmd, stopTag="bestmove").splitlines()
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

class GameLoop:
    def __init__(self):
        self.curgame = False
        self.config = None
        self.puzzle = None
        self.configFile = "config.json"
        self.puzzleFile = "puzzle.json"

    def loadConfigs(self):
        try:
            with open(self.configFile) as f:
                self.config = json.load(f)
        except FileNotFoundError as e:
            logging.error("Missing file: %s" % e)
            return False
    
        try:
            with open(self.puzzleFile) as f:
                self.puzzle = json.load(f)
        except FileNotFoundError as e:
            logging.error("Missing file: %s" % e)
            return False

        return True

    def parseCommand(self, cmd, uci):
        uci.getBoard()

        if cmd == "d":
            uci.getBoard()
            print("\n".join(uci.board))
        elif cmd == "e":
            print(uci.getOutput("eval", "Total Eval"))
        elif cmd == "clr":
            os.system("clear" if sys.platform == "linux" else "cls")
        elif cmd == "quit":
            return False
        elif cmd.startswith("load"):
            print("Not implemented yet")
        elif cmd.startswith("save"):
            print("Not implemented yet")
        elif cmd.startswith("new"):
            color = "w"
            if len(cmd) > 3:
                color = cmd.split()[1]
            uci.send("ucinewgame\nposition startpos")
            if color.lower().startswith("b"):
                uci.getBoard()
                cpumove = uci.getCpuMove()
                print("\t%s (%s)" %  (cpumove, uci.long2pgn(cpumove)))
            self.curgame = True
        elif 4 <= len(cmd) <= 5 and re.fullmatch(r"[a-h]\d[a-h]\d\w?", cmd) is not None:
            if not self.curgame:
                print("Use new or load first")
                return True

            usermove = cmd

            if uci.getUserMove(usermove) is None:
                print("Invalid move")
                return True

            uci.getBoard()
            
            cpumove = uci.getCpuMove()
            if cpumove is None:
                print("Mate")
                uci.send("stop")
                return True
            else:
                print("\t%s (%s)" %  (cpumove, uci.long2pgn(cpumove)))
        else:
            uci.send(cmd)
            print(uci.read())

        return True

    def parseCmds(self):
        if not self.loadConfigs():
            logging.error("Could not load config files")
            return

        with UCITalker(self.config) as uci:
            uci.setup()
            uci.getBoard()

            running = True
            while running:
                running = self.parseCommand(input("> "), uci)

            print(uci.moves)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    GameLoop().parseCmds()
