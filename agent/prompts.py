"""Prompt templates for Gemini agent reasoning."""

INCIDENT_ANALYSIS_PROMPT = """
You are VenueIQ, an AI operational intelligence agent for stadium crisis management.

Analyze the following incident:
Incident ID: {incident_id}
Zone Affected: {zone_affected}
Severity: {severity}
Description: {description}

Provide:
1. Impact assessment
2. Available resources that could help
3. Recommended mitigation actions
4. Estimated impact of your recommendation

Be concise and actionable.
"""

RESOURCE_ALLOCATION_PROMPT = """
Given the following incident and available resources, determine optimal allocation:

Incident: {incident}
Available Assets: {assets}
Current Constraints: {constraints}

Recommend:
1. Which assets to deploy
2. Where to deploy them
3. Expected outcome
4. Risk factors
"""

COMMAND_GENERATION_PROMPT = """
Based on operator approval of the mitigation plan, generate execution commands:

Approved Plan: {plan}
Assets to Activate: {assets}
Target Zones: {zones}

Generate:
1. Immediate action steps
2. Communication templates
3. Monitoring checkpoints
"""
