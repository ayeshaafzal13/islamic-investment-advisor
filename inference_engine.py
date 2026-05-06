"""
INFERENCE ENGINE FOR INVESTMENT ADVISOR
This is the "BRAIN" that:
1. Determines if investment is HALAL or HARAM
2. Checks if investment suits BEGINNERS
3. Calculates risk and return profiles
4. Makes final recommendation
"""

from knowledge_base import INVESTMENT_DATABASE, HALAL_RULES, BEGINNER_RULES

class InvestmentInferenceEngine:
    """
    The core logic engine that makes investment recommendations
    """
    
    def __init__(self):
        self.investment_type = None
        self.user_profile_score = 0  # 0-100
        self.halal_status = None  # HALAL, HARAM, CONDITIONAL
        self.beginner_suitable = None
        self.recommendation = None
        self.reasons = []
        self.warnings = []
    
    # ========== HALAL/HARAM CHECKING ==========
    
    def check_halal_status(self, investment_type):
        """
        Determine if investment is HALAL or HARAM
        This is the MAIN INFERENCE LOGIC
        """
        self.reasons = []
        self.warnings = []
        
        if investment_type not in INVESTMENT_DATABASE:
            return "UNKNOWN"
        
        investment = INVESTMENT_DATABASE[investment_type]
        self.halal_status = investment["halal_status"]
        
        # Add detailed reasoning
        if self.halal_status == "HALAL":
            self.reasons.append(f"✅ {investment['halal_rule']}")
            if "advantage" in investment:
                self.reasons.append(f"   Advantage: {investment['advantage']}")
        
        elif self.halal_status == "HARAM":
            self.warnings.append(f"⚠️ {investment['halal_rule']}")
            if "warning" in investment:
                self.warnings.append(f"   {investment['warning']}")
        
        else:  # CONDITIONAL
            self.reasons.append(f"⚠️ {investment['halal_rule']}")
            if "warning" in investment:
                self.warnings.append(investment['warning'])
        
        return self.halal_status
    
    # ========== BEGINNER SUITABILITY CHECK ==========
    
    def check_beginner_suitability(self, investment_type, user_score):
        """
        Check if investment is suitable for a beginner
        Based on: capital required, volatility, complexity
        """
        if investment_type not in INVESTMENT_DATABASE:
            return False
        
        investment = INVESTMENT_DATABASE[investment_type]
        
        # Factor 1: Is it marked as beginner suitable?
        if not investment["beginner_suitable"]:
            self.reasons.append(f"❌ Not recommended for beginners (requires large capital/expertise)")
            return False
        
        # Factor 2: Check risk level vs user comfort
        risk_level = investment["risk_level"]
        
        if risk_level == "VERY HIGH" and user_score < 70:
            self.warnings.append(f"⚠️ Investment is too risky for your profile (Risk: {risk_level})")
            return False
        
        if risk_level == "HIGH" and user_score < 50:
            self.warnings.append(f"⚠️ Investment may be risky for your profile (Risk: {risk_level})")
            return False
        
        # Factor 3: Return potential matches goals
        if user_score > 0:
            self.reasons.append(f"✅ Suitable capital requirement")
            self.reasons.append(f"✅ Appropriate risk level for you")
            return True
        
        return True
    
    # ========== INVESTMENT ANALYSIS ==========
    
    def analyze_investment(self, investment_type, user_score):
        """
        Complete investment analysis:
        1. Check Halal/Haram
        2. Check beginner suitability
        3. Get risk/return profile
        4. Make recommendation
        """
        self.investment_type = investment_type
        self.user_profile_score = user_score
        self.reasons = []
        self.warnings = []
        
        if investment_type not in INVESTMENT_DATABASE:
            return {
                "status": "UNKNOWN",
                "recommendation": "Investment type not found",
                "confidence": 0.0
            }
        
        investment = INVESTMENT_DATABASE[investment_type]
        
        # STEP 1: Check Halal Status
        halal_status = self.check_halal_status(investment_type)
        
        # STEP 2: Check Beginner Suitability
        is_beginner_suitable = self.check_beginner_suitability(investment_type, user_score)
        
        # STEP 3: Build Recommendation
        recommendation = self._build_recommendation(
            investment,
            halal_status,
            is_beginner_suitable,
            user_score
        )
        
        return recommendation
    
    def _build_recommendation(self, investment, halal_status, is_beginner_suitable, user_score):
        """
        Build final recommendation based on all factors
        """
        # Determine overall recommendation
        if halal_status == "HARAM":
            recommendation_text = "❌ NOT RECOMMENDED - This investment is HARAM (forbidden in Islam)"
            confidence = 0.95
        
        elif not is_beginner_suitable:
            recommendation_text = "❌ NOT RECOMMENDED FOR YOU - Not suitable for beginners"
            confidence = 0.80
        
        elif halal_status == "HALAL":
            if is_beginner_suitable:
                recommendation_text = "✅ RECOMMENDED - Halal and suitable for beginners"
                confidence = 0.90
            else:
                recommendation_text = "✓ HALAL but not ideal for beginners"
                confidence = 0.75
        
        elif halal_status == "CONDITIONAL":
            recommendation_text = "⚠️ CONDITIONAL - Can be halal, requires careful screening"
            confidence = 0.60
        
        return {
            "investment": investment["name"],
            "halal_status": halal_status,
            "beginner_suitable": is_beginner_suitable,
            "recommendation": recommendation_text,
            "confidence": confidence,
            "risk_level": investment["risk_level"],
            "return_level": investment["return_level"],
            "time_horizon": investment["time_horizon"],
            "reasons": self.reasons,
            "warnings": self.warnings
        }
    
    # ========== COMPARISON ==========
    
    def compare_investments(self, investment_list, user_score):
        """
        Compare multiple investments and rank them
        """
        results = []
        
        for investment_type in investment_list:
            result = self.analyze_investment(investment_type, user_score)
            results.append(result)
        
        # Sort by confidence and halal status
        def sort_key(x):
            halal_priority = {
                "HALAL": 3,
                "CONDITIONAL": 1,
                "HARAM": 0
            }
            return (halal_priority.get(x["halal_status"], 0), x["confidence"])
        
        results.sort(key=sort_key, reverse=True)
        return results
    
    def reset(self):
        """Clear engine for new analysis"""
        self.investment_type = None
        self.user_profile_score = 0
        self.halal_status = None
        self.beginner_suitable = None
        self.recommendation = None
        self.reasons = []
        self.warnings = []