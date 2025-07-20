from pydantic import BaseModel, Field
from typing import Literal, List

class ReasoningStep(BaseModel):
    step: str = Field(description="Name of the reasoning step")
    analysis: str = Field(description="Analysis for this step")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)

class ArticleDecision(BaseModel):
    action: Literal["summarize", "skip", "save_for_later"] = Field(description="Decision action")
    reason: str = Field(description="Main reason for the decision")
    reasoning_chain: List[ReasoningStep] = Field(description="Step by step reasoning", min_items=1)
    confidence: float = Field(description="Overall confidence 0-1", ge=0, le=1)
    key_factors: List[str] = Field(description="Key factors that influenced decision", min_items=1)

class DebateResponse(BaseModel):
    agent_name: str = Field(description="Name of the responding agent")
    response_to: str = Field(description="Which agent they're responding to")
    argument: str = Field(description="Main argument in response")
    counter_points: List[str] = Field(description="Counter-arguments", min_items=1)
    final_stance: ArticleDecision = Field(description="Final decision after debate")
