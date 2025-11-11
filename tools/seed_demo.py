from __future__ import annotations

import hashlib

from app.repo import dao


def main() -> None:
    dao.ensure_flashcard("What's up?", "A casual greeting meaning 'How are you?'", "chat")
    dao.ensure_flashcard("Break a leg", "An idiom meaning 'good luck'", "idiom")
    dao.ensure_flashcard("I have been", "Present perfect of 'to be'", "grammar")

    demo_email = "demo@english-ia.dev"
    if not dao.get_user_by_email(demo_email):
        dao.create_user(
            email=demo_email,
            password_hash=hashlib.sha256(b"englishia").hexdigest(),
            display_name="Demo Learner",
        )
        print("Created demo user:", demo_email)
    else:
        print("Demo user already exists.")


if __name__ == "__main__":
    main()
