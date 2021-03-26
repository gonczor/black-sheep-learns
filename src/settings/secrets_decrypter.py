import boto3


def get_secret(secret_name: str) -> str:
    region_name = "eu-central-1"
    COMMON_PREFIX = "/BlackSheepLearns/dev/"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    ssm_client = session.client(
        service_name='ssm',
        region_name=region_name
    )
    return ssm_client.get_parameters(
        Names=[COMMON_PREFIX + secret_name], WithDecryption=True
    )['Parameters'][0]


