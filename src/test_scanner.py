import asyncio
from scanner.cerebras_scanner import CodeScanner
import psycopg2

async def test_scanner():
    # Initialize the scanner
    scanner = CodeScanner()
    
    # Test SQL injection vulnerability
    sql_code = """
def get_user_data(user_id):
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
    """
    
    print("Testing SQL injection detection...")
    result = await scanner.analyze_code(sql_code, "sql_injection")
    print("SQL Injection Analysis:", result)
    
    # Test hardcoded credentials
    auth_code = """
def connect_to_db():
    username = "admin"
    password = "password123"
    return psycopg2.connect(
        host="localhost",
        user=username,
        password=password
    )
    """
    
    print("\nTesting hardcoded credentials detection...")
    result = await scanner.analyze_code(auth_code, "auth")
    print("Auth Analysis:", result)
    
    # Test command injection
    cmd_code = """
def ping_host(host):
    import os
    os.system(f"ping -c 4 {host}")
    """
    
    print("\nTesting command injection detection...")
    result = await scanner.analyze_code(cmd_code, "input_validation")
    print("Command Injection Analysis:", result)

if __name__ == "__main__":
    asyncio.run(test_scanner()) 