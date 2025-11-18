from abc import ABC, abstractmethod

class IUserService(ABC):

    @abstractmethod
    async def waittest(self, payload, resource):
        pass

    @abstractmethod
    async def login(self, payload, resource):
        pass

    @abstractmethod
    async def register(self, payload, resource):
        pass

    @abstractmethod
    async def get_user(self, payload, resource):
        pass
