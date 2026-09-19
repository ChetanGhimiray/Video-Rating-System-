import mysql.connector


# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="",
    database="video_grading_system"
)

# Check connection
if db.is_connected():
    print("Database connected successfully!")


# Create cursor
cursor = db.cursor()


# Test query
cursor.execute("SHOW TABLES")

tables = cursor.fetchall()

print("\nTables in database:")

for table in tables:
    print(table[0])


# Close connection
cursor.close()
db.close()

print("\nDatabase connection closed.")
