from app.jwt_helper import get_access_token, get_jwt_payload
from app.models import CustomUser


def identity_user(request):
    access_token = get_access_token(request)

    if access_token is None:
        return None

    payload = get_jwt_payload(access_token)
    user_id = payload["user_id"]
    user = CustomUser.objects.get(pk=user_id)

    return user
