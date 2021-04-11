import environ

from settings.secrets.retrievers.base_retriever import BaseSecretsRetriever


env = environ.Env()


class EnvRetriever(BaseSecretsRetriever):
    def retrieve(self, name: str) -> str:
        return env(name)
