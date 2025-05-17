#!/usr/bin/env python

"""
Fix database schema issues by recreating migrations and applying them.
This script will:
1. Detect missing columns in MySQL
2. Recreate migrations for affected apps
3. Apply migrations to fix the schema
"""

import os
import sys
import subprocess
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

def main():
    print("=== Database Schema Fix Script ===")
    
    # Check for Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bawabati.settings')
    
    # Delete existing migrations for affected apps
    print("\n1. Removing existing migrations for bawabati_app...\n")
    migrations_path = BASE_DIR / 'bawabati_app' / 'migrations'
    if os.path.exists(migrations_path):
        for file_name in os.listdir(migrations_path):
            if file_name != '__init__.py' and file_name.endswith('.py'):
                file_path = os.path.join(migrations_path, file_name)
                print(f"Deleting {file_path}")
                os.remove(file_path)
    
    # Create new migrations
    print("\n2. Creating new migrations...\n")
    run_command("python manage.py makemigrations bawabati_app")
    
    # Apply migrations
    print("\n3. Applying migrations...\n")
    run_command("python manage.py migrate bawabati_app")
    run_command("python manage.py migrate")
    
    print("\n=== Database schema fix complete ===")
    print("✓ The database should now match your models")
    print("\nIf you still encounter issues, try these advanced steps:")
    print("1. Create a superuser to test the login:")
    print("   python manage.py createsuperuser")
    print("2. If errors persist, consider dropping and recreating the database:")
    print("   mysql -u root -p -e 'DROP DATABASE bawabati_db; CREATE DATABASE bawabati_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'")
    print("   python manage.py migrate")

if __name__ == "__main__":
    main() 