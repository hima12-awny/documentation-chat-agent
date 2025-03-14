from typing import Optional
from pydantic import BaseModel, Field


class ContextSourceFormatter(BaseModel):

    source: str = Field(
        description='Name of the file providing relevant information.'
    )

    source_last_updated: str = Field(
        description='Date of the last update to the source file.'
    )

    source_url: str = Field(
        description='URL to the source file for direct access. BE ACCURATE.'
    )


class ResponseFormatter(BaseModel):

    ai_response: str = Field(
        description="The AI-generated response to the user's query."
    )

    search_query: Optional[str] = Field(
        default=None,
        description='Min 30 words Search Query to get the most relevant info.'
    )

    context_sources: Optional[list[ContextSourceFormatter]] = Field(
        default=None,
        description='**Unique** sources used in the response, including name, last updated date, and URL.'
    )
