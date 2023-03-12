@echo off
cd DokuWikiStick
>nul 2>nul chcp 65001
taskkill >nul 2>nul /f /im mapache.exe
goto begin
 
:usage
echo Usage: %~n0
echo.
echo Starts DokuWiki on a Stick (http://www.dokuwiki.org/dokuwiki_on_a_stick)
echo and waits for user to press a key to stop.
goto end
 
:begin
if not "%1"=="" goto usage
cd server
start "Apache server" /B mapache.exe
echo DokuWiki 已启动...
echo.
 
:runbrowser
echo 你的浏览器将会打开 http://localhost:8800
echo.
if exist ..\dokuwiki\conf\local.php (
	start http://localhost:8800/
) else (
	start http://localhost:8800/install.php
)

:end
