@echo off
echo ライブラリをインストールしています...

:: 現在の環境で pip 自体を最新にする
python -m pip install --upgrade pip 

:: 必要なライブラリをまとめてインストール
python -m pip install customtkinter requests psutil Pillow 

echo ------------------------------------------
echo 処理が完了しました。
pause