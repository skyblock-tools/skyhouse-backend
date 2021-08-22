from utils.misc import generate_token


def user_payload(_id, **kwargs):
    return {
        "_id": str(_id),
        # levelling data
        "experience": 0,
        "level": 1,
        "last_message": 0,
        # auth data
        "privilege_level": 1,
        "ratelimit_minute": 6,
        "web_refresh_token": None,
        "web_refresh_token_generated": 0,
        "session_token": None,
        "mod_refresh_token": generate_token(),
        # misc data
        "vc_minutes": 0,
        **kwargs,
    }
