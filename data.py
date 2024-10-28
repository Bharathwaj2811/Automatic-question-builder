from sqlalchemy import create_engine

# Replace 'your_password' and 'your_database' with your actual password and database name
engine = create_engine('mysql+pymysql://root:67896789Bhargav@@127.0.0.1:3306/bhargavr_banking')


# You can use engine.connect() to interact with the database if needed
try:
    with engine.connect() as connection:
        print("Connection to MySQL DB successful using SQLAlchemy")
except Exception as e:
    print(f"The error '{e}' occurred")
