import os
import google.auth
from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List

# --- GCP Configuration ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# --- Define the Strict Output Structure ---
# This Pydantic model defines the exact JSON structure we want.
class CompanyReport(BaseModel):
    official_name: str = Field(description="The official, legal name of the company.")
    description: str = Field(description="A one-paragraph summary of the company.")
    industry: str = Field(description="The primary industry the company operates in.")
    founders: List[str] = Field(description="A list of the company's founders.")
    ceo: str = Field(description="The current Chief Executive Officer.")
    products: List[str] = Field(description="A list of the company's main products or services.")
    geographical_location: str = Field(description="The city and country of the company's headquarters.")
    employee_size: str = Field(description="The approximate number of employees.")
    pricing_plans: List[str] = Field(description="Descriptions of the company's pricing tiers, if available.")
    funding: str = Field(description="Funding rounds or total amount raised, if available.")
    valuation: str = Field(description="Current company valuation, if known.")
    release_date: str = Field(description="Date the company or main product was first released.")
    alternatives: List[str] = Field(description="Alternative companies or services.")


# --- Agent Definition ---
JsonFormattingAgent = Agent(
    name="JsonFormattingAgent",
    model="gemini-2.0-flash-001",
    instruction="""
    You are a data formatting expert. You will receive a block of unstructured text.
    Your sole purpose is to analyze the text and extract the required information,
    populating it into the structured output format.
    If you cannot find a value for a field, use the string 'Not Found'.
    """,
    # This agent has NO tools. Its only job is to format.
    tools=[],
    # This forces the agent's final output to match the CompanyReport Pydantic model.
    output_schema=CompanyReport,
)

root_agent = JsonFormattingAgent