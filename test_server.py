#!/usr/bin/env python
"""Simple Django test server to verify Django functionality."""
import os
import sys

def main():
    """Run a minimal Django application."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
        
        # Check if Django is properly installed
        import django
        print(f"Django version: {django.get_version()}")
        
        # Use runserver with --noreload to prevent watchdog issues
        execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:8005', '--noreload'])
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    except Exception as e:
        print(f"Error starting Django: {e}")

if __name__ == '__main__':
    main()