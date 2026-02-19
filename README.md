Intelligent API Agent Gateway

From Traditional APIs to Intelligent Agents

Overview

This project is a working prototype that demonstrates how traditional API-based integrations can evolve into intelligent, decision-making agents.

Inspired by the architectural vision of APIs transforming into AI-powered agents, this system goes beyond simple data aggregation. Instead of returning raw API responses, the agent interprets, contextualizes, and synthesizes data from multiple backend services to produce actionable decisions.

The goal of this project is to model the transition from deterministic API orchestration to intelligent orchestration — a foundational concept in the evolution of digital ecosystems.

Architectural Vision

Traditional API architectures focus on:

Data exchange

Request/response communication

Deterministic integration

This project introduces an additional layer:

Contextual reasoning

Decision synthesis

Fault-aware orchestration

Adaptive service handling

Rather than acting as a gateway, the AI Agent acts as an orchestrator that:

Combines weather, traffic, and fleet data

Applies contextual business logic

Produces operational decisions

Handles partial failures intelligently

This reflects the shift from APIs as contracts to agents as problem-solvers.

System Architecture

The system consists of four independent services:

Weather Service (Port 5001)

Traffic Service (Port 5002)

Fleet Service (Port 5003)

AI Agent Orchestrator (Port 5004)

The AI Agent:

Discovers services via a service registry

Calls backend APIs

Applies retry and timeout mechanisms

Implements circuit breaker protection

Caches responses

Produces contextual delivery decisions

The architecture follows microservices principles with clear service boundaries and independent runtime environments.

Key Features
Intelligent Orchestration

The agent does not simply aggregate responses. It analyzes:

Traffic congestion levels

Weather conditions

Fleet capacity availability

It then produces a structured decision:

Proceed with delivery

Delay delivery

Delivery not possible

Along with an explanation of reasoning.

Circuit Breaker Pattern

To prevent cascading failures:

Services are monitored for repeated failures

After a threshold, the circuit opens

Calls are temporarily blocked

Recovery is attempted after cooldown

This models resilience patterns used in enterprise API platforms.

Retry and Timeout Handling

Each service call includes:

Configurable retry attempts

Timeout protection

Graceful degradation

If one service fails, the system continues operating with partial data.

In-Memory Caching

To improve performance:

Responses are cached for a configurable TTL

Repeated identical requests are served from cache

Cache hits are tracked in metrics

Metrics and Observability

The agent exposes:

Total request count

Cache hits

Agent execution count

Circuit breaker state

This enables basic observability and runtime monitoring.

Dashboard Interface

A lightweight web dashboard provides:

Metrics visualization

Circuit breaker status

Health monitoring

Real-time delivery optimization testing

The dashboard demonstrates how intelligent agents can be made accessible to end users and product teams.

How This Relates to API Evolution

Traditional API management focuses on:

Security

Rate limiting

Monetization

Governance

This prototype explores the next layer:

Agents that consume APIs

Agents that interpret and enrich API responses

Agents that orchestrate workflows dynamically

Agents that provide reasoning outputs instead of raw data

This hybrid model suggests a future where:

APIs remain deterministic foundations

Intelligent agents operate as orchestration layers

API gateways evolve to support both models

Running the Project
Option 1: Manual (4 Terminals)

Start each backend service:

Weather Service:

cd backend-apis/weather-service
python -m venv venv
source venv/Scripts/activate
pip install Flask requests
python app.py


Traffic Service:

cd backend-apis/traffic-service
python -m venv venv
source venv/Scripts/activate
pip install Flask requests
python app.py


Fleet Service:

cd backend-apis/fleet-service
python -m venv venv
source venv/Scripts/activate
pip install Flask requests
python app.py


AI Agent:

cd ai-agent
python -m venv venv
source venv/Scripts/activate
pip install Flask requests
python app.py


Access the dashboard at:

http://localhost:5004/dashboard

Option 2: Docker
docker-compose up --build


This runs all services in isolated containers.

Example API Call
curl -H "x-api-key: vinod-secure-key" \
"http://localhost:5004/agent/optimize-delivery?city=Colombo&capacity=1000"


Response includes:

Weather data

Traffic data

Fleet availability

Agent decision

Decision explanation

Future Enhancements

This prototype can be extended with:

LLM-based reasoning engines

Persistent storage

API gateway integration

Authentication and token management

Distributed tracing

Agent marketplace model

WSO2 API Manager integration

Purpose of This Project

This is not just a CRUD microservice demo.

It is a practical exploration of:

Intelligent API orchestration

Resilient distributed systems

Hybrid API-agent ecosystems

The next generation of API management models

It demonstrates how APIs can evolve from static data providers into intelligent, adaptive agents that actively participate in decision-making.

Author

Vinod Perera
Computer Science & Electrical Engineering Undergraduate
GitHub: https://github.com/Perera1325

