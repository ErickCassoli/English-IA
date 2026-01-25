import sys
import traceback
from app.repo.db import SessionLocal
from app.repo import dao

def test_dashboard():
    db = SessionLocal()
    try:
        print("Calling get_dashboard_summary...")
        summary = dao.get_dashboard_summary(db)
        print("Success:", summary)
    except Exception:
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_dashboard()
