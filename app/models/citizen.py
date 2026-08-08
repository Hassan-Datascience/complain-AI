from typing import Optional

class Citizen:
    def __init__(
        self,
        citizen_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ):
        self.citizen_id = citizen_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self) -> dict:
        return {
            "citizen_id": self.citizen_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }
