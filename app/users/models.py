from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField

from common.models import SimpleBaseModel


class User(AbstractBaseUser, SimpleBaseModel):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(max_length=12, unique=True)
    tg_username = models.CharField(max_length=50)
    user_id = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        first_name = self.first_name
        last_name = self.last_name

        full_name = first_name
        if last_name:
            full_name += f" {last_name}"

        return full_name

    @property
    def get_tg_username(self) -> str:
        return f"@{self.tg_username}"
