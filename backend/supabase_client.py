import os

from dotenv import load_dotenv

load_dotenv()

_client = None


def is_configured():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.environ.get(
        "SUPABASE_KEY", ""
    ).strip()
    return bool(url and key)


def get_client():
    global _client
    if _client is not None:
        return _client

    if not is_configured():
        return None

    from supabase import create_client

    url = os.environ["SUPABASE_URL"].strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ["SUPABASE_KEY"].strip()
    )
    _client = create_client(url, key)
    return _client
