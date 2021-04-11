import boto3

from settings.secrets.retrievers.base_retriever import BaseSecretsRetriever


class SSMSecretsRetriever(BaseSecretsRetriever):
    def __init__(self):
        region_name = "eu-central-1"
        self._common_prefix = "/BlackSheepLearns/dev/"
        # Create a Secrets Manager client
        session = boto3.session.Session()
        self._ssm_client = session.client(service_name="ssm", region_name=region_name)

    def retrieve(self, name: str) -> str:
        return self._ssm_client.get_parameter(Name=self._common_prefix + name, WithDecryption=True)[
            "Parameter"
        ]["Value"]
