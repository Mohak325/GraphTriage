import os
import json
import joblib
import numpy as np

def model_fn(model_dir):
    """Loads all trained models from model_dir into memory."""
    models = {
        "rca": joblib.load(os.path.join(model_dir, "rca_classifier.joblib")),
        "fault": joblib.load(os.path.join(model_dir, "fault_classifier.joblib")),
    }
    meta_path = os.path.join(model_dir, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            models["metadata"] = json.load(f)
    return models

def input_fn(request_body, request_content_type):
    """Parses incoming JSON request."""
    if request_content_type == "application/json":
        return json.loads(request_body)
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, models):
    """Executes Contract 2 RCA diagnosis."""
    features = np.array(input_data.get("features", [])).reshape(1, -1)
    
    rca_model = models["rca"]
    fault_model = models["fault"]
    
    # Predict Root Cause Service
    rca_pred = str(rca_model.predict(features)[0])
    rca_probs = rca_model.predict_proba(features)[0]
    classes = rca_model.classes_
    
    top3_idx = np.argsort(rca_probs)[::-1][:3]
    rankings = [{"service": str(classes[i]), "confidence": round(float(rca_probs[i]), 4)} for i in top3_idx]
    top_confidence = round(float(np.max(rca_probs)), 4)
    
    # Predict Fault Modality
    fault_pred = str(fault_model.predict(features)[0])
    
    # Map to CVE Threat Intelligence
    cve_id = "CVE-2023-44487" if "cpu" in fault_pred else ("CVE-2022-0543" if "mem" in fault_pred else "CVE-2023-27487")
    severity = "CRITICAL" if cve_id == "CVE-2022-0543" else "HIGH"
    
    return {
        "incident_id": input_data.get("incident_id", "INC-ONLINE-001"),
        "status": "COMPLETED",
        "predicted_root_cause": rca_pred,
        "confidence_score": top_confidence,
        "predicted_fault_type": fault_pred,
        "candidate_rankings": rankings,
        "cve_attribution": {
            "cve_id": cve_id,
            "severity": severity,
            "remediation_action": "Apply HTTP/2 stream concurrency limits and auto-scale pods."
        },
        "lasm_sla_penalty_pct": 20.0 if top_confidence >= 0.85 else 10.0
    }

def output_fn(prediction, accept):
    """Serializes output back to JSON."""
    if accept == "application/json" or accept == "*/*":
        return json.dumps(prediction), "application/json"
    raise ValueError(f"Unsupported accept type: {accept}")