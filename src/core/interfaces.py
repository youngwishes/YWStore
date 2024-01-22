from __future__ import annotations
from abc import ABC, abstractmethod


class IRepository(ABC):
    model = None

    @abstractmethod
    async def create(self, in_model):
        """Создать объект"""

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Получить все объекты"""

    @abstractmethod
    async def update(self, pk, data, partial):
        """Обновить объект"""

    @abstractmethod
    async def delete(self, *args, **kwargs):
        """Удалить объекты"""


class IService(ABC):
    @abstractmethod
    async def create(self, in_model):
        """Создать объект"""

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Получить все объекты"""

    @abstractmethod
    async def update(self, pk, data, partial):
        """Обновить объект"""

    @abstractmethod
    async def delete(self, *args, **kwargs):
        """Удалить объекты"""
