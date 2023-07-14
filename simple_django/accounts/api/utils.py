from django.conf import settings
from rest_framework.response import Response


def set_refresh_token_cookie(
    response: Response, refresh_token: str, expiry: int = settings.SESSION_COOKIE_AGE
) -> Response:
    kwargs = {
        "key": settings.REFRESH_TOKEN_COOKIE_NAME,
        "value": refresh_token,
        "samesite": settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        "domain": settings.REFRESH_TOKEN_COOKIE_DOMAIN,
    }

    if expiry > 0:
        kwargs["expires"] = expiry

    response.set_cookie(**kwargs)
    return response
