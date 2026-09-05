from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RiskSeverity(str, Enum):
    HIGH = "HIGH"          # Blocks E&O insurance binding; immediate legal liability
    MEDIUM = "MEDIUM"      # Requires clearance review, license negotiation, or script tweak
    LOW = "LOW"            # Advisory / low probability of claim; standard disclaimer advised


class RiskCategory(str, Enum):
    NAME = "NAME"          # Defamation, right of publicity, living person collision
    BRAND = "BRAND"        # Trademark infringement, negative product disparagement
    TITLE = "TITLE"        # Title collision, confusing similarity, registered MPAA conflict
    PROP_OTHER = "PROP"    # Phone numbers, real addresses, confidential artwork/docs


class CharacterEntity(BaseModel):
    name: str = Field(..., description="Character name as it appears in script")
    role: str = Field(default="", description="Role or profession in story (e.g. corrupt CEO, detective)")
    scenes: List[str] = Field(default_factory=list, description="Scene headings or page numbers where character appears")
    context: str = Field(default="", description="Key context or actions that could trigger liability")


class BrandEntity(BaseModel):
    brand_name: str = Field(..., description="Brand or trademarked product name mentioned or shown")
    product_type: str = Field(default="", description="Type of product (e.g. luxury watch, automobile, smartphone)")
    scenes: List[str] = Field(default_factory=list, description="Scene headings or page numbers")
    depiction_context: str = Field(default="", description="How the brand is depicted: positive, neutral, or disparaging/malfunctioning")


class TitleEntity(BaseModel):
    title_name: str = Field(..., description="Working title or referenced artwork/media title")
    entity_type: str = Field(default="project_title", description="project_title, movie_reference, book_reference, song_reference")
    context: str = Field(default="", description="Usage context")


class ParsedScript(BaseModel):
    title: str = Field(default="Untitled Screenplay", description="Working title of the screenplay")
    logline: str = Field(default="", description="1-2 sentence core premise/logline")
    genre: str = Field(default="Drama", description="Primary genre")
    characters: List[CharacterEntity] = Field(default_factory=list, description="Extracted characters")
    brands: List[BrandEntity] = Field(default_factory=list, description="Extracted brands and products")
    referenced_titles: List[TitleEntity] = Field(default_factory=list, description="Referenced media titles")
    real_world_locations: List[str] = Field(default_factory=list, description="Real locations mentioned")
    flagged_numbers_addresses: List[str] = Field(default_factory=list, description="Real phone numbers, URLs, or specific addresses")


class SourceCitation(BaseModel):
    title: str = Field(..., description="Page title or source name")
    url: str = Field(..., description="Live verifiable URL from Parallel Web Search")
    snippet: str = Field(default="", description="Verbatim citation passage extracted from the source")


class RiskItem(BaseModel):
    id: str = Field(..., description="Unique risk identifier (e.g. RISK-NAME-01)")
    entity: str = Field(..., description="The name, brand, or title that triggered the risk")
    category: RiskCategory = Field(..., description="Category of clearance risk")
    severity: RiskSeverity = Field(..., description="Clearance severity level")
    scene_or_page: str = Field(default="", description="Script location or scene reference")
    description: str = Field(..., description="Detailed legal and clearance risk analysis")
    sources: List[SourceCitation] = Field(default_factory=list, description="Source citations from Parallel Web Search")
    recommended_action: str = Field(..., description="Specific recommended clearance fix for the producer / writer")


class SummaryStats(BaseModel):
    total_flags: int = 0
    high_severity: int = 0
    medium_severity: int = 0
    low_severity: int = 0
    turnaround_saved: str = "5–10 Business Days"


class ClearanceReport(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis job ID")
    script_title: str = Field(..., description="Title of the screenplay analyzed")
    greenlight_score: int = Field(..., description="Clearance readiness score from 0 (High Risk) to 100 (Clean)")
    verdict: str = Field(..., description="GREENLIGHT, CONDITIONAL GREENLIGHT, or RED FLAG - ACTION REQUIRED")
    underwriting_summary: str = Field(..., description="Executive memo formatted for E&O insurance underwriters")
    stats: SummaryStats = Field(default_factory=SummaryStats)
    risks: List[RiskItem] = Field(default_factory=list)
    parsed_script: Optional[ParsedScript] = None
    execution_mode: str = Field(default="deterministic_engine", description="Execution mode: 'live_gemini_adk' or 'deterministic_engine'")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AnalysisRequest(BaseModel):
    script_text: str = Field(..., description="Full or excerpt screenplay text")
    script_title: Optional[str] = Field(default=None, description="Optional title override")


class PipelineStatusEvent(BaseModel):
    analysis_id: str
    stage: str
    stage_index: int
    total_stages: int
    message: str
    completed: bool = False
