#!/usr/bin/env python

"""
Script to reset migrations when switching from SQLite to MySQL
This will delete all migration files and recreate them for a fresh start
"""

import os
import shutil
import subprocess

def run_command(command):
    """Run a shell command and print its output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode

def delete_migrations():
    """Delete all migration files"""
    app_dirs = ['bawabati_app', 'courses', 'grades', 'students', 'teachers']
    
    for app in app_dirs:
        migrations_dir = os.path.join(app, 'migrations')
        if os.path.exists(migrations_dir):
            # Keep __init__.py file if it exists
            init_file = os.path.join(migrations_dir, '__init__.py')
            has_init = os.path.exists(init_file)
            
            for file in os.listdir(migrations_dir):
                if file != '__init__.py' and file.endswith('.py'):
                    file_path = os.path.join(migrations_dir, file)
                    print(f"Removing migration file: {file_path}")
                    os.remove(file_path)
            
            # Recreate __init__.py if it was deleted
            if not has_init:
                with open(init_file, 'w') as f:
                    pass
            
            # Delete __pycache__ if it exists
            pycache_dir = os.path.join(migrations_dir, '__pycache__')
            if os.path.exists(pycache_dir):
                print(f"Removing pycache directory: {pycache_dir}")
                shutil.rmtree(pycache_dir)
    
    print("All migration files have been deleted.")

def main():
    """Main function to reset migrations"""
    # Delete old migrations
    delete_migrations()
    
    # Create new migrations
    run_command('python manage.py makemigrations bawabati_app')
    run_command('python manage.py makemigrations courses')
    run_command('python manage.py makemigrations grades')
    run_command('python manage.py makemigrations students')
    run_command('python manage.py makemigrations teachers')
    
    print("\nAll migrations have been reset. Now you can run:")
    print("python manage.py migrate")

if __name__ == "__main__":
    main() 