from asgiref.sync import sync_to_async

from users.models import User
from couple.models import Couple

from django.db import models


@sync_to_async
def create_user(
    first_name: str,
    last_name: str,
    phone_number: str,
    tg_username: str,
    user_id: str,
) -> User:
    return User(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        tg_username=tg_username,
        user_id=user_id,
    ).save()


@sync_to_async
def get_user_by_user_id(user_id: str) -> User | None:
    return User.objects.filter(user_id=user_id).first()
