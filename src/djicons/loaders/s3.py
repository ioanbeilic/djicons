"""
S3 icon loader for djicons.

Loads SVG icons from an AWS S3 bucket. Useful for sharing icons
across multiple Django projects without duplicating files in each repo.

Example usage in settings.py:

    DJICONS = {
        "S3": {
            "bucket": "my-bucket",
            "region": "eu-west-1",
            "namespaces": {
                "material": "djicons/material/",
                "ion": "djicons/ion/",
            }
        }
    }

boto3 must be installed separately: pip install boto3
If boto3 is not installed, the loader silently does nothing.
"""

from .base import BaseIconLoader


class S3IconLoader(BaseIconLoader):
    """
    Load icons from an AWS S3 bucket.

    Uses boto3 for S3 access. Credentials are resolved via boto3's
    standard chain (IAM role, env vars, ~/.aws/credentials).

    Args:
        bucket: S3 bucket name
        prefix: Key prefix for this namespace (e.g. "djicons/material/")
        region: AWS region (default: "us-east-1")
        aws_access_key_id: Optional explicit AWS key (default: boto3 chain)
        aws_secret_access_key: Optional explicit AWS secret (default: boto3 chain)
    """

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        region: str = "us-east-1",
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = (prefix.rstrip("/") + "/") if prefix else ""
        self.region = region
        self._aws_key = aws_access_key_id
        self._aws_secret = aws_secret_access_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
            except ImportError:
                return None
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=self._aws_key,
                aws_secret_access_key=self._aws_secret,
            )
        return self._client

    def load(self, name: str) -> str | None:
        """Load a single icon SVG from S3. Returns None if not found or S3 unavailable."""
        if self.client is None:
            return None
        try:
            key = f"{self.prefix}{name}.svg"
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read().decode("utf-8")
        except Exception:
            return None

    def list(self) -> list[str]:
        """List all icon names available under this prefix in S3."""
        if self.client is None:
            return []
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            names = []
            for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
                for obj in page.get("Contents", []):
                    key = obj["Key"][len(self.prefix):]
                    if key.endswith(".svg") and "/" not in key:
                        names.append(key[:-4])
            return names
        except Exception:
            return []
