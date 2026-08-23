"""make_diagrams.py — methodology figures for the label-correction study.

Generates:
  fig0_pipeline.png       six-stage pipeline with defects (red) and gates (green)
  fig0b_design.png        the two-arm design and the matched-flow join
  fig3_transition_heatmap.png   (only if table5_label_transition_matrix.csv exists)

Pure matplotlib, no data needed for the first two. Run anywhere:
  python make_diagrams.py [output_dir]
"""
import sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

INK = '#1a2233'
BOX = '#eef2f8'
EDGE = '#3b5b92'
RED = '#b3362b'
GREEN = '#2c7a3f'
GREY = '#5a6472'


def box(ax, x, y, w, h, title, lines, fc=BOX, ec=EDGE, title_c=INK, fs=8.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h - 0.045, title, ha='center', va='top',
            fontsize=fs + 0.7, fontweight='bold', color=title_c)
    ax.text(x + w / 2, y + h - 0.315, '\n'.join(lines), ha='center', va='top',
            fontsize=fs - 0.6, color=INK, linespacing=1.45)


def arrow(ax, x1, y1, x2, y2, color=EDGE, lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                 mutation_scale=13, color=color, lw=lw))


def tag(ax, x, y, text, color, fs=7.2, ha='center'):
    ax.text(x, y, text, ha=ha, va='center', fontsize=fs, color=color,
            fontweight='bold', linespacing=1.4)


# ============================================================================
# Figure 0 — pipeline
# ============================================================================
fig, ax = plt.subplots(figsize=(13.2, 4.6))
ax.set_xlim(0, 13.2); ax.set_ylim(0, 4.6); ax.axis('off')

W, H, Y = 1.92, 1.58, 2.05
xs = [0.22, 2.42, 4.62, 6.82, 9.02, 11.22]

box(ax, xs[0], Y, W, H, '1 · Acquire + verify',
    ['original: TrafficLabelling_',
     '(pshikk/…-untampered)',
     'improved: Liu et al. 2022',
     '(ernie55ernie/…)',
     'SHA-256 manifest'])
box(ax, xs[1], Y, W, H, '2 · Audit + repair',
    ['label census vs published',
     'per-file reconciliation',
     'purge 288,602 blank rows',
     '→ 2,830,743 exact',
     'duplicate audit'])
box(ax, xs[2], Y, W, H, '3 · Clock normalise',
    ['per-element parsing',
     "(format='mixed')",
     '12-h → 24-h repair',
     '+3 h offset by search',
     '(local vs UTC)'])
box(ax, xs[3], Y, W, H, '4 · Matched join',
    ['canonical endpoints',
     '(sorted ip:port pairs)',
     '+ protocol + minute',
     '1,604,995 matched flows',
     'labels differ on 4.40%'])
box(ax, xs[4], Y, W, H, '5 · Experiment grid',
    ['Arm A · Arm B',
     'splits × policies',
     '3 models × 5 seeds',
     '480 runs, fixed schema,',
     'checkpointed runs.csv'])
box(ax, xs[5], Y, W, H, '6 · Analysis',
    ['H1–H4 · Wilcoxon',
     "Holm · Cliff's δ · TOST",
     'headline.json',
     'every number from CSV,',
     'none typed by hand'])

for i in range(5):
    arrow(ax, xs[i] + W, Y + H / 2, xs[i + 1], Y + H / 2)

# defects (red, below)
tag(ax, xs[1] + W / 2, 1.30, 'D1  288,602 blank rows\nin WebAttacks CSV', RED)
tag(ax, xs[2] + W / 2, 1.22, 'D2 minute resolution\nD3 12-h clock, no AM/PM\nD5 mixed formats across files', RED)
tag(ax, xs[3] + W / 2, 1.30, 'D4  inconsistent\nflow direction', RED)
tag(ax, xs[4] + W / 2, 1.30, 'design flaw caught:\nday-split multiclass degenerate', RED)
for xc in [xs[1] + W / 2, xs[2] + W / 2, xs[3] + W / 2, xs[4] + W / 2]:
    ax.plot([xc, xc], [1.62, Y - 0.02], color=RED, lw=0.9, ls=':')

# gates (green, above)
tag(ax, xs[1] + W / 2, 4.05, 'G1  integrity vs\npublished counts', GREEN)
tag(ax, xs[3] + W / 2, 4.05, 'G2  match rate ≥ 20%\n(achieved 90.8%)', GREEN)
tag(ax, xs[4] + W / 2, 4.05, 'schema repair:\n300 rows migrated', GREEN)
for xc in [xs[1] + W / 2, xs[3] + W / 2, xs[4] + W / 2]:
    ax.plot([xc, xc], [Y + H + 0.02, 3.78], color=GREEN, lw=0.9, ls=':')

ax.text(0.22, 4.38, 'Pre-registered protocol frozen before data contact; amendments logged',
        fontsize=8.6, color=GREY, style='italic')
ax.text(0.22, 0.42, 'D1–D5: defects found in the original CICIDS2017 release   ·   '
                    'G1/G2: pre-registered gates', fontsize=8.6, color=GREY)

fig.tight_layout()
p = os.path.join(OUT, 'fig0_pipeline.png')
fig.savefig(p, dpi=220, bbox_inches='tight'); plt.close(fig)
print('saved', p)

# ============================================================================
# Figure 0b — two-arm design
# ============================================================================
fig, ax = plt.subplots(figsize=(11.6, 5.6))
ax.set_xlim(0, 11.6); ax.set_ylim(0, 5.6); ax.axis('off')

# source datasets
box(ax, 0.35, 3.55, 2.5, 1.55, 'Original release',
    ['GeneratedLabelledFlows',
     '2,830,743 flows',
     '(after blank-row repair)',
     'original CICFlowMeter'])
box(ax, 0.35, 0.55, 2.5, 1.55, 'Improved release',
    ['Liu et al., IEEE CNS 2022',
     '2,099,976 flows (2017)',
     'regenerated from PCAP,',
     'fixed CICFlowMeter'])

# Arm A
box(ax, 4.35, 2.20, 2.55, 1.75, 'Arm A · dataset level',
    ['train + evaluate on each',
     'version separately',
     '',
     'measures the TOTAL effect:',
     'labels + flow reconstruction',
     '+ feature fixes  (confounded,',
     'and labelled as such)'], fc='#f3eee4', ec='#9c7c3c')
arrow(ax, 2.85, 4.30, 4.35, 3.55, color='#9c7c3c')
arrow(ax, 2.85, 1.30, 4.35, 2.60, color='#9c7c3c')

# matched join
box(ax, 4.35, 4.30, 2.55, 1.05, 'Canonical join key',
    ['sorted (ip:port) endpoints',
     '+ protocol + minute'], fc='#e8f0e9', ec=GREEN)
box(ax, 8.15, 3.55, 3.1, 1.8, 'Matched subset',
    ['1,604,995 identical flows',
     'labels differ on 70,552 (4.40%)',
     'benign→attack  65,001',
     'attack→benign  9',
     'PortScan / DDoS untouched',
     '(controls)'], fc='#e8f0e9', ec=GREEN)
arrow(ax, 6.90, 4.82, 8.15, 4.55, color=GREEN)
arrow(ax, 2.85, 4.75, 4.35, 4.85, color=GREEN)
arrow(ax, 2.85, 1.75, 4.35, 4.45, color=GREEN)

# Arm B
box(ax, 8.15, 0.75, 3.1, 2.0, 'Arm B · labels only',
    ['SAME feature matrix,',
     'two label columns:',
     'label_original vs label_improved',
     '',
     'isolates the PURE labelling',
     'effect — the contribution'], fc='#eae4f0', ec='#5b3b92')
arrow(ax, 9.70, 3.55, 9.70, 2.75, color='#5b3b92')

ax.text(0.35, 0.18, 'Why two arms: the improved release is regenerated, not relabelled — '
                    'flow boundaries moved, so no row-for-row correspondence exists by default.',
        fontsize=8.8, color=GREY, style='italic')

fig.tight_layout()
p = os.path.join(OUT, 'fig0b_design.png')
fig.savefig(p, dpi=220, bbox_inches='tight'); plt.close(fig)
print('saved', p)

# ============================================================================
# Figure 3 — transition heatmap (data figure; only if the CSV is present)
# ============================================================================
csv = os.path.join(OUT, 'table5_label_transition_matrix.csv')
if not os.path.exists(csv):
    csv = os.path.join(OUT, 'results', 'table5_label_transition_matrix.csv')
if os.path.exists(csv):
    import pandas as pd, numpy as np
    xt = pd.read_csv(csv, index_col=0)
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    logd = np.log10(xt.values + 1)
    im = ax.imshow(logd, cmap='Blues')
    ax.set_xticks(range(len(xt.columns))); ax.set_xticklabels(xt.columns, rotation=45,
                                                              ha='right', fontsize=8)
    ax.set_yticks(range(len(xt.index))); ax.set_yticklabels(xt.index, fontsize=8)
    ax.set_xlabel('improved label'); ax.set_ylabel('original label')
    for i in range(xt.shape[0]):
        for j in range(xt.shape[1]):
            v = int(xt.values[i, j])
            if v:
                ax.text(j, i, f'{v:,}', ha='center', va='center', fontsize=6.6,
                        color='white' if logd[i, j] > logd.max() * 0.6 else INK)
    ax.set_title('Label transitions on 1,604,995 matched flows (log colour scale)',
                 fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.8, label='log10(count + 1)')
    fig.tight_layout()
    p = os.path.join(OUT, 'fig3_transition_heatmap.png')
    fig.savefig(p, dpi=220, bbox_inches='tight'); plt.close(fig)
    print('saved', p)
else:
    print('table5_label_transition_matrix.csv not found here — heatmap skipped '
          '(run this script in the Drive project folder to render it)')
