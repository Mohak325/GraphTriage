"""
ConfExp: Active Diagnostic Probing Engine
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: ConfExp (Paper 12 - Koushki et al., JNSM 2025)
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class ConfExpEngine:
    """
    ConfExp Active Diagnostic Probing Engine.
    Employs a 2D Configuration Variable (CV) relevance matrix and greedy entropy-minimization
    test selection to iteratively update Bayesian confidence scores and isolate root-cause misconfigurations.
    """
    def __init__(self):
        # Candidate telecom Configuration Variables (CVs)
        self.candidate_cvs = [
            "amf.sbi.client_pool_size",
            "dns.core.srv_record",
            "smf.n4.association_timeout",
            "router.bgp.keepalive_interval",
            "k8s.pod.memory_limit"
        ]
        
        # Available active diagnostic tests / probes
        self.probes = [
            "http2_ping_nrf",
            "dns_srv_query",
            "pfcp_heartbeat_probe",
            "bgp_neighbor_check",
            "cgroup_memory_audit"
        ]
        
        # 2D Relevance Matrix M (shape: n_probes x n_cvs)
        # M[i, j] = 1 if probe i directly tests or exercises CV j
        self.M = np.array([
            [1, 0, 0, 0, 0],  # http2_ping_nrf -> amf.sbi.client_pool_size
            [0, 1, 0, 0, 0],  # dns_srv_query -> dns.core.srv_record
            [0, 0, 1, 0, 0],  # pfcp_heartbeat_probe -> smf.n4.association_timeout
            [0, 0, 0, 1, 0],  # bgp_neighbor_check -> router.bgp.keepalive_interval
            [0, 0, 0, 0, 1],  # cgroup_memory_audit -> k8s.pod.memory_limit
        ], dtype=float)

    def _entropy(self, c: np.ndarray) -> float:
        """Computes Shannon entropy of confidence vector."""
        c_nonzero = c[c > 1e-12]
        return -float(np.sum(c_nonzero * np.log2(c_nonzero)))

    def run_probing_cycle(
        self,
        suspected_cv: str = "amf.sbi.client_pool_size",
        confidence_threshold: float = 0.90,
        max_probes: int = 5
    ) -> Dict[str, Any]:
        """
        Executes an active probing sequence using greedy entropy reduction with Bayesian updating.
        """
        n_cvs = len(self.candidate_cvs)
        n_probes = len(self.probes)
        
        # Initial uniform confidence distribution
        c = np.ones(n_cvs, dtype=float) / n_cvs
        executed_probes = []
        
        available_probe_indices = list(range(n_probes))
        target_cv_idx = self.candidate_cvs.index(suspected_cv) if suspected_cv in self.candidate_cvs else 0
        
        for step in range(max_probes):
            if np.max(c) >= confidence_threshold or not available_probe_indices:
                break
                
            # Greedy test selection: choose probe that maximizes information gain
            best_probe_idx = available_probe_indices[0]
            max_gain = -1.0
            h_current = self._entropy(c)
            
            for p_idx in available_probe_indices:
                relevance = self.M[p_idx]
                p_fail = float(np.dot(c, relevance))
                gain = h_current * (1.0 - abs(0.5 - p_fail))
                if gain > max_gain:
                    max_gain = gain
                    best_probe_idx = p_idx
                    
            executed_probes.append(self.probes[best_probe_idx])
            available_probe_indices.remove(best_probe_idx)
            
            # Simulate probe outcome:
            # If the probe exercises suspected_cv, it detects the failure (probe_failed = True)
            probe_failed = (self.M[best_probe_idx, target_cv_idx] == 1)
            
            # Bayesian update across all candidate CVs
            for j in range(n_cvs):
                if probe_failed:
                    likelihood = 0.95 if self.M[best_probe_idx, j] == 1 else 0.05
                else:
                    likelihood = 0.05 if self.M[best_probe_idx, j] == 1 else 0.95
                c[j] *= likelihood
                
            # Re-normalize posterior distribution
            c /= np.sum(c)
            
        top_idx = int(np.argmax(c))
        return {
            "probes_executed": executed_probes,
            "isolated_cv": self.candidate_cvs[top_idx],
            "confidence": float(c[top_idx])
        }
