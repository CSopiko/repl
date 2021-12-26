from dataclasses import dataclass
from typing import Protocol


@dataclass
class User:
    username: str

    def __str__(self) -> str:
        return self.username


class ChannelObserver(Protocol):
    user: User

    def on_video_published(self) -> None:
        pass


@dataclass
class Printer:
    user: User

    def on_video_published(self) -> None:
        print("\t" + self.user.username)

    def __hash__(self) -> int:
        return (str(self.user) + "_" + "Printer").__hash__()


@dataclass
class EmailSender:
    user: User

    def on_video_published(self) -> None:
        pass
