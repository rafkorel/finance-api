from app.schemas.accounts import Account

ACCOUNTS: dict[int, Account] = {}
account_id = 0

def create_account(name: str, balance: float, currency: str) -> Account:

    global account_id
    account_id += 1

    ACCOUNTS[account_id] = {
        "account_id": account_id,
        "name": name,
        "balance": balance,
        "currency": currency,
    }

    return ACCOUNTS[account_id]


def is_account_exists(name: str) -> bool:

    for account in ACCOUNTS.values():
        if name == account["name"]:
            return False
    return True


def get_all_accounts() -> dict[int, Account]:
    return ACCOUNTS.copy()


def is_account_id_exists(account_id : int) -> bool:

    if account_id not in ACCOUNTS:
        return False
    return True


def get_account_by_account_id(account_id : int) -> Account | None:
    return ACCOUNTS.get(account_id)


def delete_account(account_id: int) -> dict[str, Account]:
    deleted_account = ACCOUNTS.pop(account_id)
    return {"deleted account": deleted_account}


def subtract_amount(account_id: int, amount: float) -> bool:

    if ACCOUNTS[account_id]['balance'] < amount:
        return False
    return True


def get_balance_by_account_id(account_id: int) -> float:

    return ACCOUNTS[account_id]["balance"]

def deduct_from_balance(account_id: int, amount: float) -> None:
    ACCOUNTS[account_id]['balance'] -= amount


def add_to_balance(account_id: int, amount: float) -> None:
    ACCOUNTS[account_id]['balance'] += amount


def accounts_is_empty() -> bool:
    return ACCOUNTS == {}


def get_all_balance() -> dict[str, float | list[Account]]:

    total_balance = 0
    accounts = []
    for account in ACCOUNTS.values():

        total_balance += account['balance']
        accounts.append(account)

    return {
        "total_balance": total_balance,
        "accounts": accounts,
    }