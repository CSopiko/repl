from app.channel import InMemDatabase, PKLDatabase
from app.repl import repl

if __name__ == "__main__":
    repl(PKLDatabase())
