@echo off
cd /d %~dp0
echo Initializing EqMax 監視ツール...
:: ボットを起動すれば、ボットが勝手にEqMaxを起動監視してくれます
python Eq_Watchdog.py
pause