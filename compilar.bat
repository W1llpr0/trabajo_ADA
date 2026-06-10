@echo off
REM Compila el proyecto PFSP + Bat Algorithm
g++ -O2 -Wall -std=c++17 src\pfsp.cpp src\bat.cpp src\main.cpp -o pfsp_bat.exe
if %errorlevel% equ 0 (
    echo Compilacion exitosa: pfsp_bat.exe
) else (
    echo Error de compilacion
    exit /b 1
)
