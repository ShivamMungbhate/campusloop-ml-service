
from database import check_database

try:
    check_database()
    print("MongoDB Atlas connected successfully!")
except Exception as error:
    print("MongoDB connection failed.")
    print(type(error).__name__, str(error))
