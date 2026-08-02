"""Generate synthetic member records.

Every value here is fabricated. Nothing in this project should ever touch real
member data — that would make it subject to a completely different set of
handling requirements.
"""

import random

from app.db import get_connection, init_db

FIRST_NAMES = [
    "Amara", "Diego", "Priya", "Elena", "Marcus", "Linh", "Omar", "Sofia",
    "Tobias", "Nadia", "Kwame", "Isabel", "Ravi", "Greta", "Yusuf", "Mei",
]
LAST_NAMES = [
    "Okafor", "Ramirez", "Sharma", "Novak", "Bennett", "Tran", "Haddad",
    "Moreau", "Lindqvist", "Petrov", "Mensah", "Castillo", "Iyer", "Weber",
]
CITIES = [
    ("Newark", "NJ", "07102"), ("Jersey City", "NJ", "07302"),
    ("Trenton", "NJ", "08608"), ("Paterson", "NJ", "07501"),
    ("Camden", "NJ", "08102"), ("Edison", "NJ", "08817"),
]
STREETS = ["Maple Ave", "Oak St", "Center St", "Park Blvd", "Ridge Rd"]
LANGS = ["en", "en", "en", "es", "es", "zh", "vi", "ru"]


def seed(count: int = 25, reset: bool = True):
    init_db()
    with get_connection() as conn:
        if reset:
            conn.execute("DELETE FROM members")

        for i in range(1, count + 1):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            city, state, postal = random.choice(CITIES)
            conn.execute(
                """
                INSERT INTO members (
                    member_number, first_name, last_name, email, phone,
                    address_line1, city, state, postal_code, language_preference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"M{100000 + i}",
                    first,
                    last,
                    f"{first.lower()}.{last.lower()}@example.com",
                    f"555-01{random.randint(10, 99)}",
                    f"{random.randint(100, 9999)} {random.choice(STREETS)}",
                    city,
                    state,
                    postal,
                    random.choice(LANGS),
                ),
            )
    print(f"Seeded {count} synthetic members.")


if __name__ == "__main__":
    seed()
