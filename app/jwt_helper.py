import jwt
from django.conf import settings
from django.utils import timezone

KEY = settings.JWT["SIGNING_KEY"]
ALGORITHM = settings.JWT["ALGORITHM"]
ACCESS_TOKEN_LIFETIME = settings.JWT["ACCESS_TOKEN_LIFETIME"]


def create_access_token(user_id):
    payload = {
        "token_type": "access",
        "exp": timezone.now() + ACCESS_TOKEN_LIFETIME,
        "iat": timezone.now(),
    }
    payload["user_id"] = user_id
    token = jwt.encode(payload, KEY, algorithm=ALGORITHM)
    return token


def get_jwt_payload(token):
    payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
    return payload


def get_access_token(request):
    if request.headers.get("Authorization"):
        return request.headers.get("Authorization")

    return request.COOKIES.get('access_token')