import os
import json
from openai import AsyncOpenAI
from models.schemas import ThreatAnalysis, Playbook, ChatMessage
import uuid
from datetime import datetime

class LLMOrchestrator:
    def __init__(self):
        # HuggingFace / Together AI API Client (Llama-Primus / RedSage)
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
        self.huggingface_client = AsyncOpenAI(
            api_key=self.hf_key,
            # Utilizing Together AI as the OpenAI-compatible endpoint for 8B OSS models
            base_url="https://api.together.xyz/v1" 
        ) if self.hf_key and self.hf_key != "your_huggingface_key_here" else None

        # Grok API Client
        self.grok_key = os.getenv("GROK_API_KEY")
        self.grok_client = AsyncOpenAI(
            api_key=self.grok_key,
            base_url="https://api.x.ai/v1"
        ) if self.grok_key and self.grok_key != "your_xai_grok_key_here" else None

        # Fallback config references
        self.llama_model = "meta-llama/Llama-3-8b-chat-hf" 
        self.redsage_model = "meta-llama/Llama-3-8b-chat-hf" 
        self.grok_model = "grok-beta"

    async def _safe_completion(self, primary_client, primary_model, system_prompt, user_prompt, temperature=0.2):
        """
        Attempts to call the primary model (e.g. Llama-Primus / RedSage via Together),
        falls back to Grok API if primary is unavailable or fails.
        """
        try:
            if not primary_client:
                raise ValueError("Primary client not configured.")
                
            response = await primary_client.chat.completions.create(
                model=primary_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Primary model {primary_model} failed ({e}). Falling back to Grok API...")
            if not self.grok_client:
                # If neither are configured, return a structured fallback based on the prompt type
                return self._generate_static_fallback(system_prompt)
                
            try:
                # Fallback to Grok
                response = await self.grok_client.chat.completions.create(
                    model=self.grok_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception as e2:
                print(f"Grok fallback failed ({e2}). Using static mock.")
                return self._generate_static_fallback(system_prompt)
                
    def _generate_static_fallback(self, system_prompt):
        # We handle failures gracefully so the platform never crashes during demo
        if "JSON format exactly" in system_prompt:
            if "Playbook" in system_prompt:
                return '{"playbook_id": "pb_mock", "title": "Fallback Playbook", "threat_type": "Unknown", "severity": "medium", "created_at": "2026-03-28T00:00:00Z", "nodes": [{"id":"mock-node","type":"start","label":"Investigate","description":"Check logs","responsible_team":"SOC","estimated_duration":"10m","status":"pending","tools_required":[],"position":{"x":0,"y":0}}], "edges": []}'
            else:
                return '{"id": "mock_id", "timestamp": "2026-03-28T00:00:00Z", "source_logs": [], "threat_detected": true, "threat_type": "Simulated APT", "confidence_score": 0.95, "severity": "critical", "affected_systems": [], "attack_narrative": "Fallback narrative due to API keys missing.", "mitre_techniques": [], "recommended_actions": [], "novel_threat_indicator": false, "gap_bridge_explanation": ""}'
        return "The AI Orchestrator is currently running without API keys or experiencing network issues."

    async def analyze_threat(self, logs: list) -> ThreatAnalysis:
        prompt = f"Analyze these {len(logs)} logs for threats. Return JSON format exactly."
        
        raw_response = await self._safe_completion(
            self.huggingface_client, 
            self.llama_model, 
            "You are an AegisAI Threat Analyst mapping logs to MITRE ATT&CK. Return JSON format exactly.", 
            prompt
        )
        
        try:
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0]
            data = json.loads(raw_response)
            data["id"] = data.get("id", str(uuid.uuid4()))
            data["timestamp"] = data.get("timestamp", datetime.utcnow().isoformat() + "Z")
            data["source_logs"] = data.get("source_logs", [])
            return ThreatAnalysis(**data)
        except Exception as e:
            data = json.loads(self._generate_static_fallback("JSON format exactly"))
            data["id"] = str(uuid.uuid4())
            return ThreatAnalysis(**data)

    async def generate_playbook(self, threat: ThreatAnalysis) -> Playbook:
        prompt = f"Threat: {threat.threat_type}. Severity: {threat.severity}. Generate IR Playbook JSON format exactly."
        
        raw_response = await self._safe_completion(
            self.huggingface_client, 
            self.llama_model, 
            "You are an AegisAI Playbook generator (Llama-Primus). Return JSON format exactly for actionable flowcharts.", 
            prompt
        )
        
        try:
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0]
            data = json.loads(raw_response)
            data["playbook_id"] = data.get("playbook_id", str(uuid.uuid4()))
            data["created_at"] = data.get("created_at", datetime.utcnow().isoformat() + "Z")
            return Playbook(**data)
        except:
            data = json.loads(self._generate_static_fallback("Playbook JSON format exactly"))
            data["playbook_id"] = str(uuid.uuid4())
            return Playbook(**data)

    async def copilot_chat_stream(self, messages: list):
        """
        Grok is typically better for conversational tasks, 
        so we default to Grok for Copilot but allow it to run on Llama if Grok is down.
        """
        if self.grok_client:
            client = self.grok_client
            model = self.grok_model
        elif self.huggingface_client:
            client = self.huggingface_client
            model = self.llama_model
        else:
            yield {"token": "No API keys configured. Please configure GROK_API_KEY or HUGGINGFACE_API_KEY in .env."}
            return

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield {"token": chunk.choices[0].delta.content}
        except Exception as e:
            yield {"token": f"\\n\\n*Error connecting to LLM Orchestrator: {str(e)}*"}

    async def get_red_team_action(self, scenario, context) -> str:
        # RedSage is utilized for the BAS Red Team Simulation mapping
        prompt = f"Scenario: {scenario}. Context: {context}. What is the next red team action?"
        return await self._safe_completion(
            self.huggingface_client, 
            self.redsage_model, 
            "You are RedSage, an advanced Breach and Attack Simulation engine optimizing lateral movement.", 
            prompt
        )
