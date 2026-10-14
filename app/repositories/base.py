from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def create(self, data) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, **filters) -> list[T]:
        raise NotImplementedError
