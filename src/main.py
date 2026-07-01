from logger import setup_crash_logger

setup_crash_logger()

from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
