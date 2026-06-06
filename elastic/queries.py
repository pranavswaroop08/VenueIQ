"""Pre-built Elasticsearch queries for common operations."""
from typing import Any, Dict, List


def query_incidents_by_zone(zone: str) -> Dict[str, Any]:
    """Query incidents in a specific zone."""
    return {"query": {"term": {"zone_affected.keyword": zone}}}


def query_available_assets() -> Dict[str, Any]:
    """Query all available assets."""
    return {"query": {"term": {"current_status.keyword": "Idle"}}}


def query_active_incidents() -> Dict[str, Any]:
    """Query all active incidents."""
    return {"query": {"term": {"status.keyword": "active"}}}


def update_asset_status(asset_id: str, new_status: str) -> Dict[str, Any]:
    """Generate update query for asset status."""
    return {"doc": {"current_status": new_status}}
