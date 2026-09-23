from fastapi import FastAPI, HTTPException

from datetime import datetime

app = FastAPI()

ACCOUNTS = {}
account_id = 0

CATEGORIES = {}
category_id = 0

TRANSACTIONS = {}
transaction_id = 0

TRANSFERS = {}
transfer_id = 0

###                        СЧЕТА

@app.post("/account")
async def create_account(name: str, balance: float, currency: str) -> dict:

    for account in ACCOUNTS.values():
        if name == account["name"]:
            raise HTTPException(
                status_code = 400,
                detail = f"Account with name '{name}' alredy exists"
            )
    
    if balance < 0:
        raise HTTPException(
            status_code = 400,
            detail = "Ballance cannot be nagative"
        )

    if currency not in ["RUB", "USD", "EUR"]:
        raise HTTPException(
            status_code = 400,
            detail = "Currency must be one of RUB, USD, EUR"
        )

    global account_id
    account_id += 1

    ACCOUNTS[account_id] = {
        "account_id": account_id,
        "name": name,
        "balance": balance,
        "currency": currency,
    }

    return ACCOUNTS[account_id]

@app.get("/accounts")
async def get_accounts() -> dict:
    if not ACCOUNTS:
        raise HTTPException(
            status_code = 400,
            detail = "Accounts is empty"
        )
    return ACCOUNTS

@app.get("/accounts/{account_id}")
async def get_accounts_by_account_id(account_id : int) -> dict:

    if not ACCOUNTS:
        raise HTTPException(
            status_code = 400,
            detail = "Accounts is empty"
        )

    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among accounts"
        )
    else:
        return ACCOUNTS[account_id]

@app.delete("/accounts/{account_id}")
async def delete_account_by_account_id(account_id: int) -> dict:

    if not ACCOUNTS:
        raise HTTPException(
            status_code = 400,
            detail = "Accounts is empty"
        )
    
    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code = 404,
            detail = "Id not found among accounts"
        )
    else:
        delete_account = ACCOUNTS.pop(account_id)
        return {"deleted account": delete_account}

###                     КАТЕГОРИИ

@app.post("/category")
async def add_category(name: str, category_type: str) -> dict:

    for category in CATEGORIES.values():
        if category["name"] == name:
            raise HTTPException(
                status_code = 400,
                detail = f"category '{name}' already exists"
            )

    if category_type not in ["income", "expense"]:
        raise HTTPException(
            status_code = 400,
            detail = "category must be income or expense"
        )

    global category_id
    category_id += 1

    CATEGORIES[category_id] = {
        "category_id": category_id,
        "name": name,
        "type": category_type,
    }

    return CATEGORIES[category_id]

@app.get("/categories")
async def get_categories() -> dict:
    if not CATEGORIES:
        raise HTTPException(
            status_code = 400,
            detail = "Categories is empty"
        )
    return CATEGORIES

@app.get("/categories/{category_id}")
async def get_category_by_category_id(category_id: int) -> dict:

    if not CATEGORIES:
        raise HTTPException(
            status_code = 400,
            detail = "Categories is empty"
        )
    
    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among categories"
        )
    else:
        return CATEGORIES[category_id]

@app.delete("/categories/{category_id}")
async def delete_category_by_category_id(category_id: int) -> dict:

    if not CATEGORIES:
        raise HTTPException(
            status_code = 400,
            detail = "Categories is empty"
        )
        
    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code = 404,
            detail = "Id not found among categories"
        )
    else:
        delete_category = CATEGORIES.pop(category_id)
        return {"deleted category": delete_category}

###                 Доходы и расходы

@app.post("/transactions/income")
async def add_income(account_id: int, category_id: int, amount: float, description: str, date: str) -> dict:

    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{account_id}' not found among accounts"
        )

    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{category_id}' not found among categories"
        )

    if CATEGORIES[category_id]["type"] != "income":
        raise HTTPException(
            status_code= 400,
            detail="Category must be income"
        )

    if amount <= 0:
        raise HTTPException(
            status_code= 400,
            detail="Amount must be positive"
        )
    
    ACCOUNTS[account_id]['balance'] += amount

    global transaction_id
    transaction_id += 1

    TRANSACTIONS[transaction_id] ={
        "transaction_id": transaction_id,
        "account_id": account_id,
        "category_id": category_id,
        "type": CATEGORIES[category_id]["type"],
        "amount": amount,
        "description": description,
        "date": date,
    }

    return TRANSACTIONS[transaction_id]

@app.post("/transactions/expense")
async def add_expense(account_id: int, category_id: int, amount: float, description: str, date: str) -> dict:

    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{account_id}' not found among accounts"
        )

    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{category_id}' not found among categories"
        )

    if CATEGORIES[category_id]["type"] != "expense":
        raise HTTPException(
            status_code= 400,
            detail="Category must be expense"
        )

    if amount <= 0:
        raise HTTPException(
            status_code= 400,
            detail="Amount must be positive"
        )

    if ACCOUNTS[account_id]['balance'] < amount:
        raise HTTPException(
            status_code= 400,
            detail="Amount must not exceed balance"
        )
    
    ACCOUNTS[account_id]['balance'] -= amount

    global transaction_id
    transaction_id += 1

    TRANSACTIONS[transaction_id] ={
        "transaction_id": transaction_id,
        "account_id": account_id,
        "category_id": category_id,
        "type": CATEGORIES[category_id]["type"],
        "amount": amount,
        "description": description,
        "date": date,
    }

    return TRANSACTIONS[transaction_id]

@app.get("/transactions")
async def get_transactions() -> dict:
    if not TRANSACTIONS:
        raise HTTPException(
            status_code = 400,
            detail = "Transactions is empty"
        )
    return TRANSACTIONS

@app.get("/transactions/{transaction_id}")
async def get_transaction_by_transaction_id(transaction_id: int) -> dict:

    if not TRANSACTIONS:
        raise HTTPException(
            status_code = 400,
            detail = "Transactions is empty"
        )
    
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among transactions"
        )
    else:
        return TRANSACTIONS[transaction_id]

@app.delete("/transactions/{transaction_id}")
async def delete_transaction_by_transaction_id(transaction_id: int) -> dict:

    if not TRANSACTIONS:
        raise HTTPException(
            status_code = 400,
            detail = "Transactions is empty"
        )
        
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among transactions"
        )
    else:
        delete_transaction = TRANSACTIONS.pop(transaction_id)

        account_id_from_transaction = delete_transaction['account_id']
        if delete_transaction['type'] == 'income':
            ACCOUNTS[account_id_from_transaction]['balance'] -= delete_transaction['amount']
        else:
            ACCOUNTS[account_id_from_transaction]['balance'] += delete_transaction['amount']

        return {"deleted transaction": delete_transaction}

###                     Переводы

@app.post("/transfers")
async def add_transfers(from_account_id: int, to_account_id: int, amount: float, description: str) -> dict:

    if from_account_id not in ACCOUNTS:
        raise HTTPException(
            status_code=404,
            detail = f"Id from: '{from_account_id}' not found among accounts"
        )

    if to_account_id not in ACCOUNTS:
        raise HTTPException(
            status_code=404,
            detail = f"Id to: '{to_account_id}' not found among accounts"
        )

    if from_account_id == to_account_id:
        raise HTTPException(
            status_code = 400,
            detail = 'Account must not be same'
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail = "Amount must be positive"
        )

    if ACCOUNTS[from_account_id]['balance'] < amount:
        raise HTTPException(
            status_code = 400,
            detail = 'Amount must not exceed balance from'
        )

    ACCOUNTS[from_account_id]['balance'] -= amount
    ACCOUNTS[to_account_id]['balance'] += amount

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

@app.get("/transfers")
async def get_transfers() -> dict:
    
    if not TRANSFERS:
        raise HTTPException(
            status_code = 400,
            detail = "Transfers is empty"
        )

    return TRANSFERS

@app.get("/transfers/{transfer_id}")
async def get_transfer_by_transfer_id(transfer_id: int) -> dict:

    if not TRANSFERS:
        raise HTTPException(
            status_code = 400,
            detail = "Transfers is empty"
        )
        
    if transfer_id not in TRANSFERS:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among transfers"
        )
    else:
        return TRANSFERS[transfer_id]

@app.delete("/transfers/{transfer_id}")
async def delete_transfer_by_transfer_id(transfer_id: int) -> dict:

    if not TRANSFERS:
        raise HTTPException(
            status_code = 400,
            detail = "Transfers is empty"
        )
            
    if transfer_id not in TRANSFERS:
        raise HTTPException(
            status_code = 404,
            detail = "id not found among transfers"
        )
    else:
        delete_transfer = TRANSFERS.pop(transfer_id)

        account_id_1_from_transfer = delete_transfer['from_account_id']
        ACCOUNTS[account_id_1_from_transfer]['balance'] += delete_transfer['amount']
        
        account_id_2_from_transfer = delete_transfer['to_account_id']
        ACCOUNTS[account_id_2_from_transfer]['balance'] -= delete_transfer['amount']

        return {"deleted transfer": delete_transfer}

###                         Статистика

@app.get("/statistics/balance")
async def get_all_balance() -> dict:

    if not ACCOUNTS:
        raise HTTPException(
            status_code=400,
            detail = "Accounts is empty"
        )

    total_balance = 0
    accounts = []
    for account in ACCOUNTS.values():

        total_balance += account['balance']
        accounts.append(account)

    return {
        "total_balance": total_balance,
        "accounts": accounts,
    }

@app.get("/statistics/categories")
async def get_categories_by_type(category_type: str) -> list:

    if not CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail = "Categories is empty"
        )

    if category_type not in ['income', 'expense']:
        raise HTTPException(
            status_code=400,
            detail = "category type must be income or expense"
        )

    if CATEGORIES and not TRANSACTIONS:
        raise HTTPException(
            status_code=400,
            detail = "Transaction must be not empty if categories isn`t empty"
        )

    if not any(transaction for transaction in TRANSACTIONS.values() if transaction['type'] == category_type):
        raise HTTPException(
            status_code=404,
            detail = f"type '{category_type}' not found among categories"
        )

    result = []
    for transaction in TRANSACTIONS.values():
        if transaction['type'] == category_type:

            found = False
            name = CATEGORIES[transaction['category_id']]['name']

            for dicts in result:
                if name == dicts['category']:

                    dicts['total'] += transaction['amount']
                    found = True

            if not found:

                result.append({
                    'category': name,
                    'total': transaction['amount']
                })

    return result

@app.get("/statistics/period")
async def get_transartions_by_period(date_from: str, date_to: str) -> list:

    date_from_now = datetime.strptime(date_from, "%Y-%m-%d") 
    date_to_now = datetime.strptime(date_to, "%Y-%m-%d") 

    if date_from_now > date_to_now:
        raise HTTPException(
            status_code=400,
            detail=f"'{date_from_now}' cannot be later than  '{date_to_now}'"
        )

    result = []
    found = False
    for transaction in TRANSACTIONS.values():
        if date_from_now<=datetime.strptime(transaction['date'], "%Y-%m-%d")<=date_to_now:
            result.append(transaction)
            found = True
    if not found:
        raise HTTPException(
            status_code=400,
            detail="There are no transactions in this range"
        )

    return result