# core/tools.py
from core.neo4j_client import create_skill
def update_skill_graph(updates: dict):
    # updates: {"skills":["Terraform","Kubernetes"], "role":"DevOps"}
    for s in updates.get("skills", []):
        create_skill(s)
    return True

def fetch_user_profile(user_id):
    from core.models import UserProfile
    u = UserProfile.objects.get(pk=user_id)
    return {"id": u.id, "skills": u.skills, "resume": u.resume_text}
