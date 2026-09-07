#!/usr/bin/env python
"""
Migration script for production deployment
Run this after deployment to create database tables
"""
import os
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Run migrations
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("🔄 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrations completed!")