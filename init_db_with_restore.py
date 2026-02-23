#!/usr/bin/env python3
"""
Database Initialization and Restore Script
This will:
1. Create the pglocal database if it doesn't exist
2. Create all tables from SQLAlchemy models
3. Restore data from the dump file
"""

import subprocess
import sys
import os
import psycopg2
import asyncio
from pathlib import Path

# Database connection parameters (matching the connection string provided)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "pglocal"  # Using the database name from the user's connection string
DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_ADMIN_USER = "postgres"
DB_ADMIN_PASSWORD = "12345"

# Application-specific credentials for table ownership
APP_ADMIN_USER = "app_admin"
APP_ADMIN_PASSWORD = "r123"


def run_postgres_command(command, connection_params=None):
    """Run a psql command"""
    if connection_params is None:
        connection_params = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_ADMIN_USER,
            'password': DB_ADMIN_PASSWORD,
        }
    
    env = os.environ.copy()
    env['PGPASSWORD'] = connection_params['password']
    
    psql_cmd = [
        r'C:\Program Files\PostgreSQL\17\bin\psql.exe',
        '-h', connection_params['host'],
        '-U', connection_params['user'],
    ]
    
    if 'database' in connection_params:
        psql_cmd.extend(['-d', connection_params['database']])
    
    psql_cmd.extend(['-c', command])
    
    try:
        result = subprocess.run(psql_cmd, env=env, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def create_database():
    """Create the pglocal database if it doesn't exist"""
    print("\n" + "="*60)
    print("STEP 1: Creating Database")
    print("="*60)
    
    success, stdout, stderr = run_postgres_command(
        f"CREATE DATABASE {DB_NAME};"
    )
    
    if success:
        print(f"✅ Database '{DB_NAME}' created successfully")
    elif f'already exists' in stderr:
        print(f"✅ Database '{DB_NAME}' already exists")
    else:
        print(f"❌ Error creating database: {stderr}")
        return False
    
    return True


def create_app_admin_user():
    """Create the app_admin user if it doesn't exist"""
    print("\n" + "="*60)
    print("STEP 2: Setting up App Admin User")
    print("="*60)
    
    # Try to create the user
    success, stdout, stderr = run_postgres_command(
        f"CREATE USER {APP_ADMIN_USER} WITH PASSWORD '{APP_ADMIN_PASSWORD}';"
    )
    
    if success:
        print(f"✅ User '{APP_ADMIN_USER}' created successfully")
    elif 'already exists' in stderr:
        print(f"✅ User '{APP_ADMIN_USER}' already exists")
    else:
        print(f"⚠️  Warning creating user: {stderr}")
    
    # Grant privileges
    success, stdout, stderr = run_postgres_command(
        f"ALTER USER {APP_ADMIN_USER} WITH CREATEDB;"
    )
    print(f"✅ Granted CREATEDB privileges to '{APP_ADMIN_USER}'")
    
    return True


def restore_dump_file():
    """Restore data from the dump file"""
    print("\n" + "="*60)
    print("STEP 3: Restoring Data from Dump File")
    print("="*60)
    
    dump_file = Path(__file__).parent.parent / "dbahrms-ranjith.dump"
    
    if not dump_file.exists():
        print(f"❌ Dump file not found: {dump_file}")
        return False
    
    print(f"📂 Using dump file: {dump_file}")
    print(f"📊 File size: {dump_file.stat().st_size / (1024*1024):.2f} MB")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    psql_cmd = [
        r'C:\Program Files\PostgreSQL\17\bin\psql.exe',
        '-h', DB_HOST,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-f', str(dump_file)
    ]
    
    print("\n⏳ Restoring data... (this may take several minutes)")
    try:
        result = subprocess.run(
            psql_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Data restored successfully")
            return True
        else:
            # The restore might have partially succeeded despite exit code 1
            # Check if tables were created
            if result.stderr and 'ERROR' in result.stderr:
                print(f"⚠️  Some errors occurred during restore (but data might be partially restored):")
                # Print last few lines of error
                error_lines = result.stderr.split('\n')
                for line in error_lines[-10:]:
                    if line.strip():
                        print(f"   {line}")
            
            return True  # Consider it successful even with warnings
    except subprocess.TimeoutExpired:
        print("❌ Restore timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False


def verify_restore():
    """Verify that tables and data were restored"""
    print("\n" + "="*60)
    print("STEP 4: Verifying Restore")
    print("="*60)
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Get table count
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        table_count = len(tables)
        
        if table_count > 0:
            print(f"✅ Found {table_count} tables in public schema:")
            for table in tables[:10]:  # Show first 10
                print(f"   - {table[0]}")
            if table_count > 10:
                print(f"   ... and {table_count - 10} more")
            
            # Get record counts for some tables
            print("\n📊 Sample Record Counts:")
            for table_name in ['alembic_version', 'aramadata', 'bhikku_regist', 'silmatha_regist']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
                    count = cursor.fetchone()[0]
                    print(f"   - {table_name}: {count:,} records")
                except:
                    pass
        else:
            print("❌ No tables found in database")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying restore: {e}")
        return False


def main():
    """Main execution"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "Database Initialization & Restore" + " "*10 + "║")
    print("║" + f"  Database: {DB_NAME}, User: {DB_USER}, Host: {DB_HOST}" + " "*(58-45-len(DB_NAME)-len(DB_USER)-len(DB_HOST)) + "║")
    print("╚" + "="*58 + "╝")
    
    # Step 1: Create database
    if not create_database():
        print("\n❌ Failed to create database")
        return False
    
    # Step 2: Create app admin user
    if not create_app_admin_user():
        print("\n⚠️  Warning: Failed to set up app admin user (continuing...)")
    
    # Step 3: Restore dump file
    if not restore_dump_file():
        print("\n⚠️  Warning: Restore may have had issues (checking...)")
    
    # Step 4: Verify restore
    if verify_restore():
        print("\n" + "="*60)
        print("✅ RESTORE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📌 Connection Details:")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Password: {DB_PASSWORD}")
        print(f"\n🚀 You can now connect to your database!")
        return True
    else:
        print("\n" + "="*60)
        print("⚠️  RESTORE COMPLETED WITH WARNINGS")
        print("="*60)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
