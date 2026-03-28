"""
Quick test script to verify MongoDB connection.

Run this before starting the Flask server to ensure MongoDB is accessible.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    from db_mongo import get_db, users_collection, sessions_collection
    
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    
    # Test connection
    db = get_db()
    print("✓ MongoDB connection successful!")
    
    # List databases
    databases = db.client.list_database_names()
    print(f"\n✓ Available databases: {databases}")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"✓ Collections in 'physioai' database: {collections}")
    
    # Check users count
    user_count = users_collection.count_documents({})
    print(f"\n✓ Users collection: {user_count} documents")
    
    # Check sessions count
    session_count = sessions_collection.count_documents({})
    print(f"✓ Sessions collection: {session_count} documents")
    
    print("\n" + "=" * 60)
    print("MongoDB is ready! You can start the Flask server.")
    print("=" * 60)
    
except Exception as e:
    print("=" * 60)
    print("❌ MongoDB Connection Failed!")
    print("=" * 60)
    print(f"\nError: {e}")
    print("\nPlease ensure:")
    print("1. MongoDB is installed and running")
    print("2. MongoDB is accessible at mongodb://localhost:27017")
    print("3. MONGO_URI is set correctly in .env file")
    print("\nTo start MongoDB:")
    print("  - Windows: Run 'net start MongoDB' or check Services")
    print("  - Mac/Linux: Run 'sudo systemctl start mongod'")
    print("=" * 60)
    sys.exit(1)
