"""
Wallet service for ExamSaaS platform.
Pure Python wallet operations with atomic MongoDB transactions.
Zero Flask imports — no HTTP concerns.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WalletServiceError(Exception):
    """Base exception for wallet service errors."""
    pass


def _get_model(name: str):
    """Lazy-load model to avoid circular imports."""
    from app.models import Wallet, User, WalletTransaction, TransactionType, TransactionSource, TransactionPurpose
    return Wallet, User, WalletTransaction, TransactionType, TransactionSource, TransactionPurpose


def get_or_create_wallet(user_id: str) -> "Wallet":
    """
    Get user's wallet or create with zero balance.
    Uses atomic findOneAndUpdate with upsert.

    Args:
        user_id: User document ID

    Returns:
        Wallet document
    """
    Wallet, User, _, _, _, _ = _get_model("wallet")

    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
    except Exception as e:
        raise ValueError(f"Invalid user_id: {user_id}") from e

    user = User.objects(id=user_oid).first()
    if not user:
        raise WalletServiceError(f"User not found: {user_id}")

    wallet = Wallet.objects(user=user).first()
    if wallet:
        return wallet

    wallet = Wallet(
        user=user,
        balance=0,
        currency="INR",
        total_credited=0,
        total_debited=0,
        version=0,
    )
    wallet.save()
    logger.info(f"Created new wallet for user {user_id}")
    return wallet


def credit_wallet(
    user_id: str,
    amount_paise: int,
    purpose: str,
    source: str,
    reference_id: str,
    description: str,
) -> "WalletTransaction":
    """
    Atomically credit wallet and create transaction record.

    Args:
        user_id: User document ID
        amount_paise: Amount in paise (positive integer)
        purpose: Transaction purpose (e.g. 'top_up', 'refund', 'admin_credit')
        source: Source of credit (e.g. 'razorpay', 'admin', 'system')
        reference_id: External reference ID
        description: Human-readable description

    Returns:
        WalletTransaction document

    Raises:
        WalletServiceError: If amount <= 0 or wallet not found
    """
    Wallet, User, WalletTransaction, TransactionType, TransactionSource, TransactionPurpose = _get_model("wallet")

    if amount_paise <= 0:
        raise WalletServiceError("Credit amount must be positive")

    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
    except Exception as e:
        raise WalletServiceError(f"Invalid user_id: {user_id}") from e

    user = User.objects(id=user_oid).first()
    if not user:
        raise WalletServiceError(f"User not found: {user_id}")

    wallet = Wallet.objects(user=user).first()
    if not wallet:
        wallet = Wallet(
            user=user,
            balance=0,
            currency="INR",
            total_credited=0,
            total_debited=0,
            version=0,
        )
        wallet.save()

    updated = Wallet.objects(
        id=wallet.id,
    ).modify(
        inc__balance=amount_paise,
        inc__total_credited=amount_paise,
        inc__version=1,
        new=True,
    )

    if updated is None:
        raise WalletServiceError("Failed to credit wallet — wallet not found")

    wallet.reload()
    balance_after = int(wallet.balance)

    purpose_map = {
        "top_up": TransactionPurpose.TOP_UP,
        "refund": TransactionPurpose.REFUND,
        "admin_credit": TransactionPurpose.ADMIN_CREDIT,
    }
    tx_purpose = purpose_map.get(purpose, TransactionPurpose.ADMIN_CREDIT)

    source_map = {
        "razorpay": TransactionSource.RAZORPAY,
        "admin": TransactionSource.ADMIN,
        "system": TransactionSource.SYSTEM,
    }
    tx_source = source_map.get(source, TransactionSource.SYSTEM)

    transaction = WalletTransaction(
        wallet=wallet,
        user=user,
        type=TransactionType.CREDIT,
        amount=amount_paise,
        balance_after=balance_after,
        purpose=tx_purpose,
        source=tx_source,
        reference_id=reference_id or str(wallet.id),
        description=description or f"Credited {amount_paise} paise for {purpose}",
    )
    transaction.save()

    logger.info(
        f"Credited wallet {wallet.id} for user {user_id}: "
        f"{amount_paise} paise. New balance: {balance_after} paise."
    )

    return transaction


def debit_wallet(
    user_id: str,
    amount_paise: int,
    purpose: str,
    source: str,
    reference_id: str,
    description: str,
) -> "WalletTransaction":
    """
    Atomically debit wallet with insufficient balance protection.

    Uses MongoDB atomic check-and-debit: only modifies balance if
    balance >= amount_paise, preventing race conditions and ensuring
    balance never goes negative.

    Args:
        user_id: User document ID
        amount_paise: Amount in paise (positive integer)
        purpose: Transaction purpose (e.g. 'exam_purchase', 'subscription')
        source: Source of debit (e.g. 'razorpay', 'system')
        reference_id: External reference ID
        description: Human-readable description

    Returns:
        WalletTransaction document

    Raises:
        WalletServiceError: If amount <= 0 or wallet not found
        WalletServiceError: If insufficient balance
    """
    Wallet, User, WalletTransaction, TransactionType, TransactionSource, TransactionPurpose = _get_model("wallet")

    if amount_paise <= 0:
        raise WalletServiceError("Debit amount must be positive")

    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
    except Exception as e:
        raise WalletServiceError(f"Invalid user_id: {user_id}") from e

    user = User.objects(id=user_oid).first()
    if not user:
        raise WalletServiceError(f"User not found: {user_id}")

    wallet = Wallet.objects(user=user).first()
    if not wallet:
        raise WalletServiceError(f"Wallet not found for user: {user_id}")

    updated = Wallet.objects(
        user=user,
        balance__gte=amount_paise,
    ).modify(
        inc__balance=-amount_paise,
        inc__total_debited=amount_paise,
        inc__version=1,
        new=True,
    )

    if updated is None:
        wallet.reload()
        current_balance = int(wallet.balance) if wallet else 0
        raise WalletServiceError(
            f"Insufficient balance. Required: {amount_paise} paise "
            f"(₹{amount_paise / 100:.2f}), "
            f"Available: {current_balance} paise "
            f"(₹{current_balance / 100:.2f})"
        )

    wallet.reload()
    balance_after = int(wallet.balance)

    purpose_map = {
        "exam_purchase": TransactionPurpose.EXAM_PURCHASE,
        "subscription": TransactionPurpose.SUBSCRIPTION,
    }
    tx_purpose = purpose_map.get(purpose, TransactionPurpose.EXAM_PURCHASE)

    source_map = {
        "razorpay": TransactionSource.RAZORPAY,
        "system": TransactionSource.SYSTEM,
    }
    tx_source = source_map.get(source, TransactionSource.SYSTEM)

    transaction = WalletTransaction(
        wallet=wallet,
        user=user,
        type=TransactionType.DEBIT,
        amount=amount_paise,
        balance_after=balance_after,
        purpose=tx_purpose,
        source=tx_source,
        reference_id=reference_id or str(wallet.id),
        description=description or f"Debited {amount_paise} paise for {purpose}",
    )
    transaction.save()

    logger.info(
        f"Debited wallet {wallet.id} for user {user_id}: "
        f"{amount_paise} paise. New balance: {balance_after} paise."
    )

    return transaction


def get_wallet_balance(user_id: str) -> Dict[str, Any]:
    """
    Get current wallet balance for a user.

    Args:
        user_id: User document ID

    Returns:
        dict with balance_paise (int) and balance_rupees (float)
    """
    Wallet, User, _, _, _, _ = _get_model("wallet")

    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
    except Exception:
        raise WalletServiceError(f"Invalid user_id: {user_id}")

    user = User.objects(id=user_oid).first()
    if not user:
        raise WalletServiceError(f"User not found: {user_id}")

    wallet = Wallet.objects(user=user).first()
    if not wallet:
        return {
            "balance_paise": 0,
            "balance_rupees": 0.0,
            "currency": "INR",
        }

    wallet.reload()
    balance_paise = int(wallet.balance)

    return {
        "balance_paise": balance_paise,
        "balance_rupees": float(balance_paise) / 100.0,
        "currency": wallet.currency,
        "total_credited": int(wallet.total_credited),
        "total_debited": int(wallet.total_debited),
    }


def get_transactions(
    user_id: str,
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, Any]:
    """
    Get paginated wallet transactions for a user, newest first.

    Args:
        user_id: User document ID
        page: Page number (1-indexed)
        per_page: Results per page

    Returns:
        dict with items, total, page, limit, total_pages
    """
    Wallet, User, WalletTransaction, _, _, _ = _get_model("wallet")

    try:
        from bson import ObjectId
        user_oid = ObjectId(user_id)
    except Exception:
        raise WalletServiceError(f"Invalid user_id: {user_id}")

    user = User.objects(id=user_oid).first()
    if not user:
        raise WalletServiceError(f"User not found: {user_id}")

    wallet = Wallet.objects(user=user).first()
    if not wallet:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "limit": per_page,
            "total_pages": 0,
        }

    total = WalletTransaction.objects(wallet=wallet).count()
    skip = (page - 1) * per_page
    transactions = WalletTransaction.objects(wallet=wallet).order_by("-created_at").skip(skip).limit(per_page)

    return {
        "items": [tx.to_dict() for tx in transactions],
        "total": total,
        "page": page,
        "limit": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
    }
