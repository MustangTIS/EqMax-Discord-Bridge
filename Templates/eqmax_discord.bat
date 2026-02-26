@echo off
cd /d %~dp0
echo === EqMax-Discord Bridge booting ===
:: ボットを起動すれば、ボットが勝手にEqMaxを起動してくれます
python eqmax_discord.py
pause