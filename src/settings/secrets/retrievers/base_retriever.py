from abc import ABC, abstractmethod


class BaseSecretsRetriever(ABC):
    @abstractmethod
    def retrieve(self, name: str) -> str:
        pass
