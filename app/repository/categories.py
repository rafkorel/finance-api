from app.schemas.categories import Category

CATEGORIES: dict[int, Category]= {}
category_id = 0

def create_category(name: str, category_type: str) -> Category:

    global category_id
    category_id += 1

    CATEGORIES[category_id] = {
        "category_id": category_id,
        "name": name,
        "type": category_type,
    }

    return CATEGORIES[category_id]


def is_category_exists(name: str) -> bool:

    for category in CATEGORIES.values():
        if category["name"] == name:
            return False
    return True


def get_all_categories() -> dict[int, Category]:
    return CATEGORIES.copy()


def is_category_id_exists(category_id : int) -> bool:

    if category_id not in CATEGORIES:
        return False
    return True


def get_category_by_category_id(category_id : int) -> Category | None:
    return CATEGORIES.get(category_id)


def delete_category(category_id: int) -> dict[str, Category]:
    
    deleted_category = CATEGORIES.pop(category_id)
    return {"deleted category": deleted_category}


def type_check_income(category_id: int) -> bool:

    if CATEGORIES[category_id]["type"] != "income":
        return False
    return True


def type_check_expense(category_id: int) -> bool:

    if CATEGORIES[category_id]["type"] != "expense":
        return False
    return True


def get_type_by_category_id(category_id: int) -> str:
    return CATEGORIES[category_id]["type"]


def categories_is_empty() -> bool:
    return CATEGORIES == {}


def get_category_name_by_id(category_id: int) -> str:
    return CATEGORIES[category_id]['name']
