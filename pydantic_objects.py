from pydantic import BaseModel, Field
from typing import List

class SyntaxStyleEvaluation(BaseModel):
    """Pydantic model for syntax and style evaluation results"""
    syntax_score: int = Field(..., ge=0, le=60, description="Score for syntax correctness out of 60 points")
    style_score: int = Field(..., ge=0, le=40, description="Score for readability and style out of 40 points")
    syntax_feedback: str = Field(..., description="Explanation of the syntax score")
    style_feedback: str = Field(..., description="Explanation of the style score")
    syntax_improvements: List[str] = Field(..., description="Suggestions to improve syntax")
    style_improvements: List[str] = Field(..., description="Suggestions to improve style")

class RequirementsEvaluation(BaseModel):
    """Pydantic model for requirements evaluation results"""
    requirements_score: int = Field(..., ge=0, le=100, description="Overall score for requirements fulfillment out of 100 points")
    overall_assessment: str = Field(..., description="Overall assessment of how well the code meets requirements")
    strengths: List[str] = Field(..., description="Key strengths of the code regarding requirements")
    weaknesses: List[str] = Field(..., description="Key weaknesses of the code regarding requirements")
    improvement_suggestions: List[str] = Field(..., description="Specific suggestions to better meet requirements")

class VisualizationEvaluation(BaseModel):
    """Pydantic model for visualization evaluation results"""
    visualization_score: int = Field(..., ge=0, le=100, description="Overall score for visualizations out of 100 points")
    clarity_assessment: str = Field(..., description="Assessment of visual clarity (labels, titles, appropriate chart types)")
    insight_assessment: str = Field(..., description="Assessment of how well the visualizations generate insights")
    technical_assessment: str = Field(..., description="Assessment of technical implementation of visualizations")
    strengths: List[str] = Field(..., description="Key strengths of the visualizations")
    improvement_suggestions: List[str] = Field(..., description="Specific suggestions to improve visualizations")