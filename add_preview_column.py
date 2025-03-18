import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from django.db import connection

def add_preview_url_column():
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE carti_catalog ADD COLUMN IF NOT EXISTS preview_url VARCHAR(255);")
        print("Added preview_url column to carti_catalog table")

if __name__ == "__main__":
    add_preview_url_column()