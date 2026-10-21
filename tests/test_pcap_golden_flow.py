"""
Test Suite for Wireshark PCAP Frame Extraction & Golden Flow Verifier.
Grounding: Paper 11 (Golden Flow).
"""

from src.pcap.frame_parser import PCAPFrameParser
from src.pcap.wireshark_extractor import GoldenFlowVerifier


def test_tshark_frame_parser():
    raw_frame = {
        "frame.number": "23",
        "protocol": "NAS-5GS",
        "procedure": "Registration",
        "message_type": "RegistrationReject",
        "source_component": "amf-01",
        "cause_code": "5GS_Congestion",
        "ip.src": "10.0.1.10",
        "ip.dst": "10.0.1.25"
    }

    event = PCAPFrameParser.parse_tshark_json_frame(raw_frame)

    assert event.event_type == "pcap_frame"
    assert event.severity == "critical"
    assert event.pcap_metadata is not None
    assert event.pcap_metadata.frame_number == 23
    assert event.pcap_metadata.cause_code == "5GS_Congestion"


def test_golden_flow_successful_registration():
    verifier = GoldenFlowVerifier()

    canonical_msgs = [
        "RegistrationRequest",
        "AuthenticationRequest",
        "AuthenticationResponse",
        "SecurityModeCommand",
        "SecurityModeComplete",
        "RegistrationAccept"
    ]

    events = []
    for i, msg in enumerate(canonical_msgs, start=1):
        raw = {
            "frame_number": i,
            "protocol": "NAS-5GS",
            "procedure": "registration",
            "message_type": msg,
            "source_component": "amf-01"
        }
        events.append(PCAPFrameParser.parse_tshark_json_frame(raw))

    verification = verifier.verify_call_flow("registration", events)

    assert verification.protocol_violation is False
    assert verification.deviating_frame is None


def test_golden_flow_detects_deviation_frame_and_cause():
    verifier = GoldenFlowVerifier()

    # Flow where Frame 4 has RegistrationReject instead of SecurityModeCommand
    faulty_msgs = [
        ("RegistrationRequest", None),
        ("AuthenticationRequest", None),
        ("AuthenticationResponse", None),
        ("RegistrationReject", "5GS_Congestion")
    ]

    events = []
    for i, (msg, cause) in enumerate(faulty_msgs, start=20):
        raw = {
            "frame_number": i,
            "protocol": "NAS-5GS",
            "procedure": "registration",
            "message_type": msg,
            "cause_code": cause,
            "source_component": "amf-01"
        }
        events.append(PCAPFrameParser.parse_tshark_json_frame(raw))

    verification = verifier.verify_call_flow("registration", events)

    assert verification.protocol_violation is True
    # Frame 23 must be isolated as the deviating frame
    assert verification.deviating_frame == 23
    assert "Congestion" in str(verification.cause_code) or "Reject" in str(verification.cause_code)
