@echo off
:: MakuUP Studio — Start Backend Server
:: Applies OpenSSL legacy fix for Python 3.14 + MongoDB Atlas TLS compatibility

set OPENSSL_CONF=%~dp0openssl.cnf
echo [MakuUP] Starting backend with SSL fix...
echo [MakuUP] OPENSSL_CONF=%OPENSSL_CONF%

call venv\Scripts\python.exe manage.py runserver --noreload
