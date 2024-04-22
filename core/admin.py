from core.models import Transaction, Wallet
from django.contrib import admin


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "wallet_obj",
        "reference_id",
        "amount",
        "transaction_type",
        "previous_balance",
        "current_balance",
    ]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "wallet_balance"]

    def wallet_balance(self, obj):
        return obj.transactions.last().current_balance
