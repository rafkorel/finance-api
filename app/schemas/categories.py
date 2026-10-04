from pydantic import BaseModel, Field, field_validator


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