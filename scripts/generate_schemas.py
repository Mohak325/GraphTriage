"""Script to generate JSON Schemas and OpenAPI specification from Pydantic v2 models."""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from contracts.pydantic.contract_1_telemetry import NormalizedTelemetryEvent
from contracts.pydantic.contract_2_rca_analysis import RCARequest, RCAResponse
from contracts.pydantic.contract_3_remediation import (
    DiagnoseAndRemediateRequest,
    DiagnoseAndRemediateResponse,
)


def export_schemas():
    schema_dir = ROOT_DIR / "contracts" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)

    openapi_dir = ROOT_DIR / "contracts" / "openapi"
    openapi_dir.mkdir(parents=True, exist_ok=True)

    # 1. Contract 1
    with open(schema_dir / "contract_1.json", "w") as f:
        json.dump(NormalizedTelemetryEvent.model_json_schema(), f, indent=2)

    # 2. Contract 2 Request & Response
    with open(schema_dir / "contract_2_request.json", "w") as f:
        json.dump(RCARequest.model_json_schema(), f, indent=2)

    with open(schema_dir / "contract_2_response.json", "w") as f:
        json.dump(RCAResponse.model_json_schema(), f, indent=2)

    # 3. Contract 3 Request & Response
    with open(schema_dir / "contract_3_request.json", "w") as f:
        json.dump(DiagnoseAndRemediateRequest.model_json_schema(), f, indent=2)

    with open(schema_dir / "contract_3_response.json", "w") as f:
        json.dump(DiagnoseAndRemediateResponse.model_json_schema(), f, indent=2)

    # 4. OpenAPI Specification for Contract 3 API
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Intelligent Telecom Cloud RCA & SLA Liability Service (Contract 3)",
            "version": "2.0.0",
            "description": "Carrier-grade API served by Person C for governed agentic diagnostics, SLA liability attribution (LASM), and remediation planning.",
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Local Development / Carrier Testbed"},
            {"url": "https://api.rca.telecom.carrier.internal", "description": "Production AWS API Gateway"}
        ],
        "paths": {
            "/api/rca/diagnose-and-remediate": {
                "post": {
                    "summary": "Governed Agentic Diagnostics & SLA Liability Attribution",
                    "operationId": "diagnose_and_remediate",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DiagnoseAndRemediateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful diagnostic and remediation synthesis with SLA attribution",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DiagnoseAndRemediateResponse"}
                                }
                            }
                        },
                        "422": {"description": "Validation Error"},
                        "500": {"description": "Internal Agentic Synthesis Error"}
                    }
                }
            },
            "/api/hitl/approve": {
                "post": {
                    "summary": "Approve pending remediation plan with cryptographic signature",
                    "operationId": "hitl_approve",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["incident_id", "approval_token", "operator_signature"],
                                    "properties": {
                                        "incident_id": {"type": "string"},
                                        "approval_token": {"type": "string"},
                                        "operator_signature": {"type": "string"},
                                        "comments": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Remediation plan approved and dispatched to AWS Systems Manager"},
                        "403": {"description": "Invalid or expired cryptographic token"},
                        "404": {"description": "Incident not found"}
                    }
                }
            },
            "/api/hitl/reject": {
                "post": {
                    "summary": "Reject pending remediation plan",
                    "operationId": "hitl_reject",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["incident_id", "approval_token", "reason"],
                                    "properties": {
                                        "incident_id": {"type": "string"},
                                        "approval_token": {"type": "string"},
                                        "reason": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Remediation rejected"},
                        "403": {"description": "Invalid token"}
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "DiagnoseAndRemediateRequest": DiagnoseAndRemediateRequest.model_json_schema(),
                "DiagnoseAndRemediateResponse": DiagnoseAndRemediateResponse.model_json_schema(),
                "RCARequest": RCARequest.model_json_schema(),
                "RCAResponse": RCAResponse.model_json_schema(),
                "NormalizedTelemetryEvent": NormalizedTelemetryEvent.model_json_schema(),
            }
        }
    }

    with open(openapi_dir / "contract_3_openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)

    print("Successfully exported JSON Schemas and OpenAPI spec.")


if __name__ == "__main__":
    export_schemas()
