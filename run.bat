@echo off
chcp 65001 > nul
echo.
echo ===============================================
echo    EJECUTANDO TeloCambio - Sprint 1 ✅
echo ===============================================
echo.

echo Verificando instalación...
if not exist "backend\venv" (
    echo ❌ Primero ejecuta 'install.bat'
    pause
    exit /b 1
)

echo Iniciando Backend (Django)...
start "TeloCambio Backend" cmd /k "cd backend && call venv\Scripts\activate && python manage.py runserver"
echo ✓ Backend iniciando en http://localhost:8000

echo Esperando 5 segundos para que el backend inicie...
timeout /t 5 /nobreak > nul

echo Iniciando Frontend (React)...
start "TeloCambio Frontend" cmd /k "cd frontend && npm start"
echo ✓ Frontend iniciando en http://localhost:3000

echo.
echo ===============================================
echo    ✅ PROYECTO EN EJECUCIÓN
echo ===============================================
echo.
echo 📍 Backend:  http://localhost:8000
echo 📍 Frontend: http://localhost:3000
echo 📍 Admin:    http://localhost:8000/admin
echo.
echo ⚡ Estado: Sprint 1 Completo - Listo para Sprint 2
echo.
echo Presiona cualquier tecla para cerrar este mensaje...
pause > nul