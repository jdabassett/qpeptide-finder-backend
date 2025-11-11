import json
import logging
import os

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available. AWS Secrets Manager integration disabled.")


def get_env_file() -> str:
    """Determine which .env file to load based on environment."""
    # Check if running in CI (GitHub Actions sets CI=true)
    if os.getenv("CI") == "true":
        return ".env.testing"
    # Default to .env for local development
    return ".env"


def load_aws_secrets(
    secret_name: str, region_name: str | None = None
) -> dict[str, str]:
    """
    Load secrets from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        region_name: AWS region (defaults to AWS_REGION env var or us-east-1)

    Returns:
        Dictionary of secret key-value pairs
    """
    if not BOTO3_AVAILABLE:
        logger.warning("boto3 not available, skipping AWS Secrets Manager")
        return {}

    try:
        region = region_name or os.getenv("AWS_REGION", "us-east-1")

        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region)

        # Retrieve secret
        response = client.get_secret_value(SecretId=secret_name)

        # Parse secret (can be JSON string or plain text)
        secret_string = response["SecretString"]
        try:
            # Try parsing as JSON
            secrets = json.loads(secret_string)
            if isinstance(secrets, dict):
                return secrets
            else:
                logger.warning(f"Secret {secret_name} is not a JSON object")
                return {}
        except json.JSONDecodeError:
            # If not JSON, treat as plain text (one secret value)
            logger.warning(f"Secret {secret_name} is not JSON, treating as plain text")
            return {}

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "ResourceNotFoundException":
            logger.warning(f"Secret {secret_name} not found in AWS Secrets Manager")
        else:
            logger.error(f"Error retrieving secret {secret_name}: {e}")
        return {}
    except BotoCoreError as e:
        logger.error(f"Error connecting to AWS Secrets Manager: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading AWS secrets: {e}")
        return {}


def should_use_aws_secrets() -> bool:
    """Determine if we should load from AWS Secrets Manager."""
    # Use AWS Secrets Manager if:
    # 1. ENVIRONMENT is set to production, OR
    # 2. AWS_REGION is set (indicates we're in AWS), OR
    # 3. AWS_SECRET_NAME is explicitly set
    env = os.getenv("ENVIRONMENT", "").lower()
    has_aws_region = bool(os.getenv("AWS_REGION"))
    has_secret_name = bool(os.getenv("AWS_SECRET_NAME"))

    return env == "production" or has_aws_region or has_secret_name


class Settings(BaseSettings):
    # AWS Secrets Manager configuration
    AWS_SECRET_NAME: str = "qpeptide-cutter-backend/secrets"
    AWS_REGION: str | None = None

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=True,
        extra="ignore",
    )

    # Database - MySQL
    DATABASE_URL: str = ""
    DATABASE_ECHO: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] | str = ["http://localhost:3000"]

    # Environment
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @model_validator(mode="after")
    def load_aws_secrets_if_needed(self) -> "Settings":
        """Load secrets from AWS Secrets Manager if in production/AWS environment."""
        if should_use_aws_secrets():
            secret_name = os.getenv("AWS_SECRET_NAME", self.AWS_SECRET_NAME)
            region = self.AWS_REGION or os.getenv("AWS_REGION")

            logger.info(f"Loading secrets from AWS Secrets Manager: {secret_name}")
            secrets = load_aws_secrets(secret_name, region)

            # Update settings with secrets from AWS (AWS secrets override .env values)
            for key, value in secrets.items():
                if hasattr(self, key):
                    # Override existing values with AWS secrets
                    setattr(self, key, value)
                else:
                    # Set new attributes from secrets
                    setattr(self, key, value)

        # Validate required fields after loading all sources
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is required but not set. Check .env file or AWS Secrets Manager."
            )

        return self

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string (comma-separated or JSON) or return list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
