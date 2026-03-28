# Hackathon Judge Q&A Prep

**1. How do you handle AI hallucinations in IR playbooks?**
We use strict system prompts enforcing JSON formatting and constrain the LLM context directly to the MITRE ATT&CK Enterprise JSON mapping. The playbooks are dynamically validated through Pydantic schemas before rendering in ReactFlow.

**2. How does this comply with RBI / CERT-In regulations regarding cloud data?**
Zero raw customer log data is ever sent to the cloud. We utilize local XGBoost/SecureBERT models for classification, while the LLM Orchestrator only receives sanitized, anonymized high-level threat telemetry to generate playbooks.

**3. Why use Gen-AI over a traditional SIEM like Splunk?**
Traditional SIEMs require analysts to manually write complex queries and manually bridge gaps between logs. AegisAI auto-correlates the logs, maps them to MITRE tactics contextually via LLMs, and replaces runbooks with dynamic, interactive workflows.

**4. How does the system handle data privacy?**
The architecture is designed for "Open Weights" (Llama-3-8B / RedSage). In a true production environment, these run entirely on-premise (e.g., via vLLM) meaning no data ever leaves the bank's internal firewalls. 

**5. How does this system scale to handle thousands of logs per second?**
We decoupled the injection payload via Apache Kafka event-streaming and handle log buffers asynchronously using FastAPI WebSockets rather than dragging down standard REST endpoints. 

**6. How accurate is your MITRE ATT&CK mapping?**
It is highly accurate because we perform Retrieval-Augmented Generation (RAG) against the official MITRE STIX JSON dataset, grounding the LLM's classification directly in established threat tactics.

**7. How do you manage the false-positive rate from the ML models?**
We engineered the XGBoost anomaly score to act as a flag, not an executioner. The AI Copilot incorporates human-in-the-loop validation, allowing SOC analysts to explicitly verify anomalies before triggering isolation nodes.

**8. Are you running this on a real or simulated network?**
For this hackathon, we use a sophisticated simulated data generator and NetworkX topologies. However, the system consumes standard JSON web logs making it trivial to pipe real Splunk/Elastic traffic into our Kafka brokers.

**9. Can you explain the ML models' decision-making (Explainable AI)?**
Yes, our Threat Alert Cards explicitly feature a "Gap Bridge Explanation" where the LLM parses the XGBoost bounds and translates *why* the packets were flagged into plain English narratives for the analyst.

**10. What is your timeline for production readiness?**
The core event-stream logic, LLM orchestrator, and React frontend are structurally complete. Production deployment simply requires mapping real internal APIs to the ReactFlow isolation nodes and swapping the mock log generators for real Kafka producers.
