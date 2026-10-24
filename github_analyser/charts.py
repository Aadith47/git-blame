import plotly.express as px
import plotly.graph_objects as go

from github_analyser.analytics import Analytics


def language_chart(analytics: Analytics) -> go.Figure:
    counts = sorted(analytics.facts.languages.items(), key=lambda item: item[1])
    fig = px.bar(
        x=[count for _, count in counts],
        y=[language for language, _ in counts],
        orientation="h",
        labels={"x": "Repositories", "y": ""},
    )
    fig.update_layout(title="Languages")
    return fig


def stars_chart(analytics: Analytics, top_n: int = 10) -> go.Figure:
    top = analytics.originals.nlargest(top_n, "stars").sort_values("stars")
    fig = px.bar(top, x="stars", y="name", orientation="h", labels={"stars": "Stars", "name": ""})
    fig.update_layout(title=f"Top {len(top)} repositories by stars")
    return fig


def activity_chart(analytics: Analytics) -> go.Figure:
    months = analytics.originals["last_push"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    monthly = months.value_counts().sort_index().rename_axis("month").reset_index(name="repositories")
    fig = px.bar(monthly, x="month", y="repositories", labels={"month": "Month", "repositories": "Repos"})
    fig.update_layout(title="Last push, by month")
    return fig


def age_chart(analytics: Analytics) -> go.Figure:
    fig = px.histogram(analytics.originals, x="created_at", nbins=20, labels={"created_at": "Created"})
    fig.update_layout(title="When the repositories were created", yaxis_title="Repositories")
    return fig


def documentation_chart(analytics: Analytics) -> go.Figure:
    facts = analytics.facts
    coverage = {
        "README": facts.readme_ratio,
        "Description": facts.description_ratio,
        "Topics": facts.topics_ratio,
        "License": facts.license_ratio,
    }
    fig = px.bar(
        x=list(coverage),
        y=[ratio * 100 for ratio in coverage.values()],
        labels={"x": "", "y": "% of repositories"},
    )
    fig.update_layout(title="Documentation coverage", yaxis_range=[0, 100])
    return fig