from fastapi import FastAPI, HTTPException

app = FastAPI()

ACCOUNT = {}
account_id = 0

@app.get("/account")
async def create_account(name: str, balance: float, currency: str):

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