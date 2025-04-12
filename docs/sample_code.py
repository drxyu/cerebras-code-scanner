#!/usr/bin/env python3

def get_user_data(user_id):
    """
    Fetch user data from the database
    """
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def create_user(username, password):
    """
    Create a new user in the database
    """
    # No password hashing
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    cursor.execute(query)
    conn.commit()
    
def search_users(keyword):
    """
    Search for users with a keyword
    """
    query = f"SELECT * FROM users WHERE username LIKE '%{keyword}%'"
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    # Connect to database
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    ''')
    
    # Example usage
    create_user("admin", "password123")
    user = get_user_data(1)
    print(f"User: {user}")
    
    search_results = search_users("ad")
    print(f"Search results: {search_results}")
    
    conn.close() 