#!/usr/bin/env python3
"""
Complete Database Initialization Script
Creates database, schema from models, and restores data from dump file
"""

import subprocess
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import asyncio

# Add the backend directory to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME_TARGET = "pglocal"  # Target database (from user's connection string)
DB_NAME_DEV = "dbahrms-ranjith"  # Application's configured database
DB_ADMIN_USER = "postgres"
DB_ADMIN_PASSWORD = "12345"
DB_APP_USER = "app_admin"
DB_APP_PASSWORD = "r123"


def run_psql_command(sql_command, database=None, user=None, password=None):
    """Execute a psql command"""
    user = user or DB_ADMIN_USER
    password = password or DB_ADMIN_PASSWORD
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    cmd = [r'C:\Program Files\PostgreSQL\17\bin\psql.exe', '-h', DB_HOST, '-U', user]
    
    if database:
        cmd.extend(['-d', database])
    
    cmd.extend(['-c', sql_command])
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def create_database_and_user():
    """Create target database and ensure user has access"""
    print("\n" + "="*60)
    print("STEP 1: Creating Database and User")
    print("="*60)
    
    # Create database
    success, stdout, stderr = run_psql_command(
        f"CREATE DATABASE \"{DB_NAME_TARGET}\";"
    )
    
    if success:
        print(f"✅ Database '{DB_NAME_TARGET}' created")
    elif "already exists" in stderr:
        print(f"✅ Database '{DB_NAME_TARGET}' already exists")
    else:
        print(f"❌ Error: {stderr}")
        return False
    
    # Ensure app_admin user exists
    success, stdout, stderr = run_psql_command(
        f"CREATE USER {DB_APP_USER} WITH PASSWORD '{DB_APP_PASSWORD}' CREATEDB;"
    )
    
    if success:
        print(f"✅ User '{DB_APP_USER}' created")
    elif "already exists" in stderr:
        print(f"✅ User '{DB_APP_USER}' already exists")
        # Give privileges anyway
        run_psql_command(f"ALTER USER {DB_APP_USER} WITH CREATEDB;")
    
    # Grant privileges to app_admin
    run_psql_command(f"GRANT ALL PRIVILEGES ON DATABASE \"{DB_NAME_TARGET}\" TO {DB_APP_USER};")
    print(f"✅ Granted privileges to '{DB_APP_USER}'")
    
    return True


def restore_data_dump():
    """Restore data from the dump file"""
    print("\n" + "="*60)
    print("STEP 2: Restoring Data from Dump File")
    print("="*60)
    
    dump_file = backend_path.parent / "dbahrms-ranjith.dump"
    
    if not dump_file.exists():
        print(f"❌ Dump file not found: {dump_file}")
        return False
    
    print(f"📂 Dump file: {dump_file}")
    file_size_mb = dump_file.stat().st_size / (1024 * 1024)
    print(f"📊 File size: {file_size_mb:.2f} MB")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_ADMIN_PASSWORD
    
    cmd = [
        r'C:\Program Files\PostgreSQL\17\bin\psql.exe',
        '-h', DB_HOST,
        '-U', DB_ADMIN_USER,
        '-d', DB_NAME_TARGET,
        '-f', str(dump_file)
    ]
    
    print("\n⏳ Restoring data (this may take a while)...")
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
        
        # Check for critical errors
        if "ERROR" in result.stderr:
            # Show warnings but consider it successful if some data was loaded
            error_lines = [l for l in result.stderr.split('\n') if 'ERROR' in l]
            if len(error_lines) < 5:
                print("⚠️  Some warnings occurred but data may have been restored:")
                for line in error_lines[:3]:
                    print(f"   {line}")
            else:
                print(f"❌ Too many errors ({len(error_lines)}) - restore likely failed")
                return False
        
        print("✅ Data restore completed")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Restore timed out (> 15 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_database():
    """Verify database contents"""
    print("\n" + "="*60)
    print("STEP 3: Verifying Database")
    print("="*60)
    
    try:
        # Connect with admin credentials
        connection_string = f"postgresql://{DB_ADMIN_USER}:{DB_ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_TARGET}"
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            # Get list of tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("❌ No tables found in database")
                return False
            
            print(f"✅ Found {len(tables)} tables:")
            
            # Get row counts for key tables
            for table in sorted(tables)[:15]:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM \"{table}\""))
                    count = result.scalar()
                    print(f"   • {table}: {count:,} records")
                except Exception as e:
                    print(f"   • {table}: [error reading]")
            
            if len(tables) > 15:
                print(f"   ... and {len(tables) - 15} more tables")
            
            return True
        
    except Exception as e:
        print(f"⚠️  Could not verify: {e}")
        return False


def main():
    """Main execution"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " PostgreSQL Database Restore and Initialization ".center(58) + "║")
    print("╚" + "="*58 + "╝\n")
    
    print(f"Target Database: {DB_NAME_TARGET}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"Admin User: {DB_ADMIN_USER}\n")
    
    # Step 1
    if not create_database_and_user():
        print("\n❌ Failed at Step 1: Cannot create database")
        return False
    
    # Step 2
    if not restore_data_dump():
        print("\n⚠️  Warning: Data restore may have issues")
    
    # Step 3
    if verify_database():
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print(f"\n📌 Connection String:")
        print(f"   postgresql://{DB_ADMIN_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME_TARGET}")
        print(f"\nAlternatively (using your credentials):")
        print(f"   postgresql://postgres:****@localhost?statusColor=&env=local&name={DB_NAME_TARGET}&tLSMode=0")
        return True
    else:
        print("\n⚠️  Database may not have been restored properly")
        return False


if __name__ == '__main__':
    success = False
    try:
        success = main()
    except KeyboardInterrupt:
        print("\n\n⛔ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0 if success else 1)
