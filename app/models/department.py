from typing import Optional

class Department:
    def __init__(
        self,
        department_id: str,
        name: str,
        category_handled: str,
    ):
        self.department_id = department_id
        self.name = name
        self.category_handled = category_handled

    def to_dict(self) -> dict:
        return {
            "department_id": self.department_id,
            "name": self.name,
            "category_handled": self.category_handled,
        }
