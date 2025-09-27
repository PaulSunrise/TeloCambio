@echo off
chcp 65001 > nul
echo.
echo ===============================================
echo    INSTALADOR AUTOMÁTICO - TeloCambio
echo ===============================================
echo.

echo [1/5] Verificando Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.8+ desde python.org
    pause
    exit /b 1
)
echo ✓ Python detectado

echo [2/5] Verificando Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no encontrado. Instala Node.js desde nodejs.org
    pause
    exit /b 1
)
echo ✓ Node.js detectado

echo [3/5] Instalando dependencias del Backend (Python)...
cd backend
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)
echo Activando entorno virtual...
call venv\Scripts\activate
echo Instalando dependencias...
pip install -r requirements.txt
echo ✓ Backend instalado

echo [4/5] Instalando dependencias del Frontend (React)...
cd ..\frontend
echo Instalando paquetes npm...
npm install
echo ✓ Frontend instalado

echo [5/5] Configurando base de datos...
cd ..\backend
call venv\Scripts\activate
python manage.py migrate
echo ✓ Base de datos configurada

echo.
echo ===============================================
echo    ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo Para ejecutar el proyecto:
echo.
echo MÉTODO 1 - Automático:
echo   1. Ejecuta 'run.bat' (recomendado)
echo.
echo MÉTODO 2 - Manual:
echo   Backend: cd backend && venv\Scripts\activate && python manage.py runserver
echo   Frontend: cd frontend && npm start
echo.
echo URLs:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   Admin:    http://localhost:8000/admin
echo.
pause