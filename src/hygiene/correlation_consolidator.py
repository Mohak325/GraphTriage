"""
Layer 3: Pearson Cross-Correlation Consolidation.
Grounding: IEEE ISCC 2025; TeleGAN-Core (Paper 4).
Detects pairwise collinear KPIs with absolute Pearson correlation >= tau3 (default 0.95).
Retains the KPI with highest variance / information content in each collinear cluster,
eliminating 28% to 71% of redundant collinear variables.
"""

from typing import List, Tuple, Dict
import numpy as np
import pandas as pd


def consolidate_correlated_kpis(
    df_kpis: pd.DataFrame,
    tau3: float = 0.95
) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Performs pairwise Pearson correlation screening.
    
    Args:
        df_kpis: DataFrame where columns are KPI names, rows are time steps.
        tau3: Cross-correlation threshold (default 0.95).
        
    Returns:
        kept_columns: List of KPI names to retain.
        dropped_columns: List of redundant KPI names dropped.
        redundancy_mapping: Dict mapping dropped KPI -> representative KPI kept.
    """
    if df_kpis.empty or df_kpis.shape[1] <= 1:
        return list(df_kpis.columns), [], {}

    # Calculate standard deviation to sort candidates by informative variance
    variances = df_kpis.var(numeric_only=True).to_dict()
    # Sort columns by variance descending (keep the highest variance representative)
    sorted_cols = sorted(list(df_kpis.columns), key=lambda c: variances.get(c, 0.0), reverse=True)

    corr_matrix = df_kpis[sorted_cols].corr().abs()
    
    kept_columns: List[str] = []
    dropped_columns: List[str] = []
    redundancy_mapping: Dict[str, str] = {}

    for col in sorted_cols:
        # Check if col is strongly correlated with any already kept column
        correlated_with = None
        for kept in kept_columns:
            corr_val = corr_matrix.loc[col, kept]
            if not np.isnan(corr_val) and corr_val >= tau3:
                correlated_with = kept
                break

        if correlated_with is not None:
            dropped_columns.append(col)
            redundancy_mapping[col] = correlated_with
        else:
            kept_columns.append(col)

    return kept_columns, dropped_columns, redundancy_mapping
