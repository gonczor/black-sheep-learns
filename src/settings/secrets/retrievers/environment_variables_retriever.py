import environ

from settings.secrets.retrievers.base_retriever import BaseSecretsRetriever


class EnvRetriever(BaseSecretsRetriever):
    def __init__(self):
        self.__env = environ.Env()

    def retrieve(self, name: str) -> str:
        return self.__env(name)
