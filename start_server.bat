@echo off
title ettiene-wium.co.za
cd /d "%~dp0public"
echo Public CV site: http://localhost:8097
echo Press Ctrl+C to stop.
php -S localhost:8097 router.php
