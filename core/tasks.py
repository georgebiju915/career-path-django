# core/tasks.py
from celery import shared_task
from core.mcp import mcp_call
import openai
from django.conf import settings
from core.models import UserProfile

openai.api_key = settings.OPENAI_API_KEY

def generate_roadmap_with_llm(profile_text, trends_text):
    prompt = f"Profile: {profile_text}\nTrends: {trends_text}\nProduce JSON with short_term, mid_term, long_term stages and skills."
    resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], max_tokens=600)
    return resp.choices[0].message.content

@shared_task
def career_planner_agent(user_email, user_id):
    user = UserProfile.objects.get(pk=user_id)
    # simplistic trend placeholder
    trends = "Cloud, IaC, DevOps, ML rising"
    roadmap = generate_roadmap_with_llm(user.resume_text or "", trends)
    # save to Redis audit via MCP
    return mcp_call(user_email, "update_user_roadmap", lambda uid, r: {"saved":True}, user_id, roadmap)
