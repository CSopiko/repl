import random
import string

import pytest

from app.channel import (
    EmptyAction,
    EmptyCommand,
    IDatabase,
    InMemDatabase,
    Observable,
    PublishVideoAction,
    PublishVideoCommand,
    SubscribeAction,
    SubscriptionCommand,
    check_io_publishing_format,
    check_io_subscription_format,
    extract_io_publishing_format,
    extract_io_subscription_format,
)
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


def random_string(length: int, suffix: str = "") -> str:
    rand_str = (
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
        )
        + suffix
    )
    return rand_str


def test_check_io_subscription_format_default() -> None:
    assert check_io_subscription_format("subscribe <username> to <channel>")


def test_check_io_subscription_format_rand() -> None:
    rand_user_name = random_string(random.randint(5, 10), "_user")
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert check_io_subscription_format(
        "subscribe <{}> to <{}>".format(rand_user_name, rand_channel_name)
    )


def test_check_check_io_publishing_format_default() -> None:
    assert check_io_publishing_format("publish video on <channel>")


def test_check_io_publishing_format_random() -> None:
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert check_io_publishing_format("publish video on <{}>".format(rand_channel_name))


def test_extract_io_subscription_format_default() -> None:
    user_name, channel_name = extract_io_subscription_format(
        "subscribe <username> to <channel>"
    )
    assert user_name == "username" and channel_name == "channel"


def test_extract_io_subscription_format_random() -> None:
    rand_user_name = random_string(random.randint(5, 10), "_user")
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    user_name, channel_name = extract_io_subscription_format(
        "subscribe <{}> to <{}>".format(rand_user_name, rand_channel_name)
    )
    assert user_name == rand_user_name and channel_name == rand_channel_name


def test_extract_io_publishing_format_default() -> None:
    assert extract_io_publishing_format("publish video on <channel>") == "channel"


def test_extract_io_publishing_format_random() -> None:
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert (
        extract_io_publishing_format("publish video on <{}>".format(rand_channel_name))
        == rand_channel_name
    )


@pytest.fixture
def db() -> IDatabase:
    return InMemDatabase()


def test_database_in_mem_singleton() -> None:
    assert InMemDatabase() == InMemDatabase()


def test_database_in_mem_empty(db: IDatabase) -> None:
    assert len(db.db) == 0


def test_database_in_mem_contains_channel_default(db: IDatabase) -> None:
    assert isinstance(db.contains_channel("channel"), Observable)


def test_database_in_mem_contains_channel_rand(db: IDatabase) -> None:
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert isinstance(db.contains_channel(rand_channel_name), Observable)


def test_database_in_mem_add_user_to_channel(db: IDatabase) -> None:
    db.add_user_to_channel(Observable("channel"), "username")


def test_action_empty_type_default(db: IDatabase) -> None:
    assert EmptyAction(db).is_type("")


def test_action_empty_type_rand(db: IDatabase) -> None:
    assert EmptyAction(db).is_type(random_string(random.randint(10, 15)))


def test_action_empty_action_default(db: IDatabase) -> None:
    EmptyAction(db).empty_action("")


def test_action_empty_action_rand(db: IDatabase) -> None:
    EmptyAction(db).empty_action(random_string(random.randint(10, 15)))


def test_action_subscribe_default_true(db: IDatabase) -> None:
    assert SubscribeAction(db).is_type("subscribe <username> to <channel>")


def test_action_subscribe_default_false(db: IDatabase) -> None:
    assert not SubscribeAction(db).is_type("")


def test_action_subscribe_rand_true(db: IDatabase) -> None:
    rand_user_name = random_string(random.randint(5, 10), "_user")
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert SubscribeAction(db).is_type(
        "subscribe <{}> to <{}>".format(rand_user_name, rand_channel_name)
    )


def test_action_subscribe_rand_false(db: IDatabase) -> None:
    assert not SubscribeAction(db).is_type(random_string(random.randint(5, 10)))


def test_action_publish_default_true(db: IDatabase) -> None:
    assert PublishVideoAction(db).is_type("publish video on <channel>")


def test_action_publish_default_false(db: IDatabase) -> None:
    assert not PublishVideoAction(db).is_type("")


def test_action_publish_rand_true(db: IDatabase) -> None:
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    assert PublishVideoAction(db).is_type(
        "publish video on <{}>".format(rand_channel_name)
    )


def test_action_publish_rand_false(db: IDatabase) -> None:
    assert not PublishVideoAction(db).is_type(random_string(random.randint(5, 10)))


def test_command_empty_default(db: IDatabase) -> None:
    EmptyCommand(EmptyAction(db)).execute("")


def test_command_empty_rand(db: IDatabase) -> None:
    EmptyCommand(EmptyAction(db)).execute(random_string(random.randint(5, 10)))


def test_command_subscribe_default(db: IDatabase) -> None:
    SubscriptionCommand(SubscribeAction(db)).execute(
        "subscribe <username> to <channel>"
    )


def test_command_subscribe_rand(db: IDatabase) -> None:
    rand_user_name = random_string(random.randint(5, 10), "_user")
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    SubscriptionCommand(SubscribeAction(db)).execute(
        "subscribe <{}> to <{}>".format(rand_user_name, rand_channel_name)
    )


def test_command_publish_default(db: IDatabase) -> None:
    PublishVideoCommand(PublishVideoAction(db)).execute("publish video on <channel>")


def test_command_publish_rand(db: IDatabase) -> None:
    rand_channel_name = random_string(random.randint(5, 10), "_channel")
    PublishVideoCommand(PublishVideoAction(db)).execute(
        "publish video on <{}>".format(rand_channel_name)
    )
