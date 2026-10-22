"""
Test Case T03: Golden Flow & SVM Deterministic Signaling Verifier Test
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

import pytest
from src.ml_engine.data.pcap_loader import create_synthetic_5gc_pcap
from src.ml_engine.models.signaling.golden_flow import GoldenFlowVerifier


def test_golden_flow_clean_trace():
    verifier = GoldenFlowVerifier()
    clean_frames = create_synthetic_5gc_pcap(fault_scenario=None)
    
    result = verifier.verify_trace(clean_frames)
    assert result["protocol_violation"] is False
    assert result["deviating_frame"] is None
    assert "conforms" in result["details"].lower() or "100%" in result["details"]


def test_golden_flow_faulty_trace_detection():
    verifier = GoldenFlowVerifier()
    faulty_frames = create_synthetic_5gc_pcap(fault_scenario="registration_congestion")
    
    result = verifier.verify_trace(faulty_frames)
    assert result["protocol_violation"] is True
    assert result["deviating_frame"] == 23
    assert result["cause_code"] == "5GS_Congestion_Cause_22"
    assert "RegistrationReject" in result["details"] or "anomalous" in result["details"]
    print(f"\n[PASSED] Golden Flow isolated Frame 23 with cause {result['cause_code']}")
