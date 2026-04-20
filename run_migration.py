#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migration scripts
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def run_migration(sql_file_path):
    """Execute SQL migration file"""
    
    # Database connection parameters
    db_config = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'pglocal',
        'user': 'postgres',
        'password': '12345'
    }
    
    try:
        # Read the SQL file
        if not os.path.exists(sql_file_path):
            print(f"Error: File not found: {sql_file_path}")
            return False
            
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"📂 Reading migration file: {sql_file_path}")
        print(f"📊 SQL content size: {len(sql_content)} bytes")
        
        # Connect to database
        print("\n🔗 Connecting to database...")
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"✅ Connected to {db_config['database']} as {db_config['user']}")
        
        # Execute the SQL
        print("\n⚙️  Executing migration script...")
        cursor.execute(sql_content)
        
        print("✅ Migration executed successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        print(f"   Error code: {e.pgcode}")
        print(f"   Error details: {e.pgerror}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    migration_file = os.path.join(script_dir, 'migrations', 'create_views.sql')
    
    success = run_migration(migration_file)
    sys.exit(0 if success else 1)
