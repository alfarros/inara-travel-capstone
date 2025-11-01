# /module_4_lead_scoring/app/schemas.py
from pydantic import BaseModel
from typing import Optional

# MENGAPA: Skema input HARUS mencerminkan data MENTAH
# sebelum preprocessing (seperti data dari form/CRM).
class LeadFeaturesInput(BaseModel):
    lead_source: str # e.g., 'Google', 'Facebook', 'Referral'
    pages_viewed: int
    time_on_site_sec: float
    visited_pricing_page: int # 1 or 0
    form_submission_count: int
    email_opened_count: int
    recency_visit_days: int
    # Tambahkan fitur lain jika ada

class ScoringResponse(BaseModel):
    lead_id: str
    score: int # Probabilitas konversi (0-100)
    is_hot_lead: bool
    reason: Optional[str] = None # Penjelasan SHAP