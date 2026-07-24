from app import app
from models import db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():

    # Check if admin already exists
    admin = Admin.query.filter_by(username="admin").first()

    if admin:
        print("✅ Admin already exists.")

    else:
        new_admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )

        db.session.add(new_admin)
        db.session.commit()

        print("✅ Admin created successfully!")