import uuid
from database import Database
from models import User, UserRole

def seed_database():
    db = Database()
    
    # Define users to add
    users_to_seed = [
        User(
            id=str(uuid.uuid4()),
            email="ta@university.edu",
            password="ta123",  # In production, use hashed passwords!
            role=UserRole.TA
        ),
        User(
            id=str(uuid.uuid4()),
            email="student@university.edu",
            password="student123",
            role=UserRole.STUDENT
        )
    ]
    
    print("🌱 Seeding initial users...")
    
    for user in users_to_seed:
        # Check if user already exists
        if not db.get_user_by_email(user.email):
            try:
                db.create_user(user)
                print(f"✅ Added {user.role.upper()}: {user.email}")
            except Exception as e:
                print(f"❌ Failed to add {user.email}: {e}")
        else:
            print(f"ℹ️ User {user.email} already exists. Skipping.")
            
    print("\n✨ Seeding complete! You can now use these credentials to log in.")
    print("-" * 50)
    print(f"TA Login:      ta@university.edu / ta123")
    print(f"Student Login: student@university.edu / student123")
    print("-" * 50)

if __name__ == "__main__":
    seed_database()
