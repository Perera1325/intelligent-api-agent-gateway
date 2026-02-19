🚀 Intelligent API Agent Gateway



A production-style microservices architecture that transforms traditional APIs into an intelligent, resilient AI-driven orchestration layer.



🧠 Core Concept



Instead of manually calling multiple APIs, a single AI Agent:



Calls Weather API



Calls Traffic API



Calls Fleet API



Applies intelligent decision logic



Returns contextualized, explainable recommendations



🏗 Architecture

Client

&nbsp;  ↓

AI Agent (Port 5004)

&nbsp;  ↓

Weather (5001)

Traffic (5002)

Fleet (5003)



🔐 Features



API Key Authentication



Service Registry Pattern



Retry + Timeout Handling



Partial Failure Tolerance



Health Check Endpoints



Caching Layer (TTL-based)



Metrics Endpoint



Structured Logging



Explainable Decision Output



🧪 Example Request

curl -H "x-api-key: vinod-secure-key" \\

"http://localhost:5004/agent/optimize-delivery?city=Colombo\&capacity=1000"



📊 Metrics Endpoint

GET /metrics





Tracks:



Total Requests



Cache Hits



Agent Executions



🏥 Health Endpoints

/health (available on all backend services)



🔮 Future Improvements



Circuit Breaker Pattern



Docker Containerization



Integration with WSO2 API Manager



LLM-based dynamic reasoning



Frontend Dashboard



Prometheus + Grafana monitoring

