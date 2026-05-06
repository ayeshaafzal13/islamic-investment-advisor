"""
KNOWLEDGE BASE FOR INVESTMENT ADVISOR EXPERT SYSTEM
This file contains all rules about:
1. Which investments are Halal/Haram (Islamic Finance)
2. Which investments suit beginners
3. Risk levels and returns
"""

# ============================================================
# INVESTMENT KNOWLEDGE BASE
# ============================================================

INVESTMENT_DATABASE = {
    "stocks": {
        "name": "Stock (Company Share)",
        "description": "Ownership share in a company",
        "halal_status": "CONDITIONAL",  # Can be halal or haram
        "halal_rule": "Check if company business is halal",
        "common_halal_companies": ["Tech companies", "Real estate", "Retail", "Food (halal)"],
        "common_haram_companies": ["Alcohol", "Gambling", "Pork", "Adult entertainment"],
        "beginner_suitable": True,
        "risk_level": "HIGH",
        "return_level": "HIGH",
        "time_horizon": "5+ years",
        "confidence": 0.70
    },
    
    "bonds_regular": {
        "name": "Regular Bonds (Government/Corporate)",
        "description": "Loan to government or company with interest",
        "halal_status": "HARAM",  # Definitely haram
        "halal_rule": "Contains interest (Riba) - forbidden in Islam",
        "beginner_suitable": True,
        "risk_level": "LOW",
        "return_level": "LOW",
        "time_horizon": "10+ years",
        "confidence": 1.0,
        "warning": "INTEREST-BASED - NOT ALLOWED IN ISLAM"
    },
    
    "sukuk": {
        "name": "Sukuk (Islamic Bond)",
        "description": "Asset-backed Islamic bond with profit sharing",
        "halal_status": "HALAL",  # Definitely halal
        "halal_rule": "No interest, asset-backed, profit-sharing",
        "beginner_suitable": True,
        "risk_level": "MODERATE",
        "return_level": "MODERATE",
        "time_horizon": "5-10 years",
        "confidence": 1.0,
        "advantage": "HALAL ALTERNATIVE TO BONDS"
    },
    
    "mutual_funds_islamic": {
        "name": "Islamic Mutual Fund",
        "description": "Pool of halal investments managed professionally",
        "halal_status": "HALAL",
        "halal_rule": "Only contains halal companies and assets",
        "beginner_suitable": True,
        "risk_level": "MODERATE",
        "return_level": "MODERATE",
        "time_horizon": "3+ years",
        "confidence": 0.95,
        "advantage": "BEST FOR BEGINNERS - DIVERSIFIED & PROFESSIONAL"
    },
    
    "mutual_funds_regular": {
        "name": "Regular Mutual Fund",
        "description": "Mix of stocks and bonds from any company",
        "halal_status": "CONDITIONAL",
        "halal_rule": "Check if fund contains interest-based bonds",
        "beginner_suitable": True,
        "risk_level": "MODERATE",
        "return_level": "MODERATE",
        "time_horizon": "3+ years",
        "confidence": 0.60,
        "warning": "MAY CONTAIN HARAM BONDS - CHECK HOLDINGS"
    },
    
    "gold_silver": {
        "name": "Gold/Silver (Commodities)",
        "description": "Physical precious metals or commodity futures",
        "halal_status": "HALAL",
        "halal_rule": "Tangible asset, good Islamic investment",
        "beginner_suitable": True,
        "risk_level": "MODERATE",
        "return_level": "MODERATE",
        "time_horizon": "5+ years",
        "confidence": 0.90,
        "advantage": "PHYSICAL ASSET - VERY HALAL"
    },
    
    "real_estate": {
        "name": "Real Estate (Property)",
        "description": "Buying land, buildings, or rental properties",
        "halal_status": "HALAL",
        "halal_rule": "Physical asset, allowed if used for halal purposes",
        "beginner_suitable": False,  # Needs capital
        "risk_level": "MODERATE",
        "return_level": "HIGH",
        "time_horizon": "10+ years",
        "confidence": 0.95,
        "note": "REQUIRES LARGE CAPITAL - NOT IDEAL FOR BEGINNERS"
    },
    
    "forex_trading": {
        "name": "Forex Trading (Currency Trading)",
        "description": "Speculating on currency exchange rates",
        "halal_status": "HARAM",
        "halal_rule": "Excessive uncertainty (Gharar) and speculation",
        "beginner_suitable": False,
        "risk_level": "VERY HIGH",
        "return_level": "VERY HIGH",
        "time_horizon": "Short-term",
        "confidence": 0.95,
        "warning": "HARAM - EXCESSIVE SPECULATION & RISK"
    },
    
    "gambling": {
        "name": "Gambling/Betting",
        "description": "Betting money on uncertain outcomes",
        "halal_status": "HARAM",
        "halal_rule": "Forbidden in Islam - considered theft in many views",
        "beginner_suitable": False,
        "risk_level": "VERY HIGH",
        "return_level": "VERY HIGH",
        "time_horizon": "Immediate",
        "confidence": 1.0,
        "warning": "HARAM - ABSOLUTELY FORBIDDEN"
    },
    
    "savings_account": {
        "name": "Savings Account (with Interest)",
        "description": "Bank savings earning interest/returns",
        "halal_status": "HARAM",
        "halal_rule": "Interest (Riba) is forbidden in Islam",
        "beginner_suitable": True,
        "risk_level": "VERY LOW",
        "return_level": "VERY LOW",
        "time_horizon": "Any",
        "confidence": 1.0,
        "warning": "INTEREST-BASED - NOT HALAL",
        "alternative": "Islamic Savings Account (no interest)"
    },
    
    "crypto": {
        "name": "Cryptocurrency (Bitcoin, etc.)",
        "description": "Digital currency and blockchain assets",
        "halal_status": "CONDITIONAL",
        "halal_rule": "Scholars disagree - many consider it too speculative",
        "beginner_suitable": False,
        "risk_level": "VERY HIGH",
        "return_level": "VERY HIGH",
        "time_horizon": "Short-term",
        "confidence": 0.40,
        "warning": "CONTROVERSIAL - AVOID AS BEGINNER"
    }
}

# ============================================================
# QUESTIONS TO ASK USER
# ============================================================

BEGINNER_PROFILE_QUESTIONS = [
    {
        "id": 1,
        "question": "How much money do you have to invest?",
        "type": "amount",
        "options": ["Less than $1,000", "$1,000-$5,000", "$5,000-$10,000", "More than $10,000"],
        "scores": [0, 25, 50, 75]
    },
    {
        "id": 2,
        "question": "How long can you wait before needing the money?",
        "type": "time",
        "options": ["Less than 1 year", "1-3 years", "3-5 years", "5+ years"],
        "scores": [10, 30, 60, 100]
    },
    {
        "id": 3,
        "question": "Can you tolerate losses (market going down)?",
        "type": "risk",
        "options": ["Very uncomfortable with losses", "Somewhat uncomfortable", "Moderate comfort", "Very comfortable"],
        "scores": [10, 30, 60, 100]
    },
    {
        "id": 4,
        "question": "What is your investment goal?",
        "type": "goal",
        "options": ["Preserve money (keep it safe)", "Slow growth", "Moderate growth", "High growth"],
        "scores": [20, 40, 70, 100]
    },
    {
        "id": 5,
        "question": "Is it important that your investment is Halal (Islamic)?",
        "type": "islamic",
        "options": ["Not important", "Somewhat important", "Very important", "Absolutely essential"],
        "scores": [0, 30, 70, 100]
    }
]

# ============================================================
# HALAL/HARAM CLASSIFICATION RULES
# ============================================================

HALAL_RULES = [
    {
        "rule_id": 1,
        "name": "No Riba (Interest)",
        "description": "Investment must not earn or pay interest",
        "haram_keywords": ["interest", "bond", "savings account", "fixed return"],
        "halal_keywords": ["equity", "partnership", "property", "sukuk", "profit sharing"]
    },
    {
        "rule_id": 2,
        "name": "No Gharar (Speculation)",
        "description": "Investment must not be pure speculation",
        "haram_keywords": ["forex", "gambling", "betting", "options", "very high risk"],
        "halal_keywords": ["real estate", "stocks", "mutual fund", "moderate risk"]
    },
    {
        "rule_id": 3,
        "name": "No Haram Businesses",
        "description": "Company must not be in forbidden industries",
        "haram_keywords": ["alcohol", "pork", "gambling", "adult", "tobacco", "conventional bank"],
        "halal_keywords": ["tech", "real estate", "food", "retail", "manufacturing", "services"]
    },
    {
        "rule_id": 4,
        "name": "Asset-Backed",
        "description": "Investment should be backed by real assets",
        "haram_keywords": ["pure speculation", "no underlying asset"],
        "halal_keywords": ["real estate", "gold", "property", "business", "sukuk"]
    }
]

# ============================================================
# BEGINNER SUITABILITY RULES
# ============================================================

BEGINNER_RULES = [
    {
        "id": 1,
        "criteria": "Low capital required",
        "suitable_investments": ["stocks", "mutual_funds_islamic", "mutual_funds_regular", "sukuk"],
        "unsuitable_investments": ["real_estate", "large_commodity_positions"]
    },
    {
        "id": 2,
        "criteria": "Not highly volatile",
        "suitable_investments": ["mutual_funds_islamic", "sukuk", "gold_silver"],
        "unsuitable_investments": ["forex_trading", "crypto", "options"]
    },
    {
        "id": 3,
        "criteria": "Easy to understand",
        "suitable_investments": ["stocks", "mutual_funds_islamic", "real_estate", "gold_silver"],
        "unsuitable_investments": ["forex_trading", "crypto", "derivatives"]
    },
    {
        "id": 4,
        "criteria": "Professional management available",
        "suitable_investments": ["mutual_funds_islamic", "mutual_funds_regular", "stocks"],
        "unsuitable_investments": ["forex_trading", "crypto", "gambling"]
    }
]