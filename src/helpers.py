
"""Shared helpers. Imported by every notebook so the logic lives in one place."""

import os, re, hashlib
import numpy as np
import pandas as pd

import config as C


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def norm_col(c):
    """Lowercase, collapse whitespace, strip. Both CIC releases have stray spaces."""
    return re.sub(r'\s+', ' ', str(c)).strip().lower()


def harmonise(df):
    """Rename columns to canonical names where a mapping exists; normalise the rest."""
    df = df.copy()
    df.columns = [norm_col(c) for c in df.columns]
    rename = {}
    for canon, variants in C.CANONICAL.items():
        for v in variants:
            if v in df.columns and canon not in rename.values():
                rename[v] = canon
                break
    return df.rename(columns=rename)


def feature_columns(df):
    return [c for c in df.columns if c not in C.NON_FEATURES]


def clean_features(df, report=None):
    """Protocol section 6, steps 3-4. Returns cleaned df and a report dict."""
    rep = {} if report is None else report
    feats = feature_columns(df)
    X = df[feats].replace([np.inf, -np.inf], np.nan)
    before = len(df)
    keep = ~X.isna().any(axis=1)
    rep['rows_before'] = before
    rep['rows_dropped_nan'] = int((~keep).sum())
    df = df.loc[keep].copy()
    X = X.loc[keep]
    const = [c for c in X.columns if X[c].nunique(dropna=False) <= 1]
    rep['constant_columns'] = const
    df = df.drop(columns=const)
    rep['rows_after'] = len(df)
    return df, rep


def dedup(df, report=None):
    """Protocol section 6, step 5. Duplicate removal is reported, never silent."""
    rep = {} if report is None else report
    feats = feature_columns(df)
    n_before = len(df)
    df2 = df.drop_duplicates(subset=feats + ['label'])
    rep['exact_duplicates_removed'] = int(n_before - len(df2))
    rep['duplicate_rate'] = float((n_before - len(df2)) / max(n_before, 1))
    return df2, rep


def binarise(labels):
    """BENIGN -> 0, everything else -> 1. Null labels -> -1 (must be handled upstream)."""
    s = labels.astype(str).str.strip().str.upper()
    out = (s != 'BENIGN').astype(int)
    out[labels.isna() | (s == 'NAN')] = -1
    return out


def is_attempted(labels):
    """True where the improved release marks the flow as an unsuccessful attempt.

    The 'attempted category' column in the improved CSVs uses a sentinel for
    non-attempted flows rather than a null, so it cannot be tested with notna().
    The label string is the reliable signal.
    """
    return labels.astype(str).str.contains('attempted', case=False, na=False)


# Ordered rules. Order is load-bearing and every choice here is a documented
# decision, not an accident:
#   - 'web attack' before 'brute force', or "Web Attack - Brute Force" would
#     be swallowed by the brute-force rule
#   - 'infiltration' before 'portscan', so the improved release's
#     "Infiltration - Portscan" (71,767 flows) counts as Infiltration, which is
#     the attack it belongs to. Set C.INFIL_PORTSCAN_AS = 'PortScan' to invert
#     this; the choice materially changes the PortScan and Infiltration rows of
#     the class census, so state it in the paper either way.
#   - 'ddos' before 'dos'
FAMILY_RULES = [
    ('heartbleed', 'Heartbleed'),
    ('web attack', 'WebAttack'),
    ('brute force -web', 'WebAttack'),
    ('brute force -xss', 'WebAttack'),
    ('sql injection', 'WebAttack'),
    ('brute force -web', 'WebAttack'),
    ('brute force -xss', 'WebAttack'),
    ('sql injection', 'WebAttack'),
    ('xss', 'WebAttack'),
    ('sql', 'WebAttack'),
    ('infilt', '__INFIL__'),
    ('portscan', 'PortScan'),
    ('port scan', 'PortScan'),
    ('ddos', 'DDoS'),
    ('dos', 'DoS'),
    ('patator', 'BruteForce'),
    ('brute', 'BruteForce'),
    ('bot', 'Bot'),
]


def coarse_class(labels):
    """Collapse the raw labels into families for per-class reporting.

    Null labels map to 'NULL_LABEL' — never silently into an 'Other' bucket.
    """
    infil_portscan = getattr(C, 'INFIL_PORTSCAN_AS', 'Infiltration')
    s = labels.astype(str).str.strip().str.lower()
    out = []
    for raw, v in zip(labels, s):
        if pd.isna(raw) or v in ('nan', '', 'none'):
            out.append('NULL_LABEL')
            continue
        if v.startswith('benign'):
            out.append('BENIGN')
            continue
        hit = 'Other'
        for needle, fam in FAMILY_RULES:
            if needle in v:
                if fam == '__INFIL__':
                    hit = infil_portscan if ('portscan' in v or 'port scan' in v) \
                          else 'Infiltration'
                else:
                    hit = fam
                break
        out.append(hit)
    return pd.Series(out, index=labels.index)


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > y) for x in a for y in b)
    lt = sum((x < y) for x in a for y in b)
    return (gt - lt) / (len(a) * len(b))


def save_table(df, name):
    path = os.path.join(C.RESULTS, name)
    df.to_csv(path, index=False)
    print('saved', path, df.shape)
    return path
