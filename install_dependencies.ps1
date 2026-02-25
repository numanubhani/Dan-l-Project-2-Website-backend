# PowerShell script to install dependencies
# This script installs packages one by one to avoid Pillow build issues

Write-Host "Installing Django..." -ForegroundColor Green
pip install Django==5.0.1

Write-Host "Installing Django REST Framework..." -ForegroundColor Green
pip install djangorestframework==3.14.0

Write-Host "Installing Django CORS Headers..." -ForegroundColor Green
pip install django-cors-headers==4.3.1

Write-Host "Installing Python Decouple..." -ForegroundColor Green
pip install python-decouple==3.8

Write-Host "Installing Pillow (latest version with pre-built wheels)..." -ForegroundColor Green
pip install Pillow

Write-Host "`nAll dependencies installed successfully!" -ForegroundColor Green

