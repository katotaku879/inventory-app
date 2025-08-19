#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在庫管理アプリケーション
メインエントリーポイント（メインウィンドウ版）
"""

import sys
from pathlib import Path

# PySide6のGUI部品をインポート
from PySide6.QtWidgets import QApplication, QMessageBox

# 自作モジュールをインポート
from views.main_window import MainWindow
from models.database import create_database

def initialize_app():
    """
    アプリケーションの初期化処理
    """
    try:
        # データベースを作成（存在しない場合のみ）
        create_database()
        print("データベースの初期化が完了しました")
        return True
        
    except Exception as e:
        print(f"アプリケーション初期化エラー: {e}")
        return False

def main():
    """
    アプリケーションのメイン関数
    """
    # QApplicationオブジェクトを作成（PySide6アプリに必須）
    app = QApplication(sys.argv)
    
    # アプリケーションの基本情報を設定
    app.setApplicationName("在庫管理アプリ")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("mkykr")
    
    # アプリケーションを初期化
    if not initialize_app():
        # 初期化に失敗した場合はエラーメッセージを表示して終了
        QMessageBox.critical(None, "初期化エラー", 
                           "アプリケーションの初期化に失敗しました。\n"
                           "データベースファイルの作成権限を確認してください。")
        sys.exit(1)
    
    try:
        # メインウィンドウを作成
        main_window = MainWindow()
        
        # ウィンドウを表示
        main_window.show()
        
        print("在庫管理アプリを開始しました")
        
        # アプリケーションのメインループを開始
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"アプリケーション実行エラー: {e}")
        QMessageBox.critical(None, "実行エラー", 
                           f"アプリケーションでエラーが発生しました:\n{e}")
        sys.exit(1)

# このファイルが直接実行された場合のみmain()を呼び出す
if __name__ == "__main__":
    main()