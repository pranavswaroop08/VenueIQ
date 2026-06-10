# VenueIQ

# Website: https://venueiq.streamlit.app/

> Autonomous Crisis Management for Large-Scale Sporting Events

VenueIQ is an AI-powered stadium operations agent designed to help venue operators respond to real-time transit, infrastructure, and crowd-management incidents during major sporting events such as the FIFA World Cup.

Built for the Google Cloud Rapid Agent Hackathon, VenueIQ combines Gemini-powered reasoning with Elastic-powered operational intelligence to move beyond dashboards and into actionable decision-making.

---

## Problem

When a critical incident occurs near a stadium—such as a metro outage, transportation failure, security disruption, or crowd bottleneck—operations teams often rely on fragmented dashboards and manual coordination.

This leads to:

- Slow response times
- Communication delays
- Resource misallocation
- Increased safety risks
- Poor fan experience

VenueIQ transforms incident response from reactive monitoring into proactive orchestration.

---

## Solution

VenueIQ continuously analyzes operational data and recommends mitigation strategies in real time.

When a disruption occurs, the agent:

1. Detects the incident
2. Analyzes event context
3. Identifies available nearby resources
4. Generates an optimized response plan
5. Presents recommendations for operator approval
6. Executes approved actions

Human operators remain fully in control through a Human-In-The-Loop (HITL) approval workflow.

---

## Example Scenario

### Metro Rail Power Failure

A metro outage occurs near the stadium shortly before match completion.

VenueIQ:

- Detects the incident
- Identifies affected gates and transport corridors
- Analyzes expected crowd exit volumes
- Locates available shuttle assets
- Calculates rerouting capacity
- Generates fan communication alerts
- Presents deployment recommendations
- Executes approved reroutes

Result:

- Reduced congestion
- Faster evacuation flow
- Improved fan safety
- Reduced operational workload

---

## Architecture

```text
Operator Dashboard
        │
        ▼
Google Gemini Agent
        │
        ▼
Elastic MCP Server
        │
 ┌──────┼──────┐
 ▼      ▼      ▼

Incidents  Schedule  Logistics
 Index      Index      Index
```

### Components

#### Frontend

- Streamlit Dashboard
- Live Incident Feed
- Human-In-The-Loop Queue
- Agent Trace Viewer

#### Agent Layer

- Gemini Reasoning Engine
- Multi-Step Planning
- Operational Decision Support

#### Data Layer

Elasticsearch stores:

- Incident telemetry
- Match schedules
- Transportation assets
- Operational status

#### MCP Layer

Elastic MCP provides:

- Search capabilities
- Aggregation tools
- Operational updates
- Structured tool execution

---

## Core Features

### Incident Detection

Monitor active operational incidents.

### Operational Reasoning

Analyze venue conditions and resource availability.

### Asset Discovery

Identify nearby transportation and support assets.

### Mitigation Planning

Generate optimized response strategies.

### Human-In-The-Loop Approval

Require operator approval before execution.

### Automated Execution

Update operational systems after approval.

---

## Tech Stack

### AI

- Google Gemini
- Google Cloud Agent Builder

### Data

- Elasticsearch
- Elastic MCP Server

### Frontend

- Streamlit

### Backend

- Python

### Infrastructure

- Docker
- Google Cloud Run

---

## Project Structure

```text
venueiq/
│
├── app.py
├── init_elastic.py
│
├── agent/
│   ├── venue_agent.py
│   ├── planner.py
│   └── prompts.py
│
├── elastic/
│   ├── client.py
│   ├── queries.py
│   └── seed_data.py
│
├── data/
│   ├── incidents.json
│   ├── logistics.json
│   └── schedule.json
│
├── requirements.txt
└── README.md
```

---

## Local Setup

### Clone Repository

```bash
git clone https://github.com/yourusername/venueiq.git
cd venueiq
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Elasticsearch

```bash
curl -fsSL https://elastic.co/start-local | sh
```

### Seed Mock Data

```bash
python init_elastic.py
```

### Launch Dashboard

```bash
streamlit run app.py
```

---

## Demo Workflow

1. Open VenueIQ Dashboard
2. Click "Simulate Crisis"
3. Incident enters Elastic
4. Agent analyzes impact
5. Mitigation plan generated
6. Human operator reviews plan
7. Operator clicks Approve
8. VenueIQ executes reroute strategy

---

## Why VenueIQ?

Traditional monitoring platforms tell operators what happened.

VenueIQ tells them:

- What is happening
- Why it matters
- What should be done next
- Which actions should be executed

VenueIQ turns operational data into operational decisions.

---

## Future Roadmap

- Real-time GIS mapping
- Multi-stadium coordination
- Smart city integration
- Emergency services dispatch
- Fan notification systems
- Predictive incident forecasting
- Autonomous transportation orchestration

---

## Built For

Google Cloud Rapid Agent Hackathon 2026

Track:
Elastic MCP Integration

Theme:
Building Agents for Real-World Challenges

---

## License

MIT License
