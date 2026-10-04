TRANSFERS = {}
transfer_id = 0

def create_transfer(
        from_account_id: int,
        to_account_id: int,
        amount: float,
        description: str | None
    ) -> dict:

    global transfer_id
    transfer_id += 1

    TRANSFERS[transfer_id] = {
        "transfer_id": transfer_id,
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "amount": amount,
        "description": description,
    }

    return TRANSFERS[transfer_id]


def get_all_transfers() -> dict:
    return TRANSFERS.copy()


def is_transfer_id_exists(transfer_id : int) -> bool:

    if transfer_id not in TRANSFERS:
        return False
    return True


def get_transfer_by_transfer_id(transfer_id : int) -> dict:
    return TRANSFERS[transfer_id]


def delete_transfer(transfer_id: int) -> dict:
    return TRANSFERS.pop(transfer_id)


def is_account_id_exists_in_transfers(account_id : int) -> bool:

    for transfer in TRANSFERS.values():
        if (
            transfer['from_account_id'] == account_id
            or transfer['to_account_id'] == account_id
        ):
            return False
    return True


def get_amount_by_transfer_id(transfer_id: int) -> float:
    return TRANSFERS[transfer_id]['amount']