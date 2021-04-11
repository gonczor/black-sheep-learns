from aws.secrets_retriever import SSMSecretsRetriever
from .base_retriever import BaseSecretsRetriever
from .environment_variables_retriever import EnvRetriever


class RetrieverFactory:
    def __init__(self, is_prod: bool):
        self._is_prod = is_prod

    def create_retriever(self) -> BaseSecretsRetriever:
        if self._is_prod:
            return SSMSecretsRetriever()
        else:
            return EnvRetriever()
