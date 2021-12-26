from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol, Set, Tuple, Union

from app.user import ChannelObserver, Printer, User


@dataclass
class Observable:
    name: str
    observers: Set[ChannelObserver] = field(default_factory=set)

    def attach(self, observer: ChannelObserver) -> None:
        self.observers.add(observer)

    def detach(self, observer: ChannelObserver) -> None:
        self.observers.remove(observer)

    def notify_video_published(self) -> None:
        for o in self.observers:
            o.on_video_published()


@dataclass
class InMemDatabase:
    db: Dict[str, Tuple[Observable, list[User]]]

    def __init__(self) -> None:
        self.db = {}

    def contains_channel(self, channel: str) -> Union[Observable, None]:
        if channel in self.db:
            return self.db[channel][0]
        else:
            return None

    def add_user_to_channel(
        self, channel: Union[Observable, Any, None], user: str
    ) -> None:
        if not isinstance(channel, Observable):
            return
        if self.contains_channel(channel.name):
            self.db[channel.name][1].append(user)
        else:
            self.db[channel.name] = (channel, [user])


class CommandType(Protocol):
    type_format: Callable[[str], bool]
    extraction_format: Callable[[str], Any]
    db: InMemDatabase

    def is_type(self, command: str) -> bool:
        pass

    def execute(self, command: str) -> None:
        pass


class Command(Protocol):
    def read_command(self) -> None:
        pass

    def evaluate_command(self, command: str, db: InMemDatabase) -> CommandType:
        pass

    def print_command(self, command_type: CommandType, command_str: str) -> None:
        pass


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


def extract_io_subscription_format(command: str) -> Tuple[str, str]:
    user_name = command[command.find("<") + 1 : command.find(">")]
    channel_name = command[command.rfind("<") + 1 : command.rfind(">")]
    return user_name, channel_name


def extract_io_publishing_format(command: str) -> str:
    channel_name = command[command.find("<") + 1 : command.find(">")]
    return channel_name


@dataclass
class SubscriptionCommand:
    db: InMemDatabase
    type_format: Callable[[str], bool] = check_io_subscription_format
    extraction_format: Callable[[str], Tuple[str, str]] = extract_io_subscription_format

    def execute(self, command: str) -> bool:
        return self._subscribe(command)

    def is_type(self, command: str) -> bool:
        return self.type_format(command)

    def _subscribe(self, s: str) -> bool:
        user_name, channel_name = self.extraction_format(s)
        channel = (
            self.db.contains_channel(channel_name)
            if self.db.contains_channel(channel_name) is not None
            else Observable(channel_name)
        )
        if channel is None:
            return False
        channel.attach(Printer(User(user_name)))
        self.db.add_user_to_channel(channel, user_name)
        print(user_name + " subscribed to " + channel_name)
        return True


@dataclass
class VideoPublisherCommand:
    db: InMemDatabase
    type_format: Callable[[str], bool] = check_io_publishing_format
    extraction_format: Callable[[str], str] = extract_io_publishing_format

    def execute(self, command: str) -> bool:
        return self._publish_video(command)

    def is_type(self, command: str) -> bool:
        return self.type_format(command)

    def _publish_video(self, s: str) -> bool:
        channel_name = self.extraction_format(s)
        channel = self.db.contains_channel(channel_name)

        if channel is None:
            return False

        print("Notifying subscribers of " + channel_name + ":")
        channel.notify_video_published()
        return True


COMMAND_TYPES: List[CommandType] = [SubscriptionCommand, VideoPublisherCommand]


class IOCommand:
    def read_command(self) -> str:
        return input()

    def evaluate_command(
        self, command: str, db: InMemDatabase
    ) -> Union[SubscriptionCommand, VideoPublisherCommand, None]:
        for c in COMMAND_TYPES:
            if c(db).is_type(command):
                return c(db)
        return None

    def print_command(self, command_type: CommandType, command_str: str) -> None:
        command_type.execute(command_str)
