from typing import Any, Iterable
import datetime
from django.db import models
from common.models import SimpleBaseModel
from django.utils.crypto import get_random_string

from django.db.models.manager import BaseManager

from users.models import User


class CoupleManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        kwargs["unique_id"] = get_random_string(length=10)
        return super().create(**kwargs)


class Couple(SimpleBaseModel):
    unique_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )
    user_1 = models.OneToOneField(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="couple_1",
    )
    user_2 = models.OneToOneField(
        "users.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="couple_2",
    )
    date_start = models.DateField(
        verbose_name="Дата начала отношений", null=True, blank=True
    )

    objects = CoupleManager()

    def save(self, *args, **kwargs) -> None:
        user_1 = self.user_1
        user_2 = self.user_2

        if (user_1 is not None and user_2 is not None) and (user_1 is user_2):
            raise ValueError("Два участника пары не могут быть одним пользователем")

        return super().save(*args, **kwargs)

    def join_to_couple(self: "Couple", user: "User") -> bool:
        try:
            if self.user_1 is None:
                self.user_1 = user
            elif self.user_2 is None:
                self.user_2 = user
            else:
                return False
            self.save()
        except:
            return False
        return True

    def leave_from_couple(self: "Couple", user: "User") -> bool:
        if self.user_1 == user:
            self.user_1 = None
        elif self.user_2 == user:
            self.user_2 = None
        self.save()
        return True

    def couple_user(self: "Couple", user: "User") -> User | None:
        return self.user_1 if self.user_1 not in [user, None] else self.user_2

    @property
    def formatted_date_start(self) -> str:
        return self.date_start.strftime("%d.%m.%Y") if self.date_start else ""

    def reset_date_start(self):
        self.date_start = None
        self.save()

    def set_date_start(self, date_start: datetime.date):
        self.date_start = date_start
        self.save()


class Wish(SimpleBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Описание желания")
    date_to = models.DateField(
        null=True, blank=True, verbose_name="Дата, когда желание должно испольниться"
    )

    @property
    def formatted_date_to(self) -> str:
        return self.date_to.strftime("%d.%m.%Y") if self.date_to else ""
