# Add and replace INSTALL_APPS in settings.py
```
INSTALLED_APPS = [
    ...
    # Add django-admin-style app
    'django-admin-style',
    
    # Replace 'django.contrib.admin',
    'django-admin-style.admin_site.AdminConfigExt',
    
    # 'django.contrib.auth',
    'django-admin-style.apps.AuthConfig',
    ...
]
```

# Add TEMPLATES in settings.py
```
TEMPLATES = [
    {
        'DIRS': [
            ...
            os.path.join(BASE_DIR, "django-admin-style/templates")
            ...
        ]
    }
]
```

# Add STATICFILES_DIRS in settings.py
```
STATICFILES_DIRS = [
    ...
    os.path.join(BASE_DIR, "django-admin-style/assets"),
    ...
]
```