"""Mitigation planning engine for VenueIQ."""
import logging
from typing import Any, Dict, List, Optional
from utils import get_utc_timestamp

logger = logging.getLogger(__name__)


class MitigationPlanner:
    """Generates optimized mitigation strategies based on incident analysis."""

    def __init__(self):
        self.plans = []

    def generate_plan(
        self,
        incident_id: str,
        zone_affected: str,
        available_assets: List[Dict[str, Any]],
        incident_severity: str = "medium",
    ) -> Dict[str, Any]:
        """Generate a mitigation plan.
        
        Args:
            incident_id: The incident identifier
            zone_affected: The affected zone
            available_assets: List of available resources
            incident_severity: Severity level (low, medium, high, critical)
        
        Returns:
            Mitigation plan dictionary
        """
        plan = {
            "plan_id": f"PLAN-{incident_id}-{get_utc_timestamp()}",
            "incident_id": incident_id,
            "zone_affected": zone_affected,
            "severity": incident_severity,
            "timestamp": get_utc_timestamp(),
            "recommended_assets": self._select_assets(
                available_assets, incident_severity
            ),
            "actions": self._generate_actions(zone_affected, incident_severity),
            "estimated_impact": self._estimate_impact(
                len(available_assets), incident_severity
            ),
            "requires_approval": True,
            "approved": False,
        }
        self.plans.append(plan)
        logger.info(f"Generated mitigation plan: {plan['plan_id']}")
        return plan

    def _select_assets(
        self, assets: List[Dict[str, Any]], severity: str
    ) -> List[Dict[str, Any]]:
        """Select assets based on incident severity."""
        if severity == "critical":
            return assets  # Use all available assets
        elif severity == "high":
            return assets[:2]  # Use top 2 assets
        else:
            return assets[:1]  # Use single asset

    def _generate_actions(self, zone: str, severity: str) -> List[Dict[str, str]]:
        """Generate mitigation actions."""
        base_actions = [
            {
                "action": "ALERT_OPERATIONS_TEAM",
                "target": "Gate Operations",
                "priority": "IMMEDIATE",
            },
            {
                "action": "ACTIVATE_ASSETS",
                "target": zone,
                "priority": "HIGH",
            },
        ]
        if severity in ["high", "critical"]:
            base_actions.append(
                {
                    "action": "NOTIFY_EMERGENCY_SERVICES",
                    "target": "External Services",
                    "priority": "HIGH",
                }
            )
        return base_actions

    def _estimate_impact(self, asset_count: int, severity: str) -> Dict[str, Any]:
        """Estimate the impact of mitigation plan."""
        base_effectiveness = min(asset_count * 25, 100)  # Up to 100%
        if severity == "critical":
            base_effectiveness = min(base_effectiveness + 20, 100)

        return {
            "effectiveness": f"{base_effectiveness}%",
            "response_time": "< 5 minutes",
            "estimated_people_protected": asset_count * 80,
        }

    def approve_plan(self, plan_id: str) -> bool:
        """Mark a plan as approved."""
        for plan in self.plans:
            if plan["plan_id"] == plan_id:
                plan["approved"] = True
                logger.info(f"Plan approved: {plan_id}")
                return True
        logger.warning(f"Plan not found: {plan_id}")
        return False
