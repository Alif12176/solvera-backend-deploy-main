import os
import psycopg2
from dotenv import load_dotenv

# 1. Force load the .env file
load_dotenv()

# Get URL from environment
url = os.getenv("DATABASE_URL")

print(f"\n--- DIAGNOSTIC START ---")
print(f"1. Python thinks the URL is: {url}")

try:
    # 2. Connect directly using psycopg2 (what SQLAlchemy uses under the hood)
    conn = psycopg2.connect(url)
    cur = conn.cursor()

    # 3. Ask the Database who it is
    cur.execute("SELECT current_database();")
    db_name = cur.fetchone()[0]
    print(f"2. Connected to ACTUAL Database name: '{db_name}'")

    cur.execute("SELECT current_user;")
    user_name = cur.fetchone()[0]
    print(f"3. Connected as User: '{user_name}'")

    cur.execute("SHOW search_path;")
    path = cur.fetchone()[0]
    print(f"4. Search Path is: '{path}'")

    # 4. Check if the table exists in the metadata
    print("\n--- CHECKING TABLES ---")
    cur.execute("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_name = 'service_pages';
    """)
    tables = cur.fetchall()

    if not tables:
        print("❌ CRITICAL: The table 'service_pages' was NOT found in this database.")
        print("   This proves you are connected to a different database/branch than your Dashboard.")
    else:
        print(f"✅ FOUND: {tables}")
        # Try a simple select
        cur.execute("SELECT count(*) FROM service_pages;")
        count = cur.fetchone()[0]
        print(f"   Row count: {count}")

    conn.close()

except Exception as e:
    print(f"\n❌ CONNECTION ERROR: {e}")

print("--- DIAGNOSTIC END ---\n")