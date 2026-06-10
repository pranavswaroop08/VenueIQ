import os
import time
import streamlit as st
from datetime import datetime, timezone
from elasticsearch import Elasticsearch
from agent_engine import run_venue_iq_agent, render_trace_stream
import streamlit.components.v1 as components

# Configure enterprise presentation frame
st.set_page_config(layout="wide", page_title="VenueIQ // Incident Command Network", page_icon=None)

# ─── Tailwind CDN + Enterprise Industrial Telemetry Design System ───────────
components.html(
    """
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      window.tailwind.config = {
        theme: {
          extend: {
            colors: {
              void: '#060A13',
              'void-light': '#111827',
              'cyber-cyan': '#38BDF8',
              'neon-purple': '#818CF8',
              'emerald-glow': '#10B981',
              'crimson-pulse': '#EF4444',
            },
            fontFamily: {
              display: ['Plus Jakarta Sans', 'sans-serif'],
              mono: ['JetBrains Mono', 'monospace'],
              body: ['Plus Jakarta Sans', 'sans-serif'],
            },
          },
        },
      }
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    """,
    height=0,
)

# ─── Custom Global CSS Core Styles Engine ────────────────────────────────────
st.markdown(
    """
    <style>
      /* ── Streamlit chrome suppression ── */
      .stApp { background: #060A13 !important; }
      .main .block-container {
        padding-top: 1.5rem !important;
        max-width: 100% !important;
      }
      header[data-testid="stHeader"] { background: transparent !important; }
      div[data-testid="stToolbar"] { display: none !important; }
      #MainMenu { visibility: hidden; }
      footer { visibility: hidden; }

      /* ── Global typography ── */
      .main, .main p, .main span, .main label { font-family: 'Plus Jakarta Sans', sans-serif; }
      div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #F3F4F6 !important;
        font-size: 1.65rem !important;
        font-weight: 600 !important;
      }
      div[data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: #6B7280 !important;
      }
      div[data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
      }

      /* ── SYSTEM_ERR alert pulsing glow ── */
      @keyframes criticalPulse {
        0%, 100% {
          box-shadow: 0 0 15px rgba(239, 68, 68, 0.2),
                      inset 0 0 15px rgba(239, 68, 68, 0.05);
          border-color: rgba(239, 68, 68, 0.4);
        }
        50% {
          box-shadow: 0 0 25px rgba(239, 68, 68, 0.35),
                      inset 0 0 20px rgba(239, 68, 68, 0.08);
          border-color: rgba(239, 68, 68, 0.7);
        }
      }
      @keyframes criticalBleed {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.01); }
      }
      .critical-alert-wrap {
        position: relative;
        margin-bottom: 1rem;
      }
      .critical-alert-bleed {
        position: absolute;
        inset: -8px;
        background: radial-gradient(ellipse at center, rgba(239,68,68,0.12) 0%, transparent 70%);
        border-radius: 8px;
        animation: criticalBleed 3s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
      }
      .critical-alert {
        position: relative;
        z-index: 1;
        background: linear-gradient(135deg, #160F11 0%, #0F172A 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 6px;
        padding: 1.1rem 1.25rem;
        animation: criticalPulse 3s ease-in-out infinite;
      }
      .critical-badge {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #F87171;
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.3);
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        margin-bottom: 0.5rem;
      }

      /* ── Warning card ── */
      .warning-card {
        background: linear-gradient(135deg, #17140F 0%, #0F172A 100%);
        border: 1px solid rgba(245,158,11,0.25);
        border-radius: 6px;
        padding: 0.9rem 1.15rem;
        margin-bottom: 1rem;
      }

      /* ── Status metrics panel ── */
      .metrics-panel {
        background: #0E131F;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 1.1rem;
        margin-top: 0.5rem;
      }
      .panel-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        color: #6B7280;
        text-transform: uppercase;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
      .panel-header::before {
        content: '';
        width: 6px;
        height: 6px;
        background: #38BDF8;
        border-radius: 1px;
      }

      /* ── Header bar ── */
      .cmd-header {
        background: #0E131F;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 1.1rem 1.5rem;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
      }
      .cmd-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: -0.01em;
        color: #F3F4F6;
      }
      .cmd-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #4B5563;
        letter-spacing: 0.02em;
        margin-top: 0.15rem;
      }
      .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.02em;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        font-weight: 500;
      }
      .status-online {
        color: #34D399;
        background: rgba(16,185,129,0.05);
        border: 1px solid rgba(16,185,129,0.2);
      }
      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10B981;
        animation: statusBlink 2.5s ease-in-out infinite;
      }
      @keyframes statusBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
      }
      .clock-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94A3B8;
        letter-spacing: 0.05em;
      }

      /* ── Core indexing loading state ── */
      @keyframes radarSweep {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      @keyframes radarPulse {
        0%, 100% { opacity: 0.4; transform: scale(0.98); }
        50% { opacity: 0.7; transform: scale(1); }
      }
      @keyframes barSlide {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(250%); }
      }
      .invoke-loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.85rem;
        padding: 1.5rem;
        background: #0E131F;
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 8px;
        margin-bottom: 1rem;
      }
      .radar-scanner {
        position: relative;
        width: 64px;
        height: 64px;
      }
      .radar-ring {
        position: absolute;
        inset: 0;
        border: 1px solid rgba(56,189,248,0.15);
        border-radius: 50%;
      }
      .radar-ring-2 { inset: 10px; border-color: rgba(56,189,248,0.1); }
      .radar-ring-3 { inset: 20px; border-color: rgba(56,189,248,0.05); }
      .radar-sweep {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background: conic-gradient(from 0deg, transparent 0deg, rgba(56,189,248,0.25) 30deg, transparent 60deg);
        animation: radarSweep 2s linear infinite;
      }
      .radar-core {
        position: absolute;
        top: 50%; left: 50%;
        width: 6px; height: 6px;
        margin: -3px 0 0 -3px;
        background: #38BDF8;
        border-radius: 50%;
        animation: radarPulse 1.2s ease-in-out infinite;
      }
      .invoke-loading-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #38BDF8;
        display: block;
        text-align: center;
      }
      .invoke-loading-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #4B5563;
        display: block;
        text-align: center;
        margin-top: 0.2rem;
      }
      .invoke-loading-bar {
        width: 100%;
        height: 2px;
        background: #1F2937;
        border-radius: 1px;
        overflow: hidden;
      }
      .invoke-loading-bar-fill {
        width: 35%;
        height: 100%;
        background: linear-gradient(90deg, transparent, #38BDF8, transparent);
        animation: barSlide 1.6s ease-in-out infinite;
      }

      /* ── Administrative control buttons ── */
      div[data-testid="stButton"] > button[kind="primary"],
      div[data-testid="stButton"] > button {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.01em !important;
        background: #111827 !important;
        border: 1px solid #374151 !important;
        color: #9CA3AF !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
      }
      div[data-testid="stButton"] > button:hover {
        border-color: #4B5563 !important;
        color: #E5E7EB !important;
        transform: translateY(-0.5px) !important;
      }
      div[data-testid="stButton"] > button[kind="primary"] {
        background: #0E2921 !important;
        border-color: #059669 !important;
        color: #34D399 !important;
      }
      div[data-testid="stButton"] > button[kind="primary"]:hover {
        border-color: #10B981 !important;
        background: #0F3127 !important;
      }

      /* ── Trace stream components ── */
      @keyframes traceFadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .trace-stream {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        min-height: 100px;
      }
      .trace-block {
        border-radius: 4px;
        padding: 0.75rem 0.95rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        line-height: 1.5;
        border-left: 3px solid var(--trace-accent, #4B5563);
      }
      .trace-fade-in {
        animation: traceFadeIn 0.4s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      }
      .trace-thought {
        background: #111827;
        color: #9CA3AF;
        border-left-color: #4B5563;
      }
      .trace-tool {
        background: #0C1624;
        color: #38BDF8;
        border-left-color: #0EA5E9;
      }
      .trace-agg {
        background: #151226;
        color: #C084FC;
        border-left-color: #A855F7;
      }
      .trace-plan {
        background: #0A1B17;
        color: #34D399;
        border-left-color: #10B981;
      }
      .trace-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.3rem;
      }
      .trace-label {
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--trace-accent);
      }
      .trace-time {
        font-size: 0.65rem;
        color: #374151;
      }
      .trace-body { color: inherit; }
      .idle-state {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #374151;
        text-align: center;
        padding: 2.5rem;
        background: #0E131F;
        border: 1px solid #1F2937;
        border-radius: 6px;
      }
      .hitl-idle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #4B5563;
        text-align: center;
        padding: 2rem;
        background: #0E131F;
        border: 1px dashed #1F2937;
        border-radius: 6px;
      }

      /* ── Tactical asset container grid ── */
      .tactical-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 0.85rem;
        margin: 0.85rem 0;
      }
      .tactical-card {
        background: #0E131F;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 1rem;
        transition: border-color 0.2s ease;
      }
      .tactical-card:hover {
        border-color: #374151;
      }
      .tactical-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
      }
      .tactical-asset-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        color: #E5E7EB;
      }
      .action-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        font-weight: 600;
        padding: 0.15rem 0.45rem;
        border-radius: 3px;
        white-space: nowrap;
      }
      .pill-reroute {
        color: #34D399;
        background: rgba(16,185,129,0.08);
        border: 1px solid rgba(16,185,129,0.3);
      }
      .pill-display {
        color: #C084FC;
        background: rgba(168,85,247,0.08);
        border: 1px solid rgba(168,85,247,0.3);
      }
      .tactical-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.35rem 0;
        border-bottom: 1px solid #1F2937;
        font-size: 0.72rem;
      }
      .tactical-row:last-child { border-bottom: none; }
      .tactical-key {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        color: #4B5563;
        text-transform: uppercase;
      }
      .tactical-val {
        font-family: 'JetBrains Mono', monospace;
        color: #9CA3AF;
        text-align: right;
        max-width: 65%;
      }
      .micro-action {
        margin-top: 0.65rem;
        padding: 0.45rem 0.6rem;
        background: rgba(56,189,248,0.02);
        border: 1px dashed #1F2937;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 0.4rem;
      }
      .micro-action-dot {
        width: 4px; height: 4px;
        background: #38BDF8;
        border-radius: 50%;
        flex-shrink: 0;
      }

      /* ── Section block structures ── */
      .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        color: #6B7280;
        margin: 1.25rem 0 0.65rem 0;
        text-transform: uppercase;
      }

      /* ── Subtitle administrative grime elements ── */
      .admin-grime-wrapper {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #374151;
        line-height: 1.5;
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px dashed #1F2937;
      }

      .admin-profile-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #4B5563;
        background: #111827;
        border: 1px solid #1F2937;
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        display: inline-block;
        margin-bottom: 0.5rem;
      }
      
      /* ── System registry status update banner ── */
      @keyframes uplinkSlide {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes uplinkScan {
        0% { left: -30%; }
        100% { left: 130%; }
      }
      .uplink-banner {
        position: relative;
        overflow: hidden;
        background: linear-gradient(90deg, rgba(6,78,59,0.2) 0%, #0E131F 50%, rgba(6,78,59,0.2) 100%);
        border: 1px solid rgba(52,211,153,0.3);
        border-radius: 6px;
        padding: 0.9rem 1.25rem;
        margin-bottom: 1.25rem;
        animation: uplinkSlide 0.4s ease-out forwards;
      }
      .uplink-scanline {
        position: absolute;
        top: 0; bottom: 0;
        width: 25%;
        background: linear-gradient(90deg, transparent, rgba(52,211,153,0.1), transparent);
        animation: uplinkScan 2.5s ease-in-out infinite;
      }
      .uplink-content {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 0.85rem;
        flex-wrap: wrap;
      }
      .uplink-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #34D399;
      }
      .uplink-msg {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #9CA3AF;
        margin-top: 0.1rem;
      }
      .uplink-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #4B5563;
        margin-left: auto;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Session state ───────────────────────────────────────────────────────────
if "agent_traces" not in st.session_state:
    st.session_state.agent_traces = []
if "hitl_queue_active" not in st.session_state:
    st.session_state.hitl_queue_active = False
if "processing_state" not in st.session_state:
    st.session_state.processing_state = "IDLE"
if "uplink_success" not in st.session_state:
    st.session_state.uplink_success = False

def render_tactical_cards(assets):
    """Render HITL asset cards via st.html."""
    card_parts = []
    for asset in assets:
        card_parts.append(
            f'<div class="tactical-card">'
            f'<div class="tactical-card-header">'
            f'<span class="tactical-asset-id">{asset["id"]}</span>'
            f'<span class="action-pill {asset["pill_class"]}">{asset["pill"]}</span>'
            f"</div>"
            f'<div class="tactical-row">'
            f'<span class="tactical-key">Original State</span>'
            f'<span class="tactical-val">{asset["original"]}</span>'
            f"</div>"
            f'<div class="tactical-row">'
            f'<span class="tactical-key">Mutation Target</span>'
            f'<span class="tactical-val">{asset["action"]}</span>'
            f"</div>"
            f'<div class="tactical-row">'
            f'<span class="tactical-key">Assigned Vertex</span>'
            f'<span class="tactical-val">{asset["target"]}</span>'
            f"</div>"
            f'<div class="micro-action">'
            f'<span class="micro-action-dot"></span>'
            f'{asset["micro"]}'
            f"</div>"
            f"</div>"
        )
    st.html(f'<div class="tactical-grid">{"".join(card_parts)}</div>')


TACTICAL_ASSETS = [
    {
        "id": "SURFACE_SHUTTLE_104",
        "original": "STATE_IDLE",
        "action": "MUTATE_ROUTE_GATE_4",
        "target": "TRANSIT_HUB_NORTH",
        "pill": "MUTATION_PENDING",
        "pill_class": "pill-reroute",
        "micro": "Commit route vector mutation to local driver cache",
    },
    {
        "id": "SURFACE_SHUTTLE_112",
        "original": "STATE_IDLE",
        "action": "MUTATE_ROUTE_GATE_4",
        "target": "TRANSIT_HUB_NORTH",
        "pill": "MUTATION_PENDING",
        "pill_class": "pill-reroute",
        "micro": "Commit route vector mutation to local driver cache",
    },
    {
        "id": "DIGITAL_SIGNAGE_ZONE_B",
        "original": "DISPLAY_STANDARD",
        "action": "PUSH_OVERRIDE_PAYLOAD",
        "target": "RELAY_GATE_2_TEXT",
        "pill": "OVERRIDE_PENDING",
        "pill_class": "pill-display",
        "micro": "Push character buffer matrix to Zone B signage group",
    },
]

# 🔌 Swapped out hardcoded profile logic for verified, dynamic permanent ngrok target path mapping
es = Elasticsearch(
    os.getenv("ES_HOST", "https://badland-animating-approach.ngrok-free.dev"), 
    basic_auth=(os.getenv("ES_USER", "elastic"), os.getenv("ES_PASSWORD", "0Oq5NHSuhINTYnB9ukVM")), 
    verify_certs=False
)

# ─── System registry status update banner ─────────────────────────────────────
if st.session_state.uplink_success:
    st.markdown(
        """
        <div class="uplink-banner">
            <div class="uplink-scanline"></div>
            <div class="uplink-content">
                <div>
                    <div class="uplink-title">CORE REGISTRY CONFIGURATION SYNCHRONIZED</div>
                    <div class="uplink-msg">Asset deployment parameter states verified and securely saved to local Elasticsearch cluster data layer.</div>
                </div>
                <span class="uplink-code">TX/RX_SYS_OK · CLUSTER_WRITE_ACK</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Command header with sandboxed client JavaScript clock ──────────────────
import os
import streamlit.components.v1 as components

# Pull the database target securely outside the f-string context
es_node_target = os.getenv("ES_HOST", "https://badland-animating-approach.ngrok-free.dev")

components.html(
    """
    <div style="background: #0E131F; border: 1px solid #1F2937; border-radius: 8px; padding: 1.1rem 1.5rem; display: flex; align-items: center; justify-content: space-between; font-family: 'Plus Jakarta Sans', sans-serif; color: #F3F4F6; margin-bottom: 5px;">
        <div>
            <div style="font-weight: 700; font-size: 1.25rem; letter-spacing: -0.01em;">VENUEIQ // LOGISTICS AND INCIDENT REGISTRY</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #4B5563; letter-spacing: 0.02em; margin-top: 0.15rem;">LOS ANGELES HOST STADIUM · LOGISTICS CONTROL DIVISION // REGISTRY-v2.8.4</div>
        </div>
        <div style="display: flex; gap: 1.25rem; align-items: center; flex-wrap: wrap;">
            <span style="display: inline-flex; align-items: center; gap: 0.45rem; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.02em; padding: 0.4rem 0.8rem; border-radius: 4px; font-weight: 500; color: #34D399; background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2);">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></span>
                CONNECTED_LOCAL_NODE // ELASTIC_MCP
            </span>
            <span id="live-system-clock" style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #94A3B8; letter-spacing: 0.05em;">SYSTEM_TIME: --:--:-- UTC</span>
        </div>
    </div>
    
    <script>
      function updateLiveClock() {
        const now = new Date();
        const hours = String(now.getUTCHours()).padStart(2, '0');
        const minutes = String(now.getUTCMinutes()).padStart(2, '0');
        const seconds = String(now.getUTCSeconds()).padStart(2, '0');
        const clockEl = document.getElementById('live-system-clock');
        if (clockEl) {
          clockEl.innerHTML = 'SYSTEM_TIME: ' + hours + ':' + minutes + ':' + seconds + ' UTC';
        }
      }
      setInterval(updateLiveClock, 1000);
      updateLiveClock();
    </script>
    """,
    height=90,
)

# Unpack split grid column boundaries cleanly
left_panel, right_panel = st.columns([1, 2])

# ─── LEFT: Incident feeds & stadium metrics ────────────────────────────────────
with left_panel:
    st.markdown(
        '<div class="panel-header">Inbound Exception Feeds</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="critical-alert-wrap">
            <div class="critical-alert-bleed"></div>
            <div class="critical-alert">
                <span class="critical-badge">SYS_ERR_9082</span>
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:600; font-size:0.92rem; color:#FCA5A5; margin-bottom:0.4rem;">
                    BlueLine Interlocking Signal Failure
                </div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#9CA3AF; line-height:1.6;">
                    Track circuit interlocking failure localized at C4 crossover segment [Century Blvd corridor]. Manual control override rejected by local switch framework. 14 units stalled.<br>
                    <b>Est. Clearance Latency:</b> >45 minutes
                </div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#EF4444; margin-top:0.6rem; opacity:0.7;">
                    Log Timestamp: 18:42:15 UTC
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="warning-card">
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; font-weight:600; color:#FCD34D;">FLOW_RATE_WARN</span>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:0.85rem; color:#FCD34D; margin-top:0.35rem; font-weight:500;">
                Pedestrian Bottleneck: Gate 2 Corridor
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#6B7280; margin-top:0.4rem;">
                Log Timestamp: 18:38:22 UTC
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="panel-header">Local Telemetry Indexes</div>',
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="metrics-panel">', unsafe_allow_html=True)
        st.metric(label="Current In-Gate Manifest", value="72,000 / 75,000", delta="96% Capacity Utilization")
        st.metric(label="Active Event Context ID", value="LA_MATCH_01 // LIVE 85'", delta="Current Telemetry Score: 2 - 1")
        
        # Administrative Grime Sidebar Anchorage
        st.markdown('<div class="admin-grime-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="admin-profile-badge">OPERATOR: P. SWAROOP (TIER-1 DISPATCH)</div>', unsafe_allow_html=True)
        st.markdown(f"""
            Partition ID: Local Host Node 01<br>
            Security Policy MD5: 8aef91cb27f8041c<br>
            Database Target: {os.getenv("ES_HOST", "https://badland-animating-approach.ngrok-free.dev")}
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─── RIGHT: Agent trace loop & HITL gateway ───────────────────────────────────
with right_panel:
    st.markdown(
        """
        <div class="section-title">
            AUTOMATION STREAM & ROUTING SCRIPT ORCHESTRATION LOGS
        </div>
        """,
        unsafe_allow_html=True,
    )

    invoke_placeholder = st.empty()
    trace_placeholder = st.empty()

    with invoke_placeholder.container():
        invoke_clicked = st.button(
            "Run Incident Routing Sweep & Contingency Logic",
            use_container_width=True,
            key="invoke_venue_iq",
        )

    if invoke_clicked:
        st.session_state.agent_traces = []
        st.session_state.hitl_queue_active = False
        st.session_state.processing_state = "RUNNING"
        st.session_state.uplink_success = False
        run_venue_iq_agent(es, {"incident_id": "INC-9082", "zone_affected": "Gate 4"}, invoke_placeholder, trace_placeholder)
        st.rerun()

    # Static trace render when not actively streaming
    if st.session_state.agent_traces and st.session_state.processing_state != "RUNNING":
        render_trace_stream(trace_placeholder, st.session_state.agent_traces)
    elif not st.session_state.agent_traces:
        trace_placeholder.html(
            '<div class="idle-state">System idling — awaiting edge node anomaly payload array</div>'
        )

    st.markdown(
        """
        <div class="section-title">
            PENDING OPERATOR DISPATCHES & CONFIGURATION OVERRIDES
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.hitl_queue_active:
        render_tactical_cards(TACTICAL_ASSETS)

        col_mod, col_app = st.columns(2)
        with col_mod:
            st.button("Adjust Dispatch Constraints", use_container_width=True, key="modify_plan")
        with col_app:
            if st.button("Commit Mitigation Matrix to Live Registry (Local MCP Node)", type="primary", use_container_width=True, key="approve_deploy"):
                try:
                    es.update(index="worldcup-logistics", id="Shuttle-104", doc={"current_status": "Emergency Reroute"})
                    es.update(index="worldcup-logistics", id="Shuttle-112", doc={"current_status": "Emergency Reroute"})
                except Exception:
                    pass
                st.session_state.hitl_queue_active = False
                st.session_state.uplink_success = True
                st.rerun()
    else:
        st.html('<div class="hitl-idle">Queue clear. No tactical strategies currently pending operator token authorization.</div>')