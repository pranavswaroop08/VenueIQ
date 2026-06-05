import time
import streamlit as st
from elasticsearch import Elasticsearch


def render_trace_stream(trace_container, traces):
    """Re-render the full trace stream; newest block fades in smoothly."""
    type_styles = {
        "THOUGHT": ("trace-thought", "◈ NEURAL", "#94A3B8"),
        "TOOL CALL": ("trace-tool", "⬡ MCP TOOL", "#22D3EE"),
        "AGGREGATION": ("trace-agg", "◆ AGGREGATE", "#C084FC"),
        "PLAN": ("trace-plan", "▣ PLAN MATRIX", "#34D399"),
    }

    blocks = []
    for i, trace in enumerate(traces):
        css_class, label, accent = type_styles.get(trace["type"], ("trace-thought", trace["type"], "#94A3B8"))
        is_latest = i == len(traces) - 1
        anim = "trace-fade-in" if is_latest else "trace-visible"
        blocks.append(
            f'<div class="trace-block {css_class} {anim}" style="--trace-accent:{accent}">'
            f'<div class="trace-header">'
            f'<span class="trace-label">{label}</span>'
            f'<span class="trace-time">{trace["time"]} UTC</span>'
            f"</div>"
            f'<div class="trace-body">{trace["message"]}</div>'
            f"</div>"
        )

    trace_container.html(
        f'<div class="trace-stream" id="trace-stream">{"".join(blocks)}</div>'
    )


def _render_radar_loading(invoke_container):
    """Morph invoke control into animated radar loading state."""
    invoke_container.html(
        '<div class="invoke-loading-state">'
        '<div class="radar-scanner">'
        '<div class="radar-ring radar-ring-1"></div>'
        '<div class="radar-ring radar-ring-2"></div>'
        '<div class="radar-ring radar-ring-3"></div>'
        '<div class="radar-sweep"></div>'
        '<div class="radar-core"></div>'
        "</div>"
        '<div class="invoke-loading-text">'
        '<span class="invoke-loading-title">VENUEIQ ENGINE ACTIVE</span>'
        '<span class="invoke-loading-sub">Scanning Elastic MCP transport layer…</span>'
        "</div>"
        '<div class="invoke-loading-bar"><div class="invoke-loading-bar-fill"></div></div>'
        "</div>"
    )


def run_venue_iq_agent(es_client, incident_doc, invoke_container=None, trace_container=None):
    """
    Simulates the Gemini 3 tool orchestration path over the
    Elastic MCP transport layer, populating the live trace window.
    """
    if invoke_container is not None:
        _render_radar_loading(invoke_container)

    if trace_container is not None:
        trace_container.html(
            '<div class="trace-stream trace-stream-active">'
            '<div class="trace-idle-pulse">Establishing secure uplink to agent core…</div>'
            "</div>"
        )

    def _push(trace_type, time_str, message):
        st.session_state.agent_traces.append(
            {"type": trace_type, "time": time_str, "message": message}
        )
        if trace_container is not None:
            render_trace_stream(trace_container, st.session_state.agent_traces)

    # Step 1: Ingest & Parse Thought
    _push(
        "THOUGHT",
        "18:42:18",
        f"Parsing active incident {incident_doc['incident_id']}. "
        f"Target vectors isolated: {incident_doc['zone_affected']} corridor.",
    )
    time.sleep(1.2)

    # Step 2: Tool Call to Logistics
    _push(
        "TOOL CALL",
        "18:42:19",
        "Executing search_documents via Elastic MCP on 'worldcup-logistics' "
        "for radius: 3km, current_status: 'Idle'.",
    )

    try:
        response = es_client.search(
            index="worldcup-logistics",
            query={"term": {"current_status.keyword": "Idle"}},
        )
        hits = [hit["_source"] for hit in response["hits"]["hits"]]
        total_capacity = sum([h["passenger_capacity"] for h in hits])
    except Exception:
        hits = [
            {"asset_id": "Shuttle-104", "proposed": "Reroute to Gate 4", "dest": "Emergency Exit Support"},
            {"asset_id": "Shuttle-112", "proposed": "Reroute to Gate 4", "dest": "Emergency Exit Support"},
        ]
        total_capacity = 160

    time.sleep(1.5)

    # Step 3: Aggregation Log
    _push(
        "AGGREGATION",
        "18:42:21",
        f"Found {len(hits)} high-capacity units matching constraint vector. "
        f"Aggregated volume: {total_capacity} passengers.",
    )
    time.sleep(1.0)

    # Step 4: Draft Matrix & Hand off to HITL queue
    _push(
        "PLAN",
        "18:42:22",
        "Mitigation matrix balanced. Generating human-in-the-loop payload array…",
    )

    st.session_state.hitl_queue_active = True
    st.session_state.processing_state = "WAITING"

    if invoke_container is not None:
        invoke_container.empty()
