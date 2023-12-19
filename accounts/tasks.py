from celery import shared_task
from bmstu_lab.models import Account, CardTerms, DepositTerms, CreditTerms, SaveTerms
import logging
import time

logger = logging.getLogger(__name__)


@shared_task
def delete_account(account_id):
    logger.info(f"Deleting account with ID: {account_id}")

    try:
        account = Account.objects.get(id=account_id)

        # Countdown timer in the terminal
        for i in range(30 * 24 * 60 * 60, 0, -1):
            account.refresh_from_db()
            if account.available:
                logger.warning("Account is available. Deletion canceled.")
                return

            time.sleep(1)

        if account.type == "Карта":
            curr = CardTerms.objects.get(number=account.number)
        elif account.type == "Кредитный счет":
            curr = CreditTerms.objects.get(number=account.number)
        elif account.type == "Вклад":
            curr = DepositTerms.objects.get(number=account.number)
        elif account.type == "Сберегательный счет":
            curr = SaveTerms.objects.get(number=account.number)

        curr.delete()
        account.delete()
        logger.info(f"Account deleted successfully.")
    except Account.DoesNotExist:
        logger.warning(f"Account with ID {account_id} does not exist.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
