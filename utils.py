"""Utility functions for VenueIQ."""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in HH:MM:SS format."""
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def safe_es_query(es_client, **kwargs) -> Optional[Dict[str, Any]]:
    """Execute Elasticsearch query with error handling.
    
    Args:
        es_client: Elasticsearch client instance
        **kwargs: Arguments to pass to es.search()
    
    Returns:
        Query response or None on error
    """
    try:
        return es_client.search(**kwargs)
    except Exception as e:
        logger.error(f"Elasticsearch query failed: {e}")
        return None


def format_asset_for_display(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Format asset data for dashboard display."""
    return {
        "id": asset.get("asset_id", "UNKNOWN"),
        "type": asset.get("asset_type", "unknown"),
        "status": asset.get("current_status", "UNKNOWN"),
        "capacity": asset.get("passenger_capacity", 0),
    }


def log_agent_action(action: str, details: Dict[str, Any]) -> None:
    """Log agent action for debugging."""
    logger.info(f"Agent Action: {action}")
    logger.debug(f"Details: {details}")
