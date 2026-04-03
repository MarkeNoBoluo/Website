import sys

sys.path.insert(0, r"D:\Repositories\VSCODE\Website")

from app import create_app
from app.extensions import db
from app.models import User
from app.auth.utils import create_user
import bcrypt

app = create_app()
with app.app_context():
    # Check if admin exists
    existing = User.query.filter_by(username="admin").first()
    if existing:
        print(f"Admin user already exists (ID: {existing.id})")
    else:
        # Create admin user with bcrypt
        password_hash = bcrypt.hashpw(
            "admin123".encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        admin = User(username="admin", password_hash=password_hash)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created successfully (ID: {admin.id})")

    # Verify
    users = User.query.all()
    print(f"\nAll users: {[u.username for u in users]}")
