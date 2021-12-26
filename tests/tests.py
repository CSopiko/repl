import random
import string

from app.channel import Observable
from app.user import Printer, User


def test_user_name_empty() -> None:
    assert User("").username == ""


def test_user_name_custom() -> None:
    assert User("CSopiko").username == "CSopiko"


def test_user_name_random() -> None:
    rand_name_len = random.randint(5, 10)
    rand_name = "".join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(rand_name_len)
    )
    assert User(rand_name).username == rand_name


def test_printer_user_name_empty() -> None:
    p = Printer(User(""))
    assert p.user.username == ""


def test_printer_user_name_custom() -> None:
    p = Printer(User("CSopiko"))
    assert p.user.username == "CSopiko"


def test_printer_user_name_random() -> None:
    rand_name_len = random.randint(5, 10)
    rand_name = "".join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(rand_name_len)
    )
    p = Printer(User(rand_name))
    assert p.user.username == rand_name


def test_observable_empty() -> None:
    o = Observable("")
    assert len(o.observers) == 0


def test_observable_one_observer() -> None:
    o = Observable("")
    o.attach(Printer(User("Basic")))
    assert len(o.observers) == 1


def test_observable_two_observers() -> None:
    o = Observable("")
    o.attach(Printer(User("Basic1")))
    o.attach(Printer(User("Basic2")))
    assert len(o.observers) == 2


def test_observable_rand_num_observers() -> None:
    o = Observable("")
    rand_num = random.randint(1, 10)
    for i in range(rand_num):
        o.attach(Printer(User("Basic" + str(i))))
    assert len(o.observers) == rand_num
