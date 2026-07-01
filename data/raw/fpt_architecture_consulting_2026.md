# FPT Software Architecture Consulting & Technical Standards (2025–2026)

## 1. Recommended Architecture Patterns

### 1.1 Microservices Architecture
FPT Software recommends microservices for enterprise-scale digital transformation projects:
*   **Best For:** High-scale applications requiring independent scaling, fault isolation, and polyglot technology stacks.
*   **FPT Implementation Approach:**
  *   Domain-Driven Design (DDD) for service boundary definition.
  *   API Gateway pattern (Kong, AWS API Gateway) for traffic management.
  *   Saga pattern for distributed transaction management.
  *   Service mesh (Istio) for observability and zero-trust networking.
*   **Tradeoffs:** Higher operational complexity; requires mature DevOps culture and container orchestration (Kubernetes).

### 1.2 Event-Driven Architecture (EDA)
*   **Best For:** Real-time data pipelines, decoupled microservices, and audit-trail systems.
*   **Tech Stack:** Apache Kafka, AWS EventBridge, or Azure Service Bus.
*   **Patterns Used:** CQRS (Command Query Responsibility Segregation), Event Sourcing, Outbox Pattern.

### 1.3 Serverless Architecture
*   **Best For:** Variable workloads, rapid prototyping, and event-triggered processing.
*   **Provider Options:** AWS Lambda, Azure Functions, Google Cloud Functions.
*   **FPT Guidance:** Avoid serverless for latency-sensitive, CPU-heavy AI workloads; prefer GPU-backed containers.

### 1.4 RAG (Retrieval-Augmented Generation) Architecture
*   **Best For:** Enterprise Q&A systems, knowledge base search, document intelligence.
*   **FPT RAG Stack:**
  *   Embedding model: sentence-transformers (all-MiniLM-L6-v2 or paraphrase-multilingual)
  *   Vector store: ChromaDB (development), Pinecone or Weaviate (production)
  *   Sparse retrieval: BM25 for keyword matching
  *   Hybrid fusion: Reciprocal Rank Fusion (RRF) for combining dense and sparse results
  *   Reranking: Cross-encoder reranker for precision improvement

---

## 2. Cloud Architecture Strategy

### 2.1 Multi-Cloud Approach
FPT Software advises enterprise clients on multi-cloud strategies to avoid vendor lock-in:
*   **Primary Clouds:** AWS (preferred for global scale), Azure (preferred for Microsoft-integrated enterprises), GCP (preferred for AI/ML workloads).
*   **Recommendation:** Use cloud-agnostic Kubernetes workloads with Terraform IaC for portability.

### 2.2 Cloud-Native Security
*   Zero-Trust Network Access (ZTNA) across all service-to-service communications.
*   Secrets management via HashiCorp Vault or AWS Secrets Manager.
*   Regular DAST and SAST scanning in CI/CD pipelines.
*   OWASP Top 10 automated scanning in every merge request pipeline.

---

## 3. Database Architecture Recommendations

### 3.1 Core Banking Systems
*   **Primary DB:** Oracle Database or PostgreSQL with high availability (HA) clustering.
*   **Caching Layer:** Redis Cluster for session data and hot reads (sub-1ms latency).
*   **Sharding Strategy:** Consistent hashing for horizontal scaling beyond single-node limits.
*   **Compliance:** PCI DSS v4.0 column-level encryption for cardholder data.

### 3.2 AI-Native Data Stacks
*   **Feature Store:** Feast (open-source) or Tecton (managed) for ML feature management.
*   **Data Lake:** Delta Lake or Apache Iceberg on cloud object storage (S3/GCS/ADLS).
*   **Streaming:** Apache Flink for real-time feature computation.

---

## 4. Coding Standards & Quality Gates
FPT Software enforces the following quality standards across all projects:
*   **Test Coverage Minimum:** 80% unit test coverage; 60% integration test coverage.
*   **Code Review:** All pull requests require at least 2 approvals from senior engineers.
*   **Static Analysis:** SonarQube analysis; no Critical or Blocker issues merged.
*   **Security Scanning:** Snyk or Checkmarx for dependency vulnerability scanning.
*   **Performance:** API response times under 200ms (p99) for synchronous endpoints.
*   **Documentation:** All public APIs must have OpenAPI 3.0 specification.
*   Source: FPT Software Engineering Excellence Standards (2025)
