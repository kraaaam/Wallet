import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    slug = models.CharField(
        default=uuid.uuid4,
        max_length=40,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class User(AbstractUser):
    pass


class Wallet(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Transaction(BaseModel):

    TOPUP = "topup"
    CHARGE = "charge"
    TRANSFER_ADD = "transfer_add"
    TRANSFER_DEDUCT = "transfer_deduct"
    REFUND = "refund"

    TRANSACTION_CHOICES = [
        (TOPUP, "Topup"),
        (CHARGE, "Charge"),
        (TRANSFER_ADD, "Transfer Add"),
        (TRANSFER_DEDUCT, "Transfer Deduct"),
        (REFUND, "Refund"),
    ]

    wallet_obj = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    reference_id = models.CharField(max_length=255)
    amount = models.BigIntegerField(default=0)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    previous_balance = models.BigIntegerField(default=0)
    current_balance = models.BigIntegerField(default=0)
