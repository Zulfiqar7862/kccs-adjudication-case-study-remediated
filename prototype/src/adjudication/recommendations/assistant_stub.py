from __future__ import annotations

class LLMRationaleService:
    """Deterministic local stub. Replace with a governed LLM provider in production."""
    def __init__(self,provider:str="stub",api_key:str|None=None,model:str|None=None):
        self.provider=provider; self.api_key=api_key; self.model=model
    def draft(self,recommendation:dict,evidence_gaps:list[dict])->dict:
        gaps=", ".join(g["gap_type"] for g in evidence_gaps) or "none"
        return {
            "provider":self.provider,
            "model":self.model or "deterministic-stub",
            "prompt_version":"rationale-v1",
            "evidence_summary":f"Recommendation: {recommendation['proposed_disposition']}. Evidence gaps: {gaps}.",
            "uncertainties":[g["gap_type"] for g in evidence_gaps],
            "review_action":recommendation["proposed_disposition"],
        }
