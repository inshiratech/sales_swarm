"""
Inshira Growth OS - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic models
MODEL_COMPLEX = "claude-opus-4-5"       # Deep reasoning: Agents 1,4,5,7,8,9,10,11,12,14,16
MODEL_VOLUME  = "claude-haiku-4-5"      # High-volume enrichment: Agents 2,3,13,15

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
APOLLO_API_KEY    = os.getenv("APOLLO_API_KEY", "")
HUNTER_API_KEY    = os.getenv("HUNTER_API_KEY", "")

# Business identity
FOUNDER_NAME  = os.getenv("FOUNDER_NAME", "Founder")
COMPANY_NAME  = os.getenv("COMPANY_NAME", "Inshira Technologies")

# CRM data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Lead scoring thresholds
SCORE_PRIORITY_A  = 85   # Strategic account — founder-led
SCORE_PRIORITY_B  = 70   # High fit — standard outreach queue
SCORE_PRIORITY_C  = 55   # Moderate fit — nurture
SCORE_PRIORITY_D  = 40   # Low fit — hold 90 days
# Below 40 = Disqualified

# Outreach sequence rules
MAX_TOUCHES_PER_SEQUENCE = 3
TOUCH_1_DAY = 0
TOUCH_2_DAY = 8
TOUCH_3_DAY = 18

# Trust score thresholds
TRUST_DECAY_WARN   = 30  # days without contact before warning
TRUST_DECAY_FLAG   = 45  # days without contact before flag
TRUST_SCORE_STAGES = {
    "Cold":     (0,  20),
    "Aware":    (21, 40),
    "Engaged":  (41, 60),
    "Trusting": (61, 80),
    "Partner":  (81, 100),
}

# Pilot ARR thresholds
HIGH_VALUE_ARR_THRESHOLD = 50_000   # £ — triggers deep research + founder-led mode
EXPANSION_ARR_THRESHOLD  = 25_000   # £ — triggers Checkpoint 8

# Subscription tiers (reference ranges)
SUBSCRIPTION_TIERS = {
    "Starter":    (12_000,  25_000),
    "Standard":   (25_000,  60_000),
    "Advanced":   (60_000, 120_000),
    "Enterprise": (120_000, None),
}
