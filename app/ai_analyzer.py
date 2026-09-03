import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_ai_report(profile_data):
    prompt = f"""
You are a GitHub profile reviewer.

Analyze the following GitHub profile data:

Username: {profile_data["username"]}
Followers: {profile_data["followers"]}
Following: {profile_data["following"]}
Repositories: {profile_data["repository_count"]}
Total Stars: {profile_data["total_stars"]}
Total Forks: {profile_data["total_forks"]}
Most Used Language: {profile_data["most_used_language"]}
Languages: {profile_data["languages"]}
Repositories With Descriptions: {profile_data["repositories_with_descriptions"]}
Total Topics: {profile_data["total_topics"]}
Active Repositories: {profile_data["active_repositories"]}
Profile Score: {profile_data["profile_score"]}/100

Give a concise professional report with these sections:

1. Overall Assessment
2. Strengths
3. Weaknesses
4. Recommendations
5. Next 3 Actions

Focus on practical advice that would help the developer improve their GitHub profile and portfolio.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text