from event.services import send_event

from .models import Transaction, Wallet


def get_wallet_balance(*, wallet_id: int) -> int:
    transaction = (
        Transaction.objects.filter(wallet_obj__id=wallet_id)
        .order_by("created_at")
        .last()
    )
    return transaction.current_balance if transaction else 0


def wallet_charge(*, wallet_id: int, amount: int, reference_id: str) -> Transaction:
    wallet = Wallet.objects.get(id=wallet_id)

    current_balance = get_wallet_balance(wallet_id=wallet_id) - amount
    if current_balance < 0:
        raise ValueError("Insufficient balance")

    transaction = Transaction.objects.create(
        wallet_obj=wallet,
        reference_id=reference_id,
        amount=amount,
        transaction_type=Transaction.CHARGE,
        previous_balance=get_wallet_balance(wallet_id=wallet_id),
        current_balance=get_wallet_balance(wallet_id=wallet_id) - amount,
    )

    return transaction


def wallet_event_charge(
    *, wallet_id: int, amount: int, reference_id: str
) -> Transaction:

    send_event(
        topic="wallet",
        action="charge",
        key=wallet_id,
        value={"wallet_id": wallet_id, "amount": amount, "reference_id": reference_id},
    )

    return True
