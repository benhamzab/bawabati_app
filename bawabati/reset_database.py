#!/usr/bin/env python

"""
Reset and recreate the MySQL database for the EMSI Student Management System
This script will:
1. Drop the existing database
2. Create a new empty database
3. Delete all migrations
4. Recreate migrations for all apps
5. Apply migrations to create all tables
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

# Add the project directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def run_command(command):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    if process.stdout:
        print(process.stdout)
    if process.stderr:
        print(f"Error: {process.stderr}")
    return process.returncode

def reset_mysql_database():
    """Reset MySQL database"""
    print("\n1. Resetting MySQL database...\n")
    
    # Get MySQL root password
    print("Enter your MySQL root password:")
    mysql_password = getpass.getpass()
    
    # MySQL commands to drop and recreate database
    mysql_commands = f"""DROP DATABASE IF EXISTS bawabati_db;
CREATE DATABASE bawabati_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"""
    
    # Create a temporary SQL file
    with open("temp_reset.sql", "w") as f:
        f.write(mysql_commands)
    
    # Execute MySQL commands
    mysql_cmd = f"mysql -u root -p{mysql_password} < temp_reset.sql"
    run_command(mysql_cmd)
    
    # Clean up
    if os.path.exists("temp_reset.sql"):
        os.remove("temp_reset.sql")
    
    return True

def delete_migrations():
    """Delete all migration files except __init__.py"""
    print("\n2. Deleting existing migrations...\n")
    
    # List of apps with migrations
    apps = ['bawabati_app', 'students', 'teachers', 'courses', 'grades']
    
    for app in apps:
        migrations_path = BASE_DIR / app / 'migrations'
        if os.path.exists(migrations_path):
            print(f"Cleaning migrations for {app}...")
            for file_name in os.listdir(migrations_path):
                if file_name != '__init__.py' and file_name.endswith('.py'):
                    file_path = os.path.join(migrations_path, file_name)
                    print(f"  Deleting {file_path}")
                    os.remove(file_path)

def create_and_apply_migrations():
    """Create and apply migrations for all apps"""
    print("\n3. Creating new migrations...\n")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bawabati.settings')
    
    # Create migrations for each app
    apps = ['bawabati_app', 'students', 'teachers', 'courses', 'grades']
    for app in apps:
        run_command(f"python manage.py makemigrations {app}")
    
    print("\n4. Applying migrations...\n")
    run_command("python manage.py migrate")
    
    return True

def create_superuser():
    """Create a superuser for testing"""
    print("\n5. Creating a superuser for testing...\n")
    run_command("python manage.py createsuperuser")
    
    return True

def main():
    print("=== Database Reset Script ===")
    print("WARNING: This will delete ALL data in your database!")
    print("Make sure you have a backup if needed.")
    
    confirm = input("\nDo you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Reset database
    if not reset_mysql_database():
        print("Failed to reset MySQL database. Exiting.")
        return
    
    # Delete migrations
    delete_migrations()
    
    # Create and apply migrations
    if not create_and_apply_migrations():
        print("Failed to create and apply migrations. Exiting.")
        return
    
    # Ask if user wants to create a superuser
    create_su = input("\nDo you want to create a superuser? (y/n): ")
    if create_su.lower() == 'y':
        create_superuser()
    
    print("\n=== Database reset complete ===")
    print("✓ Your database has been reset and all tables created")
    print("✓ You should now be able to login to the system")
    print("\nNext steps:")
    print("1. Start the Django development server:")
    print("   python manage.py runserver")
    print("2. Access the admin interface at:")
    print("   http://127.0.0.1:8000/admin/")
    print("3. Test the login functionality at:")
    print("   http://127.0.0.1:8000/login/")

if __name__ == "__main__":
    main() 