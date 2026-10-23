# Pre-Trained Model Artifacts Directory

This folder is the target destination for extracted model artifacts trained in **Google Colab** or local GPU/CPU runners.

### Expected Files from `rca_models_bundle.zip`:
- `rca_classifier.joblib`: Regularized Multi-Modal Random Forest Root Cause Localizer (Top-1 >= 82%, Top-3 >= 92%, MRR >= 0.880)
- `fault_classifier.joblib`: 11-Class Microservice Fault Classifier
- `mnsuad_pipeline.joblib`: MNSUAD Weakly-Supervised DAGMM + DevNet Pipeline (5% Contamination Resilient)
- `telegan_core.joblib`: BiLSTM Dual-Autoencoder GAN with Critic Gap Penalty
- `trans_gnn.joblib`: 2-Layer Graph Convolutional Network (GCN) for Invocation Call-Graph Localization
- `metadata.json`: Feature names, service vocabulary, fault vocabulary, and training validation scorecard
- `rcaeval_cve_test_report.csv`: 147 test cases with CVE mapping and remediation playbooks
- `rcaeval_cve_summary.json`: Executive test metrics summary

### How to Extract:
Extract the downloaded `rca_models_bundle.zip` directly into this folder:
```powershell
Expand-Archive -Path "$HOME\Downloads\rca_models_bundle.zip" -DestinationPath "c:\Users\sanda\cloud\src\ml_engine\saved_models" -Force
```
The `PretrainedRcaModelRegistry` in [model_loader.py](file:///c:/Users/sanda/cloud/src/ml_engine/model_loader.py) will automatically detect, load, and serve these pre-trained models.
