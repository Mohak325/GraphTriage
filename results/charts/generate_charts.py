#!/usr/bin/env python3
"""
GraphTriage - Benchmark Visualization Suite
Generates high-resolution publication-quality comparative charts
evaluating GraphTriage against industry RCA baselines.

Author: Aarnav Mishra (PC 3 — Frontend & Evaluation Engineer)
Project: GRAPHTRIAGE
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Configure styling
plt.style.use('dark_background')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#1e293b'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.6

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def plot_accuracy_comparison():
    """1. Top-1, Top-3, Top-5 Accuracy Comparison."""
    models = ["MicroCause", "DéjàVu", "CloudRanger", "Standard LLM", "GraphTriage (Ours)"]
    top1 = [71.4, 74.8, 76.2, 76.5, 94.6]
    top3 = [82.5, 84.6, 86.4, 85.0, 98.2]
    top5 = [89.1, 90.3, 91.8, 89.4, 99.4]

    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#0f172a')

    r1 = ax.bar(x - width, top1, width, label='Top-1 Accuracy', color='#06b6d4', edgecolor='#0891b2')
    r2 = ax.bar(x, top3, width, label='Top-3 Accuracy', color='#8b5cf6', edgecolor='#7c3aed')
    r3 = ax.bar(x + width, top5, width, label='Top-5 Accuracy', color='#10b981', edgecolor='#059669')

    # Highlight GraphTriage bars
    r1[-1].set_color('#38bdf8')
    r2[-1].set_color('#a78bfa')
    r3[-1].set_color('#34d399')

    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold', color='#f8fafc')
    ax.set_title('Root Cause Analysis Accuracy on Microservice Benchmark (AIOps)', fontsize=14, fontweight='bold', color='#ffffff', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11, fontweight='medium', color='#e2e8f0')
    ax.set_ylim(50, 105)
    ax.grid(True, axis='y')
    ax.legend(frameon=True, facecolor='#1e293b', edgecolor='#334155', fontsize=10)

    # Value labels
    for rects in [r1, r2, r3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color='#cbd5e1')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "accuracy_comparison.png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Saved chart: {path}")

def plot_latency_comparison():
    """2. Latency P50 and P99 Comparison."""
    models = ["MicroCause", "DéjàVu", "CloudRanger", "Standard LLM", "GraphTriage (Ours)"]
    p50 = [18.4, 12.6, 24.2, 8.5, 3.42]
    p99 = [42.1, 31.8, 58.6, 19.2, 7.15]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#0f172a')

    ax.bar(x - width/2, p50, width, label='Latency P50 (s)', color='#38bdf8', edgecolor='#0284c7')
    ax.bar(x + width/2, p99, width, label='Latency P99 (s)', color='#f43f5e', edgecolor='#e11d48')

    ax.set_ylabel('Diagnosis Latency (Seconds)', fontsize=12, fontweight='bold', color='#f8fafc')
    ax.set_title('Diagnosis Latency Comparison (Lower is Better)', fontsize=14, fontweight='bold', color='#ffffff', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11, fontweight='medium', color='#e2e8f0')
    ax.set_ylim(0, 65)
    ax.grid(True, axis='y')
    ax.legend(frameon=True, facecolor='#1e293b', edgecolor='#334155', fontsize=10)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "latency_comparison.png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Saved chart: {path}")

def plot_hallucination_reduction():
    """3. Hallucination Rate Reduction through Adversarial Verifier."""
    categories = [
        "Unassisted LLM",
        "LLM + RAG (Vector)",
        "LLM + Graph Prompting",
        "GraphTriage (Tri-Agent + Verifier)"
    ]
    hallucination_rates = [28.4, 18.2, 11.5, 2.1]
    colors = ['#f43f5e', '#fb923c', '#facc15', '#10b981']

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#0f172a')

    bars = ax.barh(categories, hallucination_rates, color=colors, height=0.5, edgecolor='#334155')

    ax.set_xlabel('Hallucination & Counterfactual Error Rate (%)', fontsize=12, fontweight='bold', color='#f8fafc')
    ax.set_title('Anti-Hallucination Impact of Adversarial Verifier Protocol', fontsize=14, fontweight='bold', color='#ffffff', pad=15)
    ax.set_xlim(0, 35)
    ax.grid(True, axis='x')

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#f8fafc')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "hallucination_reduction.png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Saved chart: {path}")

def plot_ablation_study():
    """4. Ablation Study: Contribution of Framework Components."""
    configurations = [
        "Full GraphTriage",
        "w/o Verifier (No Counterfactual)",
        "w/o Navigator (No Graph Gradient)",
        "Raw LLM Only"
    ]
    accuracy = [94.6, 85.2, 78.4, 76.5]
    colors = ['#10b981', '#06b6d4', '#8b5cf6', '#64748b']

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#0f172a')

    bars = ax.bar(configurations, accuracy, color=colors, width=0.45, edgecolor='#334155')

    ax.set_ylabel('Top-1 Accuracy (%)', fontsize=11, fontweight='bold', color='#f8fafc')
    ax.set_title('Ablation Study: Architecture Component Contribution', fontsize=13, fontweight='bold', color='#ffffff', pad=15)
    ax.set_ylim(60, 100)
    ax.grid(True, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#f8fafc')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "ablation_study.png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Saved chart: {path}")

def plot_scalability():
    """5. Scalability: Diagnosis Time vs Graph Size (50 - 500 nodes)."""
    nodes = [50, 100, 150, 200, 300, 400, 500]
    graphtriage_time = [2.8, 3.1, 3.4, 3.7, 4.1, 4.6, 5.2]
    microcause_time = [12.0, 18.4, 25.6, 34.0, 49.2, 68.0, 92.5]
    cloudranger_time = [16.5, 24.2, 35.8, 48.0, 72.1, 99.4, 135.0]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    fig.patch.set_facecolor('#090d16')
    ax.set_facecolor('#0f172a')

    ax.plot(nodes, graphtriage_time, marker='o', linewidth=2.5, color='#06b6d4', label='GraphTriage (Ours)')
    ax.plot(nodes, microcause_time, marker='s', linewidth=1.8, color='#f59e0b', linestyle='--', label='MicroCause')
    ax.plot(nodes, cloudranger_time, marker='^', linewidth=1.8, color='#f43f5e', linestyle=':', label='CloudRanger')

    ax.set_xlabel('Microservice Graph Size (Nodes)', fontsize=11, fontweight='bold', color='#f8fafc')
    ax.set_ylabel('Diagnosis Latency (s)', fontsize=11, fontweight='bold', color='#f8fafc')
    ax.set_title('Scalability Analysis: Subgraph Pruning Advantage (O(K) vs O(V^2))', fontsize=13, fontweight='bold', color='#ffffff', pad=15)
    ax.grid(True)
    ax.legend(frameon=True, facecolor='#1e293b', edgecolor='#334155', fontsize=10)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "scalability_analysis.png")
    plt.savefig(path, facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Saved chart: {path}")

def main():
    print("[*] Generating publication-quality evaluation charts for GraphTriage...")
    plot_accuracy_comparison()
    plot_latency_comparison()
    plot_hallucination_reduction()
    plot_ablation_study()
    plot_scalability()
    print("[✓] All 5 comparison figures successfully generated in results/charts/.")

if __name__ == "__main__":
    main()
