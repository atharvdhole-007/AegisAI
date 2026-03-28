"""
CyberSentinel AI — Mock Data Generator
Simulates a banking Security Operations Center (SOC) with realistic log generation.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from models.schemas import EventType, LogEntry, SeverityLevel


class MockLogGenerator:
    """Generates realistic banking security logs for demonstration purposes."""

    # Realistic IP ranges
    INTERNAL_IPS = [
        "10.0.1.10", "10.0.1.20", "10.0.1.35", "10.0.2.10", "10.0.2.20",
        "10.0.3.15", "10.0.3.22", "10.0.3.45", "10.0.3.100", "10.0.4.5",
    ]
    EXTERNAL_IPS = [
        "185.220.101.34", "91.219.236.78", "45.155.205.99", "23.129.64.210",
        "103.75.201.15", "192.42.116.200", "162.247.74.27", "198.98.56.12",
        "77.247.181.165", "209.141.58.100",
    ]
    SUSPICIOUS_IPS = [
        "185.220.101.34", "91.219.236.78", "45.155.205.99", "103.75.201.15",
    ]
    EMPLOYEE_NAMES = [
        "j.smith", "r.patel", "m.johnson", "a.williams", "s.chen",
        "d.garcia", "k.taylor", "l.martinez", "n.anderson", "p.thomas",
    ]
    COUNTRIES = [
        "US", "UK", "DE", "IN", "CN", "RU", "BR", "JP", "AU", "NG",
    ]

    def __init__(self) -> None:
        self.log_buffer: list[LogEntry] = []
        self.max_buffer_size = 500

    def _now_iso(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _random_timestamp_recent(self, seconds_back: int = 60) -> str:
        t = datetime.utcnow() - timedelta(seconds=random.randint(0, seconds_back))
        return t.isoformat() + "Z"

    # ─── Background Log Generators ────────────────────────────────────────

    def _generate_firewall_log(self) -> LogEntry:
        action = random.choice(["ALLOWED", "ALLOWED", "ALLOWED", "BLOCKED"])
        src = random.choice(self.EXTERNAL_IPS + self.INTERNAL_IPS)
        dst = random.choice(self.INTERNAL_IPS)
        port = random.choice([22, 80, 443, 3389, 8080, 1433, 3306, 5432])
        severity = SeverityLevel.LOW if action == "ALLOWED" else SeverityLevel.MEDIUM

        return LogEntry(
            timestamp=self._now_iso(),
            source_ip=src,
            event_type=EventType.FIREWALL,
            severity=severity,
            raw_message=f"Firewall {action} connection from {src} to {dst}:{port} proto=TCP",
            metadata={
                "action": action,
                "destination_ip": dst,
                "destination_port": port,
                "protocol": "TCP",
                "rule_id": f"FW-{random.randint(1000, 9999)}",
                "bytes_transferred": random.randint(64, 15000),
            },
        )

    def _generate_auth_log(self) -> LogEntry:
        user = random.choice(self.EMPLOYEE_NAMES)
        success = random.random() > 0.15
        src = random.choice(self.INTERNAL_IPS + self.EXTERNAL_IPS[:3])
        severity = SeverityLevel.LOW if success else SeverityLevel.MEDIUM

        status = "SUCCESS" if success else "FAILED"
        return LogEntry(
            timestamp=self._now_iso(),
            source_ip=src,
            event_type=EventType.AUTHENTICATION,
            severity=severity,
            raw_message=f"Authentication {status} for user '{user}' from {src} via SSO portal",
            metadata={
                "username": user,
                "auth_method": random.choice(["SSO", "MFA", "Password", "Certificate"]),
                "status": status,
                "geo_location": random.choice(self.COUNTRIES[:5]),
                "device_type": random.choice(["workstation", "laptop", "mobile"]),
                "session_id": str(uuid.uuid4())[:8],
            },
        )

    def _generate_transaction_log(self) -> LogEntry:
        amount = round(random.uniform(50, 25000), 2)
        user = random.choice(self.EMPLOYEE_NAMES)
        severity = SeverityLevel.LOW if amount < 10000 else SeverityLevel.MEDIUM

        return LogEntry(
            timestamp=self._now_iso(),
            source_ip=random.choice(self.INTERNAL_IPS),
            event_type=EventType.TRANSACTION,
            severity=severity,
            raw_message=f"Wire transfer ${amount:,.2f} initiated by {user} to account ending ****{random.randint(1000, 9999)}",
            metadata={
                "amount": amount,
                "currency": "USD",
                "initiated_by": user,
                "recipient_bank": random.choice(["Chase", "Wells Fargo", "HSBC", "Deutsche Bank", "Unknown Foreign Bank"]),
                "recipient_account": f"****{random.randint(1000, 9999)}",
                "transaction_type": random.choice(["wire", "ACH", "internal_transfer"]),
                "approval_status": random.choice(["auto_approved", "pending_review"]),
            },
        )

    def _generate_endpoint_log(self) -> LogEntry:
        processes = ["svchost.exe", "chrome.exe", "outlook.exe", "powershell.exe", "cmd.exe", "explorer.exe"]
        process = random.choice(processes)
        host = f"WKS-{random.randint(100, 999)}"
        severity = SeverityLevel.LOW if process not in ["powershell.exe", "cmd.exe"] else SeverityLevel.MEDIUM

        return LogEntry(
            timestamp=self._now_iso(),
            source_ip=random.choice(self.INTERNAL_IPS),
            event_type=EventType.ENDPOINT,
            severity=severity,
            raw_message=f"Process '{process}' started on {host} by user {random.choice(self.EMPLOYEE_NAMES)}",
            metadata={
                "hostname": host,
                "process_name": process,
                "pid": random.randint(1000, 65535),
                "parent_process": random.choice(["explorer.exe", "services.exe", "winlogon.exe"]),
                "command_line": f"C:\\Windows\\System32\\{process}",
                "file_hash": uuid.uuid4().hex[:16],
            },
        )

    def _generate_network_anomaly_log(self) -> LogEntry:
        anomaly_types = ["port_scan_detected", "dns_query_spike", "unusual_traffic_volume", "beacon_pattern"]
        anomaly = random.choice(anomaly_types)
        src = random.choice(self.INTERNAL_IPS)
        severity = SeverityLevel.MEDIUM

        return LogEntry(
            timestamp=self._now_iso(),
            source_ip=src,
            event_type=EventType.NETWORK_ANOMALY,
            severity=severity,
            raw_message=f"Network anomaly '{anomaly}' detected from {src} — {random.randint(50, 500)} events in 60s window",
            metadata={
                "anomaly_type": anomaly,
                "event_count": random.randint(50, 500),
                "time_window_seconds": 60,
                "destination_ips": random.sample(self.EXTERNAL_IPS, k=min(3, len(self.EXTERNAL_IPS))),
                "protocols": random.sample(["TCP", "UDP", "ICMP", "DNS"], k=2),
                "baseline_deviation_percent": round(random.uniform(150, 800), 1),
            },
        )

    def generate_background_logs(self, count: int = 20) -> list[LogEntry]:
        """Generate a batch of random normal background logs."""
        generators = [
            self._generate_firewall_log,
            self._generate_auth_log,
            self._generate_transaction_log,
            self._generate_endpoint_log,
            self._generate_network_anomaly_log,
        ]
        logs = [random.choice(generators)() for _ in range(count)]
        self._add_to_buffer(logs)
        return logs

    # ─── Attack Scenario Injection ────────────────────────────────────────

    def inject_scenario(self, scenario: str) -> list[LogEntry]:
        """Inject a predefined attack scenario into the log stream."""
        scenario_map = {
            "credential_stuffing": self._scenario_credential_stuffing,
            "ransomware_early": self._scenario_ransomware_early,
            "data_exfiltration": self._scenario_data_exfiltration,
            "insider_threat": self._scenario_insider_threat,
            "apt_lateral_movement": self._scenario_apt_lateral_movement,
        }
        generator = scenario_map.get(scenario)
        if generator is None:
            return []
        logs = generator()
        self._add_to_buffer(logs)
        return logs

    def _scenario_credential_stuffing(self) -> list[LogEntry]:
        """50 failed logins in 30 seconds from rotating IPs."""
        logs: list[LogEntry] = []
        target_user = "admin.treasury"
        rotating_ips = self.SUSPICIOUS_IPS + [f"45.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(10)]

        for i in range(50):
            t = datetime.utcnow() - timedelta(seconds=random.randint(0, 30))
            logs.append(LogEntry(
                timestamp=t.isoformat() + "Z",
                source_ip=random.choice(rotating_ips),
                event_type=EventType.AUTHENTICATION,
                severity=SeverityLevel.HIGH,
                raw_message=f"Authentication FAILED for user '{target_user}' from {random.choice(rotating_ips)} — attempt {i + 1} — invalid credentials",
                metadata={
                    "username": target_user,
                    "auth_method": "Password",
                    "status": "FAILED",
                    "geo_location": random.choice(["RU", "CN", "NG", "BR", "KP"]),
                    "failure_reason": "invalid_credentials",
                    "attempt_number": i + 1,
                    "device_type": "unknown",
                    "session_id": str(uuid.uuid4())[:8],
                },
            ))

        # A few successful attempts interspersed to simulate credential stuffing
        logs.append(LogEntry(
            timestamp=self._now_iso(),
            source_ip=random.choice(rotating_ips),
            event_type=EventType.AUTHENTICATION,
            severity=SeverityLevel.CRITICAL,
            raw_message=f"Authentication SUCCESS for user '{target_user}' from suspicious IP after 50 failed attempts",
            metadata={
                "username": target_user,
                "auth_method": "Password",
                "status": "SUCCESS",
                "geo_location": "RU",
                "device_type": "unknown",
                "session_id": str(uuid.uuid4())[:8],
                "risk_flag": "post_brute_force_success",
            },
        ))
        return logs

    def _scenario_ransomware_early(self) -> list[LogEntry]:
        """Process creates shadow copy deletion commands."""
        logs: list[LogEntry] = []
        compromised_host = "WKS-342"
        src_ip = "10.0.3.45"

        commands = [
            "vssadmin.exe delete shadows /all /quiet",
            "wmic shadowcopy delete",
            "bcdedit /set {default} recoveryenabled no",
            "bcdedit /set {default} bootstatuspolicy ignoreallfailures",
            "wbadmin delete catalog -quiet",
            "powershell.exe -enc UwB0AGEAcgB0AC0AUwBsAGUAZQBwACAALQBzACAAMwA=",
        ]

        for i, cmd in enumerate(commands):
            t = datetime.utcnow() - timedelta(seconds=len(commands) - i)
            logs.append(LogEntry(
                timestamp=t.isoformat() + "Z",
                source_ip=src_ip,
                event_type=EventType.ENDPOINT,
                severity=SeverityLevel.CRITICAL,
                raw_message=f"Suspicious process execution on {compromised_host}: {cmd}",
                metadata={
                    "hostname": compromised_host,
                    "process_name": cmd.split()[0],
                    "command_line": cmd,
                    "pid": random.randint(1000, 65535),
                    "parent_process": "cmd.exe",
                    "user": "SYSTEM",
                    "file_hash": uuid.uuid4().hex[:16],
                    "threat_indicator": "shadow_copy_deletion",
                },
            ))

        # File encryption activity
        for i in range(10):
            logs.append(LogEntry(
                timestamp=self._now_iso(),
                source_ip=src_ip,
                event_type=EventType.ENDPOINT,
                severity=SeverityLevel.CRITICAL,
                raw_message=f"File system change on {compromised_host}: C:\\Users\\Public\\Documents\\report_{i}.docx.encrypted — file extension changed to .encrypted",
                metadata={
                    "hostname": compromised_host,
                    "file_path": f"C:\\Users\\Public\\Documents\\report_{i}.docx.encrypted",
                    "original_extension": ".docx",
                    "new_extension": ".encrypted",
                    "operation": "rename",
                    "threat_indicator": "ransomware_encryption",
                },
            ))
        return logs

    def _scenario_data_exfiltration(self) -> list[LogEntry]:
        """Large outbound data transfer to unknown external IP."""
        logs: list[LogEntry] = []
        exfil_ip = "185.220.101.34"
        src_ip = "10.0.2.20"  # database server

        # DNS queries to suspicious domain
        for i in range(5):
            logs.append(LogEntry(
                timestamp=self._random_timestamp_recent(120),
                source_ip=src_ip,
                event_type=EventType.NETWORK_ANOMALY,
                severity=SeverityLevel.HIGH,
                raw_message=f"DNS query from {src_ip} to suspicious domain: data-sync-{random.randint(100,999)}.darkcloud.io",
                metadata={
                    "anomaly_type": "suspicious_dns",
                    "domain": f"data-sync-{random.randint(100,999)}.darkcloud.io",
                    "query_type": "A",
                    "resolved_ip": exfil_ip,
                },
            ))

        # Large data transfers
        for i in range(8):
            size_mb = round(random.uniform(50, 500), 1)
            logs.append(LogEntry(
                timestamp=self._random_timestamp_recent(60),
                source_ip=src_ip,
                event_type=EventType.FIREWALL,
                severity=SeverityLevel.CRITICAL,
                raw_message=f"Large outbound transfer: {size_mb}MB from {src_ip} to {exfil_ip}:443 — exceeds baseline by 4000%",
                metadata={
                    "action": "ALLOWED",
                    "destination_ip": exfil_ip,
                    "destination_port": 443,
                    "protocol": "TCP",
                    "bytes_transferred": int(size_mb * 1024 * 1024),
                    "baseline_deviation_percent": round(random.uniform(3000, 5000), 1),
                    "threat_indicator": "data_exfiltration",
                    "destination_geo": "Unknown",
                },
            ))
        return logs

    def _scenario_insider_threat(self) -> list[LogEntry]:
        """After-hours bulk download of customer records."""
        logs: list[LogEntry] = []
        insider = "r.patel"
        src_ip = "10.0.3.22"

        # After-hours login
        logs.append(LogEntry(
            timestamp=self._now_iso(),
            source_ip=src_ip,
            event_type=EventType.AUTHENTICATION,
            severity=SeverityLevel.HIGH,
            raw_message=f"After-hours authentication SUCCESS for '{insider}' at 02:34 AM local time — outside normal working hours",
            metadata={
                "username": insider,
                "auth_method": "Password",
                "status": "SUCCESS",
                "local_time": "02:34:00",
                "normal_hours": "08:00-18:00",
                "geo_location": "US",
                "risk_flag": "after_hours_access",
            },
        ))

        # Bulk database queries
        tables = ["customer_records", "account_balances", "ssn_data", "credit_scores", "transaction_history"]
        for table in tables:
            rows = random.randint(10000, 500000)
            logs.append(LogEntry(
                timestamp=self._now_iso(),
                source_ip=src_ip,
                event_type=EventType.TRANSACTION,
                severity=SeverityLevel.CRITICAL,
                raw_message=f"Bulk SELECT query by '{insider}' on {table}: {rows:,} rows exported to CSV at 02:35 AM",
                metadata={
                    "username": insider,
                    "query_type": "SELECT",
                    "table_name": table,
                    "rows_returned": rows,
                    "export_format": "CSV",
                    "data_classification": "PII" if table in ["ssn_data", "customer_records"] else "Confidential",
                    "threat_indicator": "bulk_data_access",
                },
            ))

        # USB device connected
        logs.append(LogEntry(
            timestamp=self._now_iso(),
            source_ip=src_ip,
            event_type=EventType.ENDPOINT,
            severity=SeverityLevel.CRITICAL,
            raw_message=f"USB storage device connected on {insider}'s workstation WKS-122 — 64GB SanDisk — policy violation",
            metadata={
                "hostname": "WKS-122",
                "device_type": "USB_STORAGE",
                "device_name": "SanDisk Ultra 64GB",
                "username": insider,
                "policy_violation": True,
                "threat_indicator": "data_theft_attempt",
            },
        ))
        return logs

    def _scenario_apt_lateral_movement(self) -> list[LogEntry]:
        """Compromised host scanning internal subnets."""
        logs: list[LogEntry] = []
        compromised = "10.0.3.100"

        # Initial compromise via phishing
        logs.append(LogEntry(
            timestamp=self._random_timestamp_recent(300),
            source_ip=compromised,
            event_type=EventType.ENDPOINT,
            severity=SeverityLevel.HIGH,
            raw_message=f"Suspicious macro execution in invoice_Q4_2024.xlsm on WKS-587 — dropper detected",
            metadata={
                "hostname": "WKS-587",
                "process_name": "EXCEL.EXE",
                "child_process": "powershell.exe",
                "command_line": "powershell.exe -WindowStyle Hidden -ep bypass -file C:\\Users\\Public\\update.ps1",
                "file_name": "invoice_Q4_2024.xlsm",
                "threat_indicator": "macro_dropper",
            },
        ))

        # Port scanning
        scanned_hosts = ["10.0.2.10", "10.0.2.20", "10.0.1.10", "10.0.1.20", "10.0.4.5"]
        for target in scanned_hosts:
            ports = random.sample([22, 80, 135, 139, 443, 445, 1433, 3306, 3389, 5432, 8080], k=5)
            logs.append(LogEntry(
                timestamp=self._random_timestamp_recent(180),
                source_ip=compromised,
                event_type=EventType.NETWORK_ANOMALY,
                severity=SeverityLevel.HIGH,
                raw_message=f"Port scan detected from {compromised} to {target} — {len(ports)} ports probed in 5s",
                metadata={
                    "anomaly_type": "port_scan_detected",
                    "target_ip": target,
                    "ports_scanned": ports,
                    "scan_duration_seconds": 5,
                    "packets_sent": random.randint(50, 200),
                },
            ))

        # Lateral movement attempts
        logs.append(LogEntry(
            timestamp=self._random_timestamp_recent(60),
            source_ip=compromised,
            event_type=EventType.AUTHENTICATION,
            severity=SeverityLevel.CRITICAL,
            raw_message=f"Pass-the-hash authentication attempt from {compromised} to 10.0.2.10 (Core Banking Server) using harvested NTLM hash",
            metadata={
                "username": "svc_banking",
                "auth_method": "NTLM",
                "status": "SUCCESS",
                "source_host": "WKS-587",
                "target_host": "CORE-BANKING-01",
                "target_ip": "10.0.2.10",
                "threat_indicator": "lateral_movement",
                "technique": "T1550.002 — Pass the Hash",
            },
        ))

        # C2 beaconing
        for i in range(6):
            logs.append(LogEntry(
                timestamp=self._random_timestamp_recent(300),
                source_ip=compromised,
                event_type=EventType.NETWORK_ANOMALY,
                severity=SeverityLevel.HIGH,
                raw_message=f"C2 beacon pattern detected: {compromised} → 91.219.236.78:443 — regular 60s interval, encrypted payload",
                metadata={
                    "anomaly_type": "beacon_pattern",
                    "c2_server": "91.219.236.78",
                    "beacon_interval_seconds": 60,
                    "jitter_percent": random.randint(5, 15),
                    "payload_size_bytes": random.randint(128, 512),
                    "encryption": "TLS 1.3",
                    "threat_indicator": "c2_communication",
                },
            ))
        return logs

    # ─── Buffer Management ────────────────────────────────────────────────

    def _add_to_buffer(self, logs: list[LogEntry]) -> None:
        self.log_buffer.extend(logs)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]

    def get_recent_logs(self, count: int = 50) -> list[LogEntry]:
        """Return the most recent logs from the buffer."""
        return self.log_buffer[-count:]

    def get_logs_since(self, seconds: int = 30) -> list[LogEntry]:
        """Return logs from the last N seconds."""
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        cutoff_str = cutoff.isoformat() + "Z"
        return [log for log in self.log_buffer if log.timestamp >= cutoff_str]


# Global instance
log_generator = MockLogGenerator()
