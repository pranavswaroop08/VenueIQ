"""Main VenueIQ agent for incident orchestration."""
import logging
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from agent.planner import MitigationPlanner
from agent.prompts import INCIDENT_ANALYSIS_PROMPT
from utils import safe_es_query, get_utc_timestamp, log_agent_action

logger = logging.getLogger(__name__)


class VenueIQAgent:
    """Autonomous agent for venue crisis management."""

    def __init__(self, es_client: Elasticsearch, gemini_client: Optional[Any] = None):
        """Initialize VenueIQ Agent.
        
        Args:
            es_client: Elasticsearch client for data access
            gemini_client: Optional Google Gemini client for AI reasoning
        """
        self.es_client = es_client
        self.gemini_client = gemini_client
        self.planner = MitigationPlanner()
        self.traces = []

    def analyze_incident(
        self, incident_id: str, zone_affected: str
    ) -> Dict[str, Any]:
        """Analyze an incident and generate response plan.
        
        Args:
            incident_id: The incident identifier
            zone_affected: The affected zone
        
        Returns:
            Analysis result with mitigation plan
        """
        self._add_trace(
            "THOUGHT",
            f"Analyzing incident {incident_id} in zone {zone_affected}",
        )

        # Fetch incident details
        incident = self._get_incident(incident_id)
        if not incident:
            logger.warning(f"Incident not found: {incident_id}")
            incident = {"incident_id": incident_id, "zone_affected": zone_affected}

        self._add_trace(
            "TOOL CALL",
            f"Querying Elasticsearch for available assets in {zone_affected}",
        )

        # Fetch available assets
        assets = self._get_available_assets(zone_affected)
        self._add_trace(
            "AGGREGATION", f"Found {len(assets)} available assets for deployment"
        )

        # Generate mitigation plan
        plan = self.planner.generate_plan(
            incident_id=incident_id,
            zone_affected=zone_affected,
            available_assets=assets,
            incident_severity=incident.get("severity", "medium"),
        )

        self._add_trace(
            "PLAN", "Mitigation plan generated. Awaiting operator approval."
        )
        log_agent_action(
            "INCIDENT_ANALYZED",
            {"incident_id": incident_id, "plan_id": plan["plan_id"]},
        )

        return {"incident": incident, "assets": assets, "plan": plan}

    def execute_plan(self, plan_id: str, approved_by: str) -> Dict[str, Any]:
        """Execute an approved mitigation plan.
        
        Args:
            plan_id: The plan identifier
            approved_by: Operator who approved the plan
        
        Returns:
            Execution result
        """
        self._add_trace("THOUGHT", f"Executing approved plan {plan_id}")

        # Approve the plan
        if not self.planner.approve_plan(plan_id):
            return {"success": False, "error": f"Plan not found: {plan_id}"}

        self._add_trace(
            "TOOL CALL", "Committing mitigation actions to Elasticsearch cluster"
        )

        # Execute actions (would update Elasticsearch in production)
        try:
            # In production, this would make actual updates to Elasticsearch
            log_agent_action(
                "PLAN_EXECUTED",
                {"plan_id": plan_id, "approved_by": approved_by},
            )
            self._add_trace("PLAN", "Plan execution successful.")
            return {"success": True, "plan_id": plan_id, "status": "EXECUTED"}
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            return {"success": False, "error": str(e)}

    def _get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Fetch incident details from Elasticsearch."""
        response = safe_es_query(
            self.es_client,
            index="worldcup-incidents",
            query={"term": {"incident_id.keyword": incident_id}},
        )
        if response and response["hits"]["hits"]:
            return response["hits"]["hits"][0]["_source"]
        return None

    def _get_available_assets(
        self, zone_affected: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch available assets from Elasticsearch."""
        response = safe_es_query(
            self.es_client,
            index="worldcup-logistics",
            query={"term": {"current_status.keyword": "Idle"}},
            size=limit,
        )
        if response and response["hits"]["hits"]:
            return [hit["_source"] for hit in response["hits"]["hits"]]
        return []

    def _add_trace(
        self, trace_type: str, message: str, timestamp: Optional[str] = None
    ) -> None:
        """Add a trace entry for debugging."""
        if timestamp is None:
            timestamp = get_utc_timestamp()
        self.traces.append(
            {"type": trace_type, "message": message, "time": timestamp}
        )

    def get_traces(self) -> List[Dict[str, str]]:
        """Get all agent traces."""
        return self.traces

    def clear_traces(self) -> None:
        """Clear trace history."""
        self.traces = []
