import os
import logging
from typing import Optional
from google.adk.agents import SequentialAgent, ParallelAgent
from agents.script_parser import create_script_parser_agent
from agents.name_clearance import create_name_clearance_agent
from agents.brand_clearance import create_brand_clearance_agent
from agents.title_clearance import create_title_clearance_agent
from agents.risk_synthesizer import create_risk_synthesizer_agent
from tools.parallel_mcp import create_parallel_toolset

logger = logging.getLogger("greenlight.agents.pipeline")


def build_greenlight_pipeline(model: Optional[str] = None) -> SequentialAgent:
    """Constructs the complete GREENLIGHT multi-agent clearance pipeline in Google ADK.
    
    Architecture:
      Stage 1 (Sequential): ScriptParserAgent extracts character names, brands, titles.
      Stage 2 (Parallel): ParallelAgent runs 3 concurrent clearance specialist agents:
        - NameClearanceAgent (Defamation & Publicity) -> session.state["name_risks"]
        - BrandClearanceAgent (Trademark & Disparagement) -> session.state["brand_risks"]
        - TitleClearanceAgent (Title Collisions & MPAA) -> session.state["title_risks"]
        All three are grounded in live web intelligence via the Parallel Search MCP toolset.
      Stage 3 (Sequential): RiskSynthesizerAgent unifies findings, scores severity,
        and outputs the final ClearanceReport for E&O underwriting.
    """
    chosen_model = model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    logger.info(f"Initializing Parallel MCP Toolset for pipeline with model '{chosen_model}'...")
    parallel_tools = create_parallel_toolset()

    logger.info("Instantiating ADK clearance agents...")
    # Stage 1: Entity Parsing
    parser_agent = create_script_parser_agent(model=chosen_model)

    # Stage 2: Concurrent Clearance Specialists
    name_agent = create_name_clearance_agent(tools=parallel_tools, model=chosen_model)
    brand_agent = create_brand_clearance_agent(tools=parallel_tools, model=chosen_model)
    title_agent = create_title_clearance_agent(tools=parallel_tools, model=chosen_model)

    clearance_team = ParallelAgent(
        name="ParallelClearanceTeam",
        description="Executes concurrent character, brand, and title clearance investigations.",
        sub_agents=[name_agent, brand_agent, title_agent]
    )

    # Stage 3: Risk Synthesis & Underwriting Verdict
    synthesizer_agent = create_risk_synthesizer_agent(model=chosen_model)

    # Composed Root Pipeline
    pipeline = SequentialAgent(
        name="GreenlightClearancePipeline",
        description="End-to-end autonomous script clearance and E&O insurance risk copilot.",
        sub_agents=[parser_agent, clearance_team, synthesizer_agent]
    )

    logger.info("GREENLIGHT multi-agent pipeline successfully constructed.")
    return pipeline
