from datetime import date

TRANSACTIONS = {}
transaction_id = 0

def create_transactions(
        account_id : int,
        category_id: int,
        amount: float,
        description: str | None,
        date: date,
        category_type: str
    ) -> dict:

    global transaction_id
    transaction_id += 1

    TRANSACTIONS[transaction_id] ={
        "transaction_id": transaction_id,
        "account_id": account_id,
        "category_id": category_id,
        "type": category_type,
        "amount": amount,
        "description": description,
        "date": date,
    }

    return TRANSACTIONS[transaction_id]


def is_transaction_id_exists(transaction_id : int) -> bool:

    if transaction_id not in TRANSACTIONS:
        return False
    return True


def get_all_transactions() -> dict:
    return TRANSACTIONS.copy()


def get_transaction_by_transaction_id(transaction_id : int) -> dict:
    return TRANSACTIONS[transaction_id]


def delete_transaction(transaction_id: int) -> dict:
    
    return TRANSACTIONS.pop(transaction_id)


def get_type_by_transaction_id(transaction_id: int) -> str:
    return TRANSACTIONS[transaction_id]['type']


def get_amount_by_transaction_id(transaction_id: int) -> float:
    return TRANSACTIONS[transaction_id]['amount']


def is_account_id_exists_in_transactions(account_id : int) -> bool:

    for transaction in TRANSACTIONS.values():
        if transaction["account_id"] == account_id:
            return False
    return True


def is_category_id_exists_in_transactions(category_id: int) -> bool:
        
    for transaction in TRANSACTIONS.values():
        if transaction['category_id'] == category_id:
            return False
    return True


def transactions_is_empty() -> bool:
    return TRANSACTIONS == {}


def is_category_type_exists_in_transactions(category_type: str) -> bool:
    if not any(
    transaction['type'] == category_type
    for transaction in TRANSACTIONS.values()
    ):
        return False
    return True


def get_transactions_statistics_by_period(date_from: date, date_to: date) -> list:

    result = []
    for transaction in TRANSACTIONS.values():
        if date_from <= transaction['date'] <= date_to:
            result.append(transaction)

    return result