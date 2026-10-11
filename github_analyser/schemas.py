from pydantic import BaseModel, Field


class ProjectInsight(BaseModel):
    repo_name: str = Field(description="Exact name of one of the repositories in the data")
    comment: str = Field(description="One or two sentences about this repository")


class GitHubReport(BaseModel):
    """The shape the LLM must answer in. LangChain turns this into a typed object for us."""

    overall_summary: str = Field(description="2-3 sentences about the profile as a whole")
    strengths: list[str] = Field(description="3-5 specific things the profile does well")
    weaknesses: list[str] = Field(description="3-5 specific things that could be better")
    recommendations: list[str] = Field(description="3-5 concrete next steps")
    project_insights: list[ProjectInsight] = Field(
        description="Comments on up to 3 standout repositories. Use an empty list if none stand out."
    )
    action_plan: list[str] = Field(description="Ordered steps to raise the score, most impactful first")