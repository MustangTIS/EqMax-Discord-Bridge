@echo off
cd /d %~dp0
echo === EqMax守護神ボット 起動中 ===
:: ボットを起動すれば、ボットが勝手にEqMaxを起動監視してくれます
python Eq_Watchdog.py
pause