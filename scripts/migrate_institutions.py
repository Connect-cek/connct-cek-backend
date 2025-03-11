import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.institutions import Institution, InstitutionStatus


def migrate_institutions():
    """Add status field to existing institutions."""
    db = SessionLocal()
    try:
        # Get all institutions
        institutions = db.query(Institution).all()

        # Update each institution with a default status
        for institution in institutions:
            # Check if the institution already has a status
            if not hasattr(institution, "status") or institution.status is None:
                institution.status = InstitutionStatus.PENDING

        db.commit()
        print(f"Successfully updated {len(institutions)} institutions")
    except Exception as e:
        print(f"Error updating institutions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_institutions()
