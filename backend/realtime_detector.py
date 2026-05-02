import numpy as np

# ── Keypoint indices (YOLOv8 COCO order) ────────────────────────
LEFT_SHOULDER  = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW     = 7
RIGHT_ELBOW    = 8
LEFT_WRIST     = 9
RIGHT_WRIST    = 10
LEFT_HIP       = 11
RIGHT_HIP      = 12

# ── EMA state ────────────────────────────────────────────────────
_ema_score = 0.0
EMA_ALPHA  = 0.25          # how fast score reacts (lower = smoother)

# ── Cooldown so SHOPLIFTING stays visible ────────────────────────
_cooldown       = 0
COOLDOWN_FRAMES = 60        # ~2 s at 30 fps


# ── Helpers ──────────────────────────────────────────────────────
def _torso_height(kp):
    """Pixel height from hip-midpoint to shoulder-midpoint."""
    shoulder = (kp[LEFT_SHOULDER] + kp[RIGHT_SHOULDER]) / 2
    hip      = (kp[LEFT_HIP]      + kp[RIGHT_HIP])      / 2
    h = np.linalg.norm(shoulder - hip)
    return max(h, 1.0)          # avoid div-by-zero


def _is_valid(kp):
    """
    Require the 8 key joints to have non-zero coordinates.
    YOLOv8 .xy tensors don't carry confidence, so we just check
    that the point was actually detected (non-zero).
    """
    needed = [LEFT_SHOULDER, RIGHT_SHOULDER,
              LEFT_WRIST,    RIGHT_WRIST,
              LEFT_HIP,      RIGHT_HIP,
              LEFT_ELBOW,    RIGHT_ELBOW]
    return all(np.linalg.norm(kp[i]) > 1.0 for i in needed)


def _arm_angle(kp, side="left"):
    """
    Elbow bend angle (degrees).  90° = fully bent, 180° = straight arm.
    Lower angle → more suspicious (concealment gesture).
    """
    if side == "left":
        s, e, w = kp[LEFT_SHOULDER], kp[LEFT_ELBOW], kp[LEFT_WRIST]
    else:
        s, e, w = kp[RIGHT_SHOULDER], kp[RIGHT_ELBOW], kp[RIGHT_WRIST]

    v1 = s - e
    v2 = w - e
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom < 1e-6:
        return 180.0
    cos_a = np.dot(v1, v2) / denom
    return float(np.degrees(np.arccos(np.clip(cos_a, -1.0, 1.0))))


# ── Core scoring ─────────────────────────────────────────────────
def compute_score(sequence):
    """
    Returns a raw score in [0, 1].
    Higher score  →  more suspicious.
    """
    hand_scores   = []
    motion_values = []
    arm_scores    = []

    prev_lw = prev_rw = None

    for kp in sequence:
        if not _is_valid(kp):
            continue

        torso = _torso_height(kp)
        hip_center = (kp[LEFT_HIP] + kp[RIGHT_HIP]) / 2

        # --- feature 1: normalised hand-to-hip distance ---
        lw_dist = np.linalg.norm(kp[LEFT_WRIST]  - hip_center) / torso
        rw_dist = np.linalg.norm(kp[RIGHT_WRIST] - hip_center) / torso
        # hands close to body are suspicious (concealment)
        # typical relaxed = ~0.8, very close = ~0.2
        hand_score = max(0.0, 1.0 - min(lw_dist, rw_dist) / 0.8)
        hand_scores.append(hand_score)

        # --- feature 2: wrist motion (normalised) ---
        if prev_lw is not None:
            lm = np.linalg.norm(kp[LEFT_WRIST]  - prev_lw) / torso
            rm = np.linalg.norm(kp[RIGHT_WRIST] - prev_rw) / torso
            motion_values.append((lm + rm) / 2)

        prev_lw = kp[LEFT_WRIST].copy()
        prev_rw = kp[RIGHT_WRIST].copy()

        # --- feature 3: arm-bend angle (lower = more bent = suspicious) ---
        l_angle = _arm_angle(kp, "left")
        r_angle = _arm_angle(kp, "right")
        min_angle = min(l_angle, r_angle)
        # map 180° (straight) → 0, 60° (very bent) → 1
        arm_score = max(0.0, (180.0 - min_angle) / 120.0)
        arm_scores.append(arm_score)

    # --- combine ---
    hand_mean   = float(np.mean(hand_scores))   if hand_scores   else 0.0
    motion_var  = float(np.var(motion_values))  if motion_values else 0.0
    arm_mean    = float(np.mean(arm_scores))    if arm_scores    else 0.0

    # motion_var is typically 0–0.05 after normalisation; scale to 0–1
    motion_score = min(1.0, motion_var / 0.02)

    # weighted sum
    raw = (0.45 * hand_mean) + (0.30 * motion_score) + (0.25 * arm_mean)
    return float(np.clip(raw, 0.0, 1.0))


# ── Classification with EMA + hysteresis ─────────────────────────
def classify_sequence(sequence):
    """
    Returns (status_string, smoothed_score).
    Statuses: "NORMAL" | "SUSPICIOUS" | "SHOPLIFTING"
    """
    global _ema_score, _cooldown

    raw = compute_score(sequence)

    # exponential moving average on the score
    _ema_score = EMA_ALPHA * raw + (1.0 - EMA_ALPHA) * _ema_score

    score = _ema_score

    # threshold with hysteresis
    if score > 0.65:
        status = "SHOPLIFTING"
    elif score > 0.38:
        status = "SUSPICIOUS"
    else:
        status = "NORMAL"

    # cooldown: once SHOPLIFTING is triggered, hold it for N frames
    if status == "SHOPLIFTING":
        _cooldown = COOLDOWN_FRAMES
    elif _cooldown > 0:
        status = "SHOPLIFTING"
        _cooldown -= 1

    return status, round(score, 3)
