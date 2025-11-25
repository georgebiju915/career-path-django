# core/mcp.py
import json
from django.conf import settings
from django.utils import timezone
from core.models import UserProfile
import redis
r = redis.from_url(settings.REDIS_URL)

class Policy:
    @staticmethod
    def allow(user_email, tool_name):
        # stub: allow all except send_email
        if tool_name == "send_email" and user_email != "admin@example.com":
            return False
        return True

def audit_log(entry: dict):
    entry["ts"] = timezone.now().isoformat()
    r.rpush("mcp:audits", json.dumps(entry))

def mcp_call(user_email: str, tool_name: str, tool_fn, *args, **kwargs):
    if not Policy.allow(user_email, tool_name):
        audit_log({"user": user_email, "tool": tool_name, "status": "denied"})
        raise PermissionError("Policy denies this tool call")
    audit_log({"user": user_email, "tool": tool_name, "status": "start", "args": str(args)})
    res = tool_fn(*args, **kwargs)
    audit_log({"user": user_email, "tool": tool_name, "status": "done", "result_summary": str(res)[:500]})
    return res
