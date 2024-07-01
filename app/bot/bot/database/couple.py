from asgiref.sync import sync_to_async

from users.models import User
from couple.models import Couple, Wish

from django.db import models

import datetime


@sync_to_async
def create_couple(user_1: User) -> Couple:
    return Couple.objects.create(user_1=user_1)


@sync_to_async
def join_to_couple(couple: Couple, user: User) -> bool:
    return couple.join_to_couple(user)


@sync_to_async
def leave_from_couple(couple: Couple, user: User) -> bool:
    return couple.leave_from_couple(user)


@sync_to_async
def reset_date_start(couple: Couple) -> None:
    return couple.reset_date_start()


@sync_to_async
def set_date_start(couple: Couple, date_start: datetime.date) -> None:
    return couple.set_date_start(date_start)


@sync_to_async
def get_couple_user(couple: Couple, user: User) -> User | None:
    return couple.couple_user(user)


@sync_to_async
def get_couple_by_unique_id(unique_id: str) -> Couple | None:
    return Couple.objects.filter(unique_id=unique_id).first()


@sync_to_async
def get_user_couple(user: User) -> Couple | None:
    if user is not None:
        return (
            Couple.objects.filter(models.Q(user_1=user) | models.Q(user_2=user))
            .select_related("user_1", "user_2")
            .first()
        )


@sync_to_async
def create_wish(
    couple: Couple, user: User, description: str, date_to: datetime.date = None
) -> Wish:
    wish = Wish.objects.create(user=user, description=description, date_to=date_to)
    return wish


@sync_to_async
def get_user_wishes(user: User) -> list[Wish]:
    return list(Wish.objects.filter(user=user))


@sync_to_async
def get_wish_by_id(wish_id: int) -> Wish | None:
    return Wish.objects.filter(id=wish_id).select_related("user").first()


@sync_to_async
def save_wish(wish: Wish, data: dict = None) -> None:
    if data:
        for key, value in data.items():
            setattr(wish, key, value)
    wish.save()


@sync_to_async
def delete_wish(wish: Wish) -> None:
    wish.delete()
