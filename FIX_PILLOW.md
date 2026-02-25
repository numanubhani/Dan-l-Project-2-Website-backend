# Fix for Pillow Installation Issue

The issue is that Pillow 10.2.0 tries to build from source on Windows and fails. Here's how to fix it:

## Solution 1: Install without Pillow first, then add Pillow

```powershell
# Install all dependencies except Pillow
pip install Django==5.0.1 djangorestframework==3.14.0 django-cors-headers==4.3.1 python-decouple==3.8

# Then install Pillow (latest version has pre-built wheels)
pip install Pillow
```

## Solution 2: Use the install script

Run the PowerShell script:
```powershell
.\install_dependencies.ps1
```

## Solution 3: Install packages one by one

```powershell
pip install Django==5.0.1
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1
pip install python-decouple==3.8
pip install Pillow
```

## Solution 4: Skip Pillow for now (optional)

If you don't need image uploads immediately, you can skip Pillow and add it later. The app will work without it, but avatar uploads won't work.

```powershell
pip install Django==5.0.1 djangorestframework==3.14.0 django-cors-headers==4.3.1 python-decouple==3.8
```

Then comment out the avatar field in the User model temporarily.

## Recommended: Try Solution 1

This should work because newer versions of Pillow have pre-built wheels for Windows.

