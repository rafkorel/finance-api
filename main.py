from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator, model_validator

from datetime import date

app = FastAPI()

ACCOUNTS = {}
account_id = 0

CATEGORIES = {}
category_id = 0

TRANSACTIONS = {}
transaction_id = 0

TRANSFERS = {}
transfer_id = 0

###                   ВАЛИДАЦИЯ СЧЕТА

class CreateAccountRequest(BaseModel):
    name: str = Field(..., max_length=127)
    balance: float
    currency: str = Field(..., max_length=3)

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:

        v = v.strip()

        if not v:
            raise ValueError("Account name cannot be empty")

        return v

    @field_validator('balance')
    def balance_not_negative(cls, v: float) -> float:

        if v < 0:
            raise ValueError("Initial balance cannot be negative")
                
        return v

    @field_validator('currency')
    def validate_currency(cls, v: str) -> str:

        if v not in ["RUB", "EUR", "USD"]:
            raise ValueError("Currency must be one of RUB, USD, EUR")

        return v

###                        СЧЕТА

@app.post("/accounts", status_code=201)
async def create_account(request: CreateAccountRequest) -> dict:

    for account in ACCOUNTS.values():
        if request.name == account["name"]:
            raise HTTPException(
                status_code = 409,
                detail = f"Account with name '{request.name}' already exists"
            )

    global account_id
    account_id += 1

    ACCOUNTS[account_id] = {
        "account_id": account_id,
        "name": request.name,
        "balance": request.balance,
        "currency": request.currency,
    }

    return ACCOUNTS[account_id]

@app.get("/accounts")
async def get_accounts() -> dict:    
    return ACCOUNTS

@app.get("/accounts/{account_id}")
async def get_account(account_id : int) -> dict:

    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code = 404,
            detail = f"Account '{account_id}' not found"
        )

    return ACCOUNTS[account_id]

@app.delete("/accounts/{account_id}")
async def delete_account(account_id: int) -> dict:
    
    if account_id not in ACCOUNTS:
        raise HTTPException(
            status_code = 404,
            detail = f"Account '{account_id}' not found"
        )


    for transaction in TRANSACTIONS.values():
        if transaction["account_id"] == account_id:
            raise HTTPException(
                status_code=409,
                detail = f"Account '{account_id}' cannot be deleted because it is used in a transaction",
            )

    for transfer in TRANSFERS.values():
        if (
            transfer['from_account_id'] == account_id
            or transfer['to_account_id'] == account_id
        ):
            raise HTTPException(
                status_code=409,
                detail = f"Account '{account_id}' cannot be deleted because it is used in a transfer",
            )

    
    deleted_account = ACCOUNTS.pop(account_id)
    return {"deleted account": deleted_account}

###                 ВАЛИДАЦИЯ КАТЕГОРИЙ

class AddCategoryRequest(BaseModel):
    name: str = Field(..., max_length=127)
    category_type: str = Field(..., max_length=7)

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:

        v = v.strip()

        if not v:
            raise ValueError("Category name cannot be empty")

        return v

    @field_validator('category_type')
    def validate_category_type(cls, v: str) -> str:

        if v not in ["income", "expense"]:
            raise ValueError("Category type must be either 'income' or 'expense'")

        return v


###                     КАТЕГОРИИ

@app.post("/categories", status_code=201)
async def create_category(request: AddCategoryRequest) -> dict:

    for category in CATEGORIES.values():
        if category["name"] == request.name:
            raise HTTPException(
                status_code = 409,
                detail = f"Category with name '{request.name}' already exists"
            )

    global category_id
    category_id += 1

    CATEGORIES[category_id] = {
        "category_id": category_id,
        "name": request.name,
        "type": request.category_type,
    }

    return CATEGORIES[category_id]

@app.get("/categories")
async def get_categories() -> dict:
    return CATEGORIES

@app.get("/categories/{category_id}")
async def get_category(category_id: int) -> dict:
    
    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code = 404,
            detail = f"Category '{category_id}' not found"
        )

    return CATEGORIES[category_id]

@app.delete("/categories/{category_id}")
async def delete_category(category_id: int) -> dict:
        
    if category_id not in CATEGORIES:
        raise HTTPException(
            status_code = 404,
            detail = f"Category '{category_id}' not found"
        )

    for transaction in TRANSACTIONS.values():
        if transaction['category_id'] == category_id:
            raise HTTPException(
                status_code=409,
                detail = f"Category '{category_id}' cannot be deleted because it is used in a transaction",
            )

    deleted_category = CATEGORIES.pop(category_id)
    return {"deleted category": deleted_category}

###             ВАЛИДАЦИЯ ДОХОДОВ И РАСХОДОВ

class AddTransactionRequest(BaseModel):
    account_id: int
    category_id: int
    amount: float
    description: str | None = None
    date: date

    @field_validator('amount')
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
###                 Доходы и расходы

@app.post("/transactions/income", status_code=201)
async def create_income(request: AddTransactionRequest) -> dict:

    if request.account_id not in ACCOUNTS:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if request.category_id not in CATEGORIES:
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if CATEGORIES[request.category_id]["type"] != "income":
        raise HTTPException(
            status_code= 400,
            detail="Category must be income"
        )
    
    ACCOUNTS[request.account_id]['balance'] += request.amount

    global transaction_id
    transaction_id += 1

    TRANSACTIONS[transaction_id] ={
        "transaction_id": transaction_id,
        "account_id": request.account_id,
        "category_id": request.category_id,
        "type": CATEGORIES[request.category_id]["type"],
        "amount": request.amount,
        "description": request.description,
        "date": request.date,
    }

    return TRANSACTIONS[transaction_id]

@app.post("/transactions/expense", status_code=201)
async def create_expense(request: AddTransactionRequest) -> dict:

    if request.account_id not in ACCOUNTS:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if request.category_id not in CATEGORIES:
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if CATEGORIES[request.category_id]["type"] != "expense":
        raise HTTPException(
            status_code= 400,
            detail="Category must be expense"
        )

    if ACCOUNTS[request.account_id]['balance'] < request.amount:
        raise HTTPException(
            status_code= 400,
            detail="Expense amount cannot exceed the account balance"
        )
    
    ACCOUNTS[request.account_id]['balance'] -= request.amount

    global transaction_id
    transaction_id += 1

    TRANSACTIONS[transaction_id] ={
        "transaction_id": transaction_id,
        "account_id": request.account_id,
        "category_id": request.category_id,
        "type": CATEGORIES[request.category_id]["type"],
        "amount": request.amount,
        "description": request.description,
        "date": request.date,
    }

    return TRANSACTIONS[transaction_id]

@app.get("/transactions")
async def get_transactions() -> dict:
    return TRANSACTIONS

@app.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: int) -> dict:
    
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(
            status_code = 404,
            detail = f"Transaction '{transaction_id}' not found"
        )
    
    return TRANSACTIONS[transaction_id]

@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict:
        
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(
            status_code = 404,
            detail = f"Transaction '{transaction_id}' not found"
        )

    if (
        TRANSACTIONS[transaction_id]['type'] == 'income' 
        and ACCOUNTS[TRANSACTIONS[transaction_id]['account_id']]['balance'] < TRANSACTIONS[transaction_id]['amount']
    ):
        raise HTTPException(
            status_code= 409,
            detail= f"Transaction '{transaction_id}' cannot be deleted because it would make the account balance negative"
        )
    
    deleted_transaction = TRANSACTIONS.pop(transaction_id)

    account_id_from_transaction = deleted_transaction['account_id']
    if deleted_transaction['type'] == 'income':
        ACCOUNTS[account_id_from_transaction]['balance'] -= deleted_transaction['amount']
    else:
        ACCOUNTS[account_id_from_transaction]['balance'] += deleted_transaction['amount']

    return {"deleted transaction": deleted_transaction}

###                 ВАЛИДАЦИЯ ПЕРЕВОДОВ

class AddTransferRequest(BaseModel):
    from_account_id : int
    to_account_id: int
    amount: float
    description: str | None = None

    @model_validator(mode="after")
    def accounts_must_be_different(self):
        if self.from_account_id == self.to_account_id:
            raise ValueError('Source and destination accounts must be different')
        return self

    @field_validator('amount')
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

###                     ПЕРЕВОДЫ

@app.post("/transfers", status_code=201)
async def create_transfer(request: AddTransferRequest) -> dict:

    if request.from_account_id not in ACCOUNTS:
        raise HTTPException(
            status_code=404,
            detail = f"Id from: '{request.from_account_id}' not found among accounts"
        )

    if request.to_account_id not in ACCOUNTS:
        raise HTTPException(
            status_code=404,
            detail = f"Id to: '{request.to_account_id}' not found among accounts"
        )

    if ACCOUNTS[request.from_account_id]['balance'] < request.amount:
        raise HTTPException(
            status_code = 400,
            detail = 'Transfer amount cannot exceed the source account balance'
        )

    ACCOUNTS[request.from_account_id]['balance'] -= request.amount
    ACCOUNTS[request.to_account_id]['balance'] += request.amount

    global transfer_id
    transfer_id += 1

    TRANSFERS[transfer_id] = {
        "transfer_id": transfer_id,
        "from_account_id": request.from_account_id,
        "to_account_id": request.to_account_id,
        "amount": request.amount,
        "description": request.description,
    }

    return TRANSFERS[transfer_id]

@app.get("/transfers")
async def get_transfers() -> dict:
    return TRANSFERS

@app.get("/transfers/{transfer_id}")
async def get_transfer(transfer_id: int) -> dict:
        
    if transfer_id not in TRANSFERS:
        raise HTTPException(
            status_code = 404,
            detail = f"Transfer '{transfer_id}' not found"
        )

    return TRANSFERS[transfer_id]

@app.delete("/transfers/{transfer_id}")
async def delete_transfer(transfer_id: int) -> dict:
            
    if transfer_id not in TRANSFERS:
        raise HTTPException(
            status_code = 404,
            detail = f"Transfer '{transfer_id}' not found"
        )

    if ACCOUNTS[TRANSFERS[transfer_id]['to_account_id']]['balance'] < TRANSFERS[transfer_id]['amount']:
        raise HTTPException(
            status_code=409,
            detail = f"Transfer '{transfer_id}' cannot be deleted because the recipient account has insufficient balance",
        )

    deleted_transfer = TRANSFERS.pop(transfer_id)

    account_id_1_from_transfer = deleted_transfer['from_account_id']
    ACCOUNTS[account_id_1_from_transfer]['balance'] += deleted_transfer['amount']
    
    account_id_2_from_transfer = deleted_transfer['to_account_id']
    ACCOUNTS[account_id_2_from_transfer]['balance'] -= deleted_transfer['amount']

    return {"deleted transfer": deleted_transfer}

###                         СТАТИСТИКА

@app.get("/statistics/balance")
async def get_balance_statistics() -> dict:

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
async def get_categories_statistics(category_type: str = Query(..., max_length=7)) -> list:


    if category_type not in ['income', 'expense']:
        raise HTTPException(
            status_code = 400,
            detail = "category type must be income or expense",
        )

    if not CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail = "Categories is empty"
        )

    if not TRANSACTIONS:
        raise HTTPException(
            status_code=400,
            detail = "No transactions found"
        )

    if not any(
    transaction['type'] == category_type
    for transaction in TRANSACTIONS.values()
    ):
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
async def get_transactions_statistics_by_period(date_from: date, date_to: date) -> list:

    if date_from > date_to:
        raise HTTPException(
            status_code= 400,
            detail = f"date_from cannot be later than date_to",
        )

    result = []
    for transaction in TRANSACTIONS.values():
        if date_from <= transaction['date'] <= date_to:
            result.append(transaction)

    return result