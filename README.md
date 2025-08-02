# Turkish Call-Center Agent for TEKNOFEST NLP Competition 2025

## Project Structure

```
callcenter-agent-teknofest/
├─ frontend/                    # Next.js 14 UI (mic recording, transcript, playback)
│
├─ backend/                     # Core FastAPI app + agent logic
│  ├─ app/
│  │   ├─ main.py               # WS gateway  /stream
│  │   ├─ stream_manager.py     # cancel / resume per call
│  │   ├─ metrics.py            # fire-and-forget KPI events
│  │   └─ metrics_worker.py     # async aggregation → Parquet
│  │
│  ├─ agents/                   # Agentic Framework (LangGraph / Agno)
│  │   ├─ router_agent.py       # optional router agent
│  │   └─ package_change/       # example scenario
│  │        ├─ agent.py
│  │        ├─ tools.py
│  │        └─ prompt.py
│  │
│  ├─ clients/                  # thin REST callers
│  │   ├─ stt_client.py         # POST /transcribe -> text
│  │   └─ tts_client.py         # POST /synthesize -> wav
│  │
│  └─ mock_db/                  # demo data for telco tools
│      └─ users.json
│
├─ services/                    # self-contained micro-services
│  ├─ stt/                      # Whisper REST wrapper
│  │   ├─ Dockerfile
│  │   ├─ server.py             # FastAPI  POST /transcribe
│  │   └─ requirements.txt
│  ├─ tts/                      # XTTS / Piper wrapper
│  │   ├─ Dockerfile
│  │   ├─ server.py             # FastAPI  POST /synthesize
│  │   └─ requirements.txt
│  └─ llm/                      # (optional) local vLLM server
│      └─ docker-compose.yml
│
├─ docs/
│  ├─ architecture.drawio
│  └─ kpi.md
│
└─ docker-compose.yml           # stitches api + services
 
        


```

## TL;DR

- **frontend/** – pure Next.js, talks WebSocket.
- **services/** – three swappable containers: STT, TTS, optional LLM.
- **backend/app/** – FastAPI gateway, stream control, KPI logging.
- **agents/** – modular scenario graphs; each owns its tools & prompts.
- **infra/docker-compose.yml** – docker-compose up launches a full local stack.

Set endpoints in .env to switch between local containers and remote SaaS without touching code. KPIs flush to metrics/telemetry.parquet for easy reporting.
