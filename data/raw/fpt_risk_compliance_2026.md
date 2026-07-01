# FPT Software Risk Management, Compliance & Security Standards (2025–2026)

## 1. FPT Secure-First Development Framework
FPT Software enforces a "Secure-First" approach across all development projects:

### 1.1 DevSecOps Integration
*   Static Application Security Testing (SAST): Embedded in all CI/CD pipelines using SonarQube and Checkmarx.
*   Dynamic Application Security Testing (DAST): OWASP ZAP scans on every staging deployment.
*   Software Composition Analysis (SCA): Snyk or Black Duck for third-party library vulnerability tracking.
*   Container Security: Trivy image scanning in Docker build pipelines; no HIGH or CRITICAL CVEs allowed in production.

### 1.2 OWASP Compliance Standards
All FPT Software applications are tested against OWASP Top 10 (2021) and OWASP API Security Top 10:
*   A01 - Broken Access Control: Role-based access control (RBAC) with principle of least privilege.
*   A02 - Cryptographic Failures: TLS 1.3 mandatory; AES-256-GCM for data at rest; no MD5/SHA-1.
*   A03 - Injection: Parameterized queries enforced; input validation via allowlists.
*   A09 - Security Logging & Monitoring: Centralized SIEM with anomaly detection and real-time alerting.

---

## 2. Risk Assessment Framework
FPT Software uses a structured risk assessment methodology with the following dimensions:

### 2.1 Risk Matrix Categories
*   **Technical Risks:** Technology obsolescence, architectural coupling, vendor lock-in, data migration complexity.
*   **Security Risks:** Data breach exposure, authentication weaknesses, privilege escalation, supply chain attacks.
*   **Compliance Risks:** GDPR violations, PCI DSS gaps, HIPAA non-compliance, local data sovereignty requirements.
*   **Operational Risks:** Single points of failure, disaster recovery RTO/RPO breaches, staff knowledge concentration.
*   **Financial Risks:** TCO overruns, hidden licensing costs, cloud cost unpredictability.

### 2.2 Risk Scoring
Each risk is scored by Likelihood (1–5) × Impact (1–5) = Risk Score (1–25):
*   1–5: Low — Monitor quarterly.
*   6–12: Medium — Mitigate within current sprint.
*   13–19: High — Immediate mitigation plan required.
*   20–25: Critical — Escalate to CTO/CISO; block deployment.

---

## 3. Key Compliance Standards Supported
*   **GDPR (EU):** Data minimization, right-to-erasure, data breach notification within 72 hours.
*   **PCI DSS v4.0:** Cardholder data environment segmentation, tokenization, quarterly ASV scans.
*   **HIPAA (US):** PHI encryption, audit logging, BAA agreements, role-based access control.
*   **ISO 27001:** Information security management system — FPT Software certified.
*   **SOC 2 Type II:** Annual audit for security, availability, and confidentiality for cloud services.
*   **ISO 26262 (Automotive):** Functional safety for embedded automotive software (ASIL-B to ASIL-D).
*   Source: FPT Software Compliance & Risk Framework (2025)

---

## 4. Business Continuity & Disaster Recovery (BC/DR)
*   **Recovery Time Objective (RTO):** Target < 4 hours for Tier 1 systems; < 24 hours for Tier 2.
*   **Recovery Point Objective (RPO):** Target < 1 hour for critical financial systems; < 4 hours for standard systems.
*   **Backup Strategy:** 3-2-1 rule (3 copies, 2 media types, 1 off-site); cross-region replication for cloud workloads.
*   **Failover Testing:** Mandatory quarterly disaster recovery drills with documented results.
*   Source: FPT Software BC/DR Policy (2025)
