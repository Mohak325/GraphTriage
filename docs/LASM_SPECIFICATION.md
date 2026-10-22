# Algorithmic Specification: LASM SLA Liability Engine

**Research Grounding**: Paper 3: Anser et al. (IEEE Trans. Netw. Serv. Manage. [TNSM], 2025) • INSPIRE-5Gplus  
**Component**: `backend/app/services/lasm_engine.py`  
**Test Suite**: `backend/tests/test_lasm_cs1_cs8.py` (100% Pass)

---

## 1. Problem Context

In 5G Service-Based Architectures (SBA) and carrier multi-tenant clouds, end-to-end services traverse heterogeneous infrastructure:
- **MNO Core Operator** (e.g., AMF, SMF, UPF network functions)
- **Cloud Infrastructure Provider** (e.g., Kubernetes worker nodes, hypervisors, storage volumes)
- **Transport Optical Carrier** (e.g., BGP edge routers, DWDM transponders)

When an SLA breach occurs (e.g., PDU Session Setup Latency > 250ms), static alarm thresholds fail to disambiguate root culpability from symptom propagation, leading to prolonged legal and financial dispute.

**LASM (Liability and Trust Analysis Service)** algorithmically computes dynamic trust scores and automatically assesses contractual financial penalties based on Monthly Recurring Charges (MRC).

---

## 2. Mathematical Trust Scoring & Penalty Formula

### 2.1 Dynamic Trust Score ($T \in [0.05, 0.99]$)

Given an identified culpable component $C$, root-cause anomaly score $\alpha \in [0, 1]$, and historical breach frequency $H \in \mathbb{N}$:

$$T = \max\left(0.05, \min\left(0.99, 1.0 - \left(0.45 \cdot \alpha + 0.10 \cdot \min(H, 5)\right)\right)\right)$$

*For the frozen benchmark scenario `INC-2026-0042`:*  
- Component: `amf-01`
- Operator: `MNO-Core-Operator`
- Evaluated Trust Score: **$T = 0.42$**

---

### 2.2 Contractual Penalty Tiers (YAML Configurable)

The dynamic trust score maps deterministically to contractual MRC penalty tiers:

$$\text{Penalty } \% (T) = \begin{cases} 
30.0\% & \text{if } T < 0.30 \quad (\text{Critical Trust Breakdown}) \\
20.0\% & \text{if } 0.30 \le T < 0.60 \quad (\text{Moderate Breach}) \\
10.0\% & \text{if } 0.60 \le T < 0.80 \quad (\text{Minor Degradation}) \\
0.0\% & \text{if } T \ge 0.80 \quad (\text{High Standing / Exonerated})
\end{cases}$$

---

### 2.3 Financial Penalty Assessment

$$\text{MRC Financial Penalty USD} = \text{MRC USD} \times \left(\frac{\text{Penalty } \%}{100.0}\right)$$

*Reference Calculation for `INC-2026-0042`:*  
- Culpable Actor: `MNO-Core-Operator`
- Managed Service: `amf-01`
- Monthly Recurring Charge (MRC): **$150,000.00 USD**
- Penalty Tier: **20.0%**
- Assessed Financial Penalty: **$30,000.00 USD**

---

## 3. Multi-Tenant Test Matrix (CS1–CS8)

| Case ID | Scenario Description | Service Target | Dynamic Trust ($T$) | Penalty % | Financial Penalty |
|---|---|---|---|---|---|
| **CS1** | High Trust / Good Standing | `amf-01` | $0.92$ | $0.0\%$ | **$0.00** |
| **CS2** | Low Penalty Tier | `k8s-worker-node-14` | $0.72$ | $10.0\%$ | **$8,500.00** ($85k \times 10\%$) |
| **CS3** | Medium Tier (Reference INC-2026-0042) | `amf-01` | $0.42$ | $20.0\%$ | **$30,000.00** ($150k \times 20\%$) |
| **CS4** | Critical Trust Breakdown | `amf-01` | $0.18$ | $30.0\%$ | **$45,000.00** ($150k \times 30\%$) |
| **CS5** | Cloud Infrastructure Provider Culpability | `k8s-worker-node-14` | $0.50$ | $20.0\%$ | **$17,000.00** ($85k \times 20\%$) |
| **CS6** | Transport Optical Carrier Culpability | `router-core-2` | $0.22$ | $30.0\%$ | **$12,000.00** ($40k \times 30\%$) |
| **CS7** | Exact Tier Boundary Conditions | Boundary test | $0.30, 0.60, 0.80$ | $20\%, 10\%, 0\%$ | Boundary verified |
| **CS8** | Edge Cases (Zero MRC, Unmapped Actor) | `unknown-sidecar` | $0.20$ | $30.0\%$ | **$0.00** (Zero MRC handled safely) |
