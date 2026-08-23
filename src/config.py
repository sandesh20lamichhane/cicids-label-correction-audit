
"""Frozen configuration for the CICIDS2017 label-correction study.

Nothing in this file may change after PROTOCOL.md is signed. If it must change,
record the change and the reason in PROTOCOL_AMENDMENTS.md.
"""

import os

DRIVE_ROOT = '/content/drive/MyDrive/research/ids-label-correction'

RAW_ORIGINAL = os.path.join(DRIVE_ROOT, 'data/raw_original')
RAW_IMPROVED = os.path.join(DRIVE_ROOT, 'data/raw_improved')
INTERIM      = os.path.join(DRIVE_ROOT, 'data/interim')
RESULTS      = os.path.join(DRIVE_ROOT, 'results')
FIGURES      = os.path.join(DRIVE_ROOT, 'figures')
CHECKPOINTS  = os.path.join(DRIVE_ROOT, 'checkpoints')

# --- frozen experimental constants -----------------------------------------
SEEDS = [11, 23, 37, 51, 73]

SPLIT_PROTOCOLS = ['random_70_30', 'day_ordered']

# how flows labelled "Attempted" in the improved dataset are treated
ATTEMPTED_POLICIES = ['as_attack', 'as_benign', 'dropped']

MODELS = ['logreg', 'random_forest', 'xgboost']

# equivalence margin for H4 (TOST)
EQUIV_MARGIN = 0.02

# gate G2: minimum acceptable matched-flow rate for Arm B
MIN_MATCH_RATE = 0.20

# gate G4: maximum tolerated cross-session drift
REPRO_TOLERANCE = 0.02

# how the improved release's "Infiltration - Portscan" flows are counted.
# 'Infiltration' (default) or 'PortScan'. This is a reported decision.
INFIL_PORTSCAN_AS = 'Infiltration'

# rows carrying no label at all are dropped and the count is reported
DROP_NULL_LABELS = True

# --- day-ordered split ------------------------------------------------------
TRAIN_DAYS = ['monday', 'tuesday', 'wednesday']
TEST_DAYS  = ['thursday', 'friday']

# --- Kaggle slugs -----------------------------------------------------------
# VERIFIED slug for the corrected data (Liu et al., IEEE CNS 2022):
KAGGLE_IMPROVED = 'ernie55ernie/improved-cicids2017-and-csecicids2018'

# The original CICIDS2017 has several Kaggle mirrors and they are NOT equivalent.
# You must use a mirror carrying GeneratedLabelledFlows / TrafficLabelling_,
# which retains Source IP / Destination IP / Flow ID. Mirrors carrying only
# MachineLearningCVE will make Arm B impossible. Notebook 01 helps you check.
KAGGLE_ORIGINAL = ''   # <-- fill in during notebook 01, then never change

# --- column harmonisation ---------------------------------------------------
# The two versions name the same fields differently. Keys are the canonical
# names used throughout the pipeline.
CANONICAL = {
    'src_ip':    ['source ip', 'src ip', 'srcip'],
    'src_port':  ['source port', 'src port', 'srcport'],
    'dst_ip':    ['destination ip', 'dst ip', 'dstip'],
    'dst_port':  ['destination port', 'dst port', 'dstport'],
    'protocol':  ['protocol'],
    'timestamp': ['timestamp'],
    'label':     ['label'],
    'flow_id':   ['flow id', 'flowid', 'id'],
    'attempted': ['attempted category'],
}

# columns never used as model features
NON_FEATURES = ['src_ip', 'dst_ip', 'timestamp', 'label', 'flow_id',
                'attempted', 'day', 'version']
