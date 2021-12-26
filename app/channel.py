from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol, Set, Tuple, Type, Union

from app.user import ChannelObserver, Printer, User


# Observer Pattern
@dataclass
class Observable:
    name: str
    observers: Set[ChannelObserver] = field(default_factory=set)

    def attach(self, observer: ChannelObserver) -> None:
        self.observers.add(observer)

    def detach(self, observer: ChannelObserver) -> None:
        self.observers.remove(observer)

    def notify_video_published(self) -> None:
        print("Notifying subscribers of " + self.name + ":")
        for o in self.observers:
            o.on_video_published()


# For Singleton pattern
class DatabaseSingletonMeta(type):
    _instances: Dict["DatabaseSingletonMeta", "IDatabase"] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> "IDatabase":
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# Repository Pattern
class IDatabase(Protocol):
    __metaclass__: Type[DatabaseSingletonMeta] = DatabaseSingletonMeta

    def contains_channel(self, channel: str) -> Observable:
        pass

    def add_user_to_channel(self, channel: Observable, user: str) -> None:
        pass


@dataclass
class InMemDatabase:
    __metaclass__ = DatabaseSingletonMeta
    db: Dict[str, Tuple[Observable, list[User]]]

    def __init__(self) -> None:
        self.db = {}

    def contains_channel(self, channel: str) -> Observable:
        if channel not in self.db:
            self.db[channel] = (Observable(channel), [])
        return self.db[channel][0]

    def add_user_to_channel(self, channel: Observable, user: str) -> None:
        if not isinstance(channel, Observable):
            return
        if self.contains_channel(channel.name):
            self.db[channel.name][1].append(User(user))
        else:
            self.db[channel.name] = (channel, [User(user)])


class ActionType:
    @abstractmethod
    def is_type(self, command: str) -> bool:
        pass


# Command Pattern
class Command:
    @abstractmethod
    def execute(self, command: str) -> None:
        pass


# Strategy pattern
# Strategies for input format
def check_io_subscription_format(command: str) -> bool:
    # subscribe <username> to <channel>
    return (
        command.startswith("subscribe")
        and "> to <" in command
        and command.count("<") == 2
        and command.count(">") == 2
    )


def check_io_publishing_format(command: str) -> bool:
    # publish video on <Continuous Delivery>
    return (
        command.startswith("publish video on")
        and command.count("<") == 1
        and command.count(">") == 1
    )


# Strategies for extraction format
def extract_io_subscription_format(command: str) -> Tuple[str, str]:
    user_name = command[command.find("<") + 1 : command.find(">")]
    channel_name = command[command.rfind("<") + 1 : command.rfind(">")]
    return user_name, channel_name


def extract_io_publishing_format(command: str) -> str:
    channel_name = command[command.find("<") + 1 : command.find(">")]
    return channel_name


@dataclass
class PublishVideoAction(ActionType):
    db: IDatabase
    type_format: Callable[[str], bool] = check_io_publishing_format
    extraction_format: Callable[[str], str] = extract_io_publishing_format

    def is_type(self, command: str) -> bool:
        return self.type_format(command)

    def publish_video(self, s: str) -> None:
        channel_name = self.extraction_format(s)
        channel = self.db.contains_channel(channel_name)
        channel.notify_video_published()


@dataclass
class SubscribeAction(ActionType):
    db: IDatabase
    type_format: Callable[[str], bool] = check_io_subscription_format
    extraction_format: Callable[[str], Tuple[str, str]] = extract_io_subscription_format

    def is_type(self, command: str) -> bool:
        return self.type_format(command)

    def subscribe(self, s: str) -> None:
        user_name, channel_name = self.extraction_format(s)
        channel = self.db.contains_channel(channel_name)
        channel.attach(Printer(User(user_name)))
        self.db.add_user_to_channel(channel, user_name)
        print(user_name + " subscribed to " + channel_name)


class IInputType(ABC):
    @abstractmethod
    def read_cmd(self) -> str:
        pass

    @abstractmethod
    def parse_cmd(self, cmd: str, db: IDatabase) -> Union[Command, None]:
        pass

    @abstractmethod
    def run(self, command: Command, cmd: str) -> None:
        pass


@dataclass
class SubscriptionCommand(Command):
    def __init__(self, receiver: SubscribeAction):
        self.receiver = receiver

    def execute(self, command: str) -> None:
        return self.receiver.subscribe(command)


@dataclass
class PublishVideoCommand(Command):
    def __init__(self, receiver: PublishVideoAction):
        self.receiver = receiver

    def execute(self, command: str) -> None:
        return self.receiver.publish_video(command)


ACTION_TYPES: List[Union[Type[SubscribeAction], Type[PublishVideoAction]]] = [
    SubscribeAction,
    PublishVideoAction,
]

COMMAND_TYPES: List[Union[Type[SubscriptionCommand], Type[PublishVideoCommand]]] = [
    SubscriptionCommand,
    PublishVideoCommand,
]


class CLI(IInputType):
    def read_cmd(self) -> str:
        return input(">>> ")

    def parse_cmd(self, cmd: str, db: IDatabase) -> Union[Command, None]:
        if SubscribeAction(db).is_type(cmd):
            return SubscriptionCommand(SubscribeAction(db))
        if PublishVideoAction(db).is_type(cmd):
            return PublishVideoCommand(PublishVideoAction(db))
        return None

    def run(self, command: Command, cmd: str) -> None:
        command.execute(cmd)
