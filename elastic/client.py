"""Elasticsearch client wrapper with connection management."""
import logging
from elasticsearch import Elasticsearch
from config import get_es_config

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Wrapper for Elasticsearch client with error handling."""

    def __init__(self):
        """Initialize Elasticsearch client with config."""
        try:
            config = get_es_config()
            self.client = Elasticsearch(
                hosts=config["hosts"],
                basic_auth=config["basic_auth"],
                verify_certs=config["verify_certs"],
            )
            # Test connection
            if self.client.ping():
                logger.info("Connected to Elasticsearch")
            else:
                logger.warning("Elasticsearch connection test failed")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if connected to Elasticsearch."""
        if self.client is None:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False

    def get_client(self) -> Elasticsearch:
        """Get the Elasticsearch client instance."""
        return self.client
