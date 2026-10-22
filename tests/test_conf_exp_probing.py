"""
Test: ConfExp Active Diagnostic Probing Test
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

import pytest
from src.ml_engine.models.probing.conf_exp import ConfExpEngine


def test_conf_exp_active_probing():
    engine = ConfExpEngine()
    
    # Run active probing targeting 'amf.sbi.client_pool_size'
    result = engine.run_probing_cycle(suspected_cv="amf.sbi.client_pool_size", confidence_threshold=0.90)
    
    assert len(result["probes_executed"]) >= 1
    assert result["isolated_cv"] == "amf.sbi.client_pool_size"
    assert result["confidence"] >= 0.90
    print(f"\n[PASSED] ConfExp isolated CV: {result['isolated_cv']} with confidence {result['confidence']:.3f} using probes {result['probes_executed']}")
