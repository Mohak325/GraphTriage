"""
5G Core PCAP & Wireshark JSON Trace Loader
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Reference: Paper 11 (Golden Flow - Isaac et al. / Jarrah et al., 2024/2025)
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PcapFrame:
    frame_number: int
    timestamp: float
    source_ip: str
    dest_ip: str
    protocol: str  # NGAP, NAS-5GS, HTTP2
    procedure: str  # Registration, PDU_Session_Establishment, Deregistration
    message_type: str  # RegistrationRequest, RegistrationAccept, RegistrationReject, etc.
    status_code: Optional[int] = None
    cause_code: Optional[str] = None
    delta_time_ms: float = 0.0


def create_synthetic_5gc_pcap(
    fault_scenario: Optional[str] = "registration_congestion"
) -> List[PcapFrame]:
    """
    Creates a canonical 3GPP 5G Core control-plane signaling trace.
    If `fault_scenario` is 'registration_congestion', injects a failure at Frame 23.
    """
    frames = []
    
    # 1. NGAP Initial UE Message / Registration Request
    frames.append(PcapFrame(
        frame_number=1, timestamp=0.001, source_ip="10.0.1.10", dest_ip="10.0.2.1",
        protocol="NGAP", procedure="Registration", message_type="InitialUEMessage"
    ))
    frames.append(PcapFrame(
        frame_number=2, timestamp=0.003, source_ip="10.0.1.10", dest_ip="10.0.2.1",
        protocol="NAS-5GS", procedure="Registration", message_type="RegistrationRequest"
    ))
    
    # 2. SBI HTTP/2 AMF <-> AUSF Authentication
    frames.append(PcapFrame(
        frame_number=5, timestamp=0.012, source_ip="10.0.2.1", dest_ip="10.0.2.5",
        protocol="HTTP2", procedure="Authentication", message_type="POST /nausf-auth/v1/ue-authentications",
        status_code=201
    ))
    
    # 3. NAS-5GS Security Mode Command / Complete
    frames.append(PcapFrame(
        frame_number=10, timestamp=0.025, source_ip="10.0.2.1", dest_ip="10.0.1.10",
        protocol="NAS-5GS", procedure="Registration", message_type="SecurityModeCommand"
    ))
    frames.append(PcapFrame(
        frame_number=12, timestamp=0.031, source_ip="10.0.1.10", dest_ip="10.0.2.1",
        protocol="NAS-5GS", procedure="Registration", message_type="SecurityModeComplete"
    ))
    
    # 4. SBI HTTP/2 AMF <-> UDM Subscription Data
    frames.append(PcapFrame(
        frame_number=18, timestamp=0.045, source_ip="10.0.2.1", dest_ip="10.0.2.8",
        protocol="HTTP2", procedure="Registration", message_type="GET /nudm-sdm/v2/imsi-sub-data",
        status_code=200
    ))
    
    # 5. Fault Injection or Clean Finish
    if fault_scenario == "registration_congestion":
        # Deviating Frame 23: Registration Reject due to 5GS Congestion
        frames.append(PcapFrame(
            frame_number=23, timestamp=0.185, source_ip="10.0.2.1", dest_ip="10.0.1.10",
            protocol="NAS-5GS", procedure="Registration", message_type="RegistrationReject",
            status_code=503, cause_code="5GS_Congestion_Cause_22", delta_time_ms=140.0
        ))
    else:
        # Canonical Golden Flow: Registration Accept
        frames.append(PcapFrame(
            frame_number=23, timestamp=0.060, source_ip="10.0.2.1", dest_ip="10.0.1.10",
            protocol="NAS-5GS", procedure="Registration", message_type="RegistrationAccept",
            status_code=200, delta_time_ms=15.0
        ))
        
    return frames
