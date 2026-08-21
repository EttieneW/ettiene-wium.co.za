@echo off
title ettiene-wium.com
cd /d "%~dp0public"
echo Public CV site: http://localhost:8097  (production: https://ettiene-wium.com)
echo Press Ctrl+C to stop.
php -S localhost:8097 router.php
