from enum import Enum

class Category(Enum):
    INPUT = "input"
    RATE = "rate"
    SERVER = "server"
    OTHER = "other"

def classify_http(status: int | None) -> Category:
    if status in (400, 404, 422):
        return Category.INPUT
    if status == 429:
        return Category.RATE
    if 500 <= status <= 599:
        return Category.SERVER
    else:
        return Category.OTHER