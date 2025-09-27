@echo off
chcp 65001 > nul
echo.
echo ===============================================
echo    GUÍA PARA SUBIR TeloCambio A GITHUB
echo ===============================================
echo.

echo PASO 1: Crear repositorio en GitHub.com
echo   1. Ve a https://github.com
echo   2. Inicia sesión o crea cuenta
echo   3. Click en '+' -> New repository
echo   4. Nombre: TeloCambio
echo   5. Descripción: Plataforma de trueques comunitarios
echo   6. Visibilidad: Public (gratis) o Private
echo   7. NO marcar 'Add README'
echo   8. Click 'Create repository'
echo.

echo PASO 2: Ejecutar estos comandos EN ORDEN:
echo.
echo cd "C:\Users\paul lopez ortiz\Desktop\Telo_cambio"
echo git init
echo git add .
echo git commit -m "Sprint 1 completo: Sistema multi-tenant con autenticación JWT"
echo git branch -M main
echo git remote add origin https://github.com/PaulSunrise/TeloCambio.git
echo git push -u origin main
echo.

echo ✅ ¡COMANDOS LISTOS CON TU USUARIO PaulSunrise!
echo.

echo PASO 3: Para que tus compañeros clonen:
echo   git clone https://github.com/PaulSunrise/TeloCambio.git
echo   cd TeloCambio
echo   install.bat
echo   run.bat
echo.

echo ✅ Listo! Tu equipo puede usar el proyecto.
echo.

pause