from fastapi import FastAPI, HTTPException

app = FastAPI()

ACCOUNT = {}
account_id = 0

@app.post("/account")
async def create_account(name: str, balance: float, currency: str) -> dict:

    for account in ACCOUNT.values():
        if name == account["name"]:
            raise HTTPException(
                status_code = 400,
                detail = f"Account with name '{name}' alredy exists"
            )
    
    if balance < 0:
        raise HTTPException(
            status_code = 400,
            detail = f"Ballance cannot be nagative"
        )

    if currency not in ["RUB", "USD", "EUR"]:
        raise HTTPException(
            status_code = 400,
            detail = f"Currency must be one of RUB, USD, EUR"
        )

    global account_id
    account_id += 1

    ACCOUNT[account_id] = {
        "id": account_id,
        "name": name,
        "balance": balance,
        "currency": currency,
    }

    return ACCOUNT[account_id]

@app.get("/accounts")
async def get_accounts() -> dict:
    if ACCOUNT == {}:
        raise HTTPException(
            status_code = 400,
            detail = "Accounts not found"
        )
    return ACCOUNT

@app.get("/accounts/{account_id}")
async def get_accounts_by_account_id(account_id : int) -> dict:

    if ACCOUNT == {}:
            raise HTTPException(
                status_code = 400,
                detail = "Accounts not found"
            )

    if account_id not in ACCOUNT:
        raise HTTPException(
            status_code = 400,
            detail = "id not found among accounts"
        )
    else:
        return ACCOUNT[account_id]

@app.delete("/accounts/{account_id}")
async def delete_account_by_account_id(account_id: int) -> dict:

    if not ACCOUNT:
        return ACCOUNT
    
    if account_id not in ACCOUNT:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among accounts"
        )
    else:
        delete_account = ACCOUNT.pop(account_id)
        return {"deleted account": delete_account}