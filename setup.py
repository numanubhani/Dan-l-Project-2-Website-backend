"""
Setup script for VPulse Backend
Run this script to initialize the Django project
"""
import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}\n")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    if result.stdout:
        print(result.stdout)
    return True


def main():
    """Main setup function"""
    print("\n" + "="*50)
    print("VPulse Backend Setup")
    print("="*50 + "\n")
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        if not run_command("python -m venv venv", "Create virtual environment"):
            print("Failed to create virtual environment")
            return
    
    # Activate virtual environment and install dependencies
    if sys.platform == 'win32':
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    print("Installing dependencies...")
    if not run_command(f"{pip_command} install -r requirements.txt", "Install dependencies"):
        print("Failed to install dependencies")
        return
    
    print("Running migrations...")
    if not run_command(f"{python_command} manage.py makemigrations", "Create migrations"):
        print("Failed to create migrations")
        return
    
    if not run_command(f"{python_command} manage.py migrate", "Apply migrations"):
        print("Failed to apply migrations")
        return
    
    print("Creating default admin user...")
    if not run_command(f"{python_command} manage.py create_default_admin", "Create admin user"):
        print("Failed to create admin user")
        return
    
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nDefault Admin Credentials:")
    print("  Username: admin")
    print("  Email: admin@vpulse.com")
    print("  Password: admin123")
    print("\nTo start the server:")
    if sys.platform == 'win32':
        print("  venv\\Scripts\\python manage.py runserver")
    else:
        print("  venv/bin/python manage.py runserver")
    print("\nAdmin Panel: http://localhost:8000/admin/")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()

