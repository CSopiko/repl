from app.channel import InMemDatabase
from app.repl import repl

if __name__ == "__main__":
    repl(InMemDatabase())
