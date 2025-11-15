import sqlite3
import os

# Change to backend directory to find the database
os.chdir(os.path.dirname(__file__))

# Connect to database
conn = sqlite3.connect('shop_steward.db')
cursor = conn.cursor()

# Check current role
cursor.execute("SELECT username, email, role FROM users WHERE username = 'admin'")
print("BEFORE:", cursor.fetchone())

# Update to HUB_MASTER
cursor.execute("UPDATE users SET role = 'HUB_MASTER' WHERE username = 'admin'")
conn.commit()

# Verify the change
cursor.execute("SELECT username, email, role FROM users WHERE username = 'admin'")
print("AFTER:", cursor.fetchone())

# Close connection
conn.close()
print("\n✅ Role updated successfully!")
