from app.channel import Database
from app.repl import repl

if __name__ == "__main__":
    repl(Database())
