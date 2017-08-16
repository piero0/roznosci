#!/usr/bin/python3
"""
    Blind Chess 
    A Text Interface to Stockfish (or any other UCI engine)
"""
import subprocess as sp
from threading import Thread
import logging
import sys
import time

Config = { "engineCmd": "E:\\stockfish8\\stockfish_8_x64_popcnt.exe"}

class EngineRunner:
    engineCmd = Config["engineCmd"]

    def __init__(self):
        self.eng = None
        self.buf = []

    def start(self):
        logging.info("Starting engine")
        try:
            self.eng = sp.Popen([self.engineCmd], bufsize=0, stdout=sp.PIPE, stdin=sp.PIPE, universal_newlines=True)
        except sp.SubprocessError as e:
            logging.error("%s" % e.msg)
            return

        if sys.platform != "linux":
            self.setupReaderWin()
        else:
            self.setupReaderLinux()

    def setupReaderLinux(self):
        self.selector = select.poll()
        self.selector.register(self.eng.stdout,select.POLLIN)

    def readLinux(self):
        # On Windows readWin works in thread
        # so we can immediately read self.buf
        # What to do here?
        if self.selector.poll(1):
            self.buf.append(self.eng.stdout.readline())

    def setupReaderWin(self):
        self.readerThread = Thread(target=self.readWin)
        self.readerThread.start()

    def read(self):
        logging.info("Reading output")
        while len(self.buf) == 0:
            continue
        out = "".join(self.buf)
        self.buf.clear()
        return out

    def readWin(self):
        while True:
            line = self.eng.stdout.readline()
            if line:
                self.buf.append(line)
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

    def setOptions(self):
        pass

    def getBoard(self):
        self.send("d")
        data = self.read().splitlines()
        asciiBoard = data[1:18]
        fen = data[19][5:]
        checks = data[21][11:]

        return asciiBoard, fen, checks

    def parseCommand(self, cmd):
        if cmd.startswith("mv"):
            brd,fen,chk = self.getBoard()
            self.send("position fen %s moves %s\n d" % (fen, cmd[3:]))
            brd,fen,chk = self.getBoard()
            print("\n".join(brd))
            print(fen)
        elif cmd.startswith("go"):
            self.send("go")
            time.sleep(5)
            self.send("stop")
            print(self.read())

    def loop(self):
        self.setOptions()
        self.getBoard()

        cmd = "gogo"

        while cmd != "quit":
            cmd = input("> ")
            self.parseCommand(cmd)

class MainLoop:
    def play(self):
        pass

class ArgParser:
    def parse(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    with UCITalker() as eng:
        eng.loop()
