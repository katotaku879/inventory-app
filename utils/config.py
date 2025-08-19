 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アプリケーション設定管理
定数や設定値をまとめて管理
"""

import os
from pathlib import Path

# アプリケーション基本情報
APP_NAME = "在庫管理アプリ"
APP_VERSION = "0.1.0"
#アプリの作者名（"mkykr"）をプログラム内で定数として管理・利用できます。
APP_AUTHOR = "mkykr"

# ウィンドウサイズ設定
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# データベース設定
DB_NAME = "inventory.db"

# ファイルパス設定
def get_app_data_dir():
    """
    アプリケーションデータの保存ディレクトリを取得
    
    Returns:
        Path: データ保存用ディレクトリのパス
    """
    # ユーザーのホームディレクトリ内にアプリ用フォルダを作成
    app_dir = Path.home() / ".inventory_app"
    
    # フォルダが存在しない場合は作成
    app_dir.mkdir(exist_ok=True)
    
    return app_dir

def get_database_path():
    """
    データベースファイルのパスを取得
    
    Returns:
        Path: データベースファイルのパス
    """
    #アプリ用データフォルダ内のデータベースファイル（DB_NAME）のパスを取得できます。
    return get_app_data_dir() / DB_NAME

# カテゴリ設定
DEFAULT_CATEGORIES = [
    "日用品",
    "洗剤",
    "食品",
    "調味料",
    "飲料",
    "冷凍食品",
    "その他"
]

# 保存場所設定
DEFAULT_STORAGE_LOCATIONS = [
    "キッチン",
    "冷蔵庫",
    "冷凍庫",
    "クローゼット",
    "お風呂",
    "トイレ",
    "洗面所",
    "その他"
]

# 購入場所設定
DEFAULT_PURCHASE_LOCATIONS = [
    "スーパー",
    "ドラッグストア",
    "コンビニ",
    "ネット通販",
    "ホームセンター",
    "ドン・キホーテ",
    "100円ショップ",
    "その他"
]

# 在庫状況の色設定（HTMLカラーコード）
STOCK_COLORS = {
    'out_of_stock': '#ffebee',  # 薄い赤 危険（在庫切れ）
    'low_stock': '#fff8e1',     # 薄い黄色 注意（在庫少）
    'normal': '#ffffff'         # 白 正常（在庫あり）
}

# テスト用設定　デバッグ用の特別な動作モードを有効化するためのフラグ
DEBUG_MODE = True  # 開発中はTrue、完成時はFalse

# 設定テスト関数
def test_config():
    """
    設定の動作テスト
    """
    print("=== 設定情報テスト ===")
    print(f"アプリ名: {APP_NAME}")
    print(f"バージョン: {APP_VERSION}")
    print(f"データディレクトリ: {get_app_data_dir()}")
    print(f"データベースパス: {get_database_path()}")
    print(f"デフォルトカテゴリ数: {len(DEFAULT_CATEGORIES)}")
    print(f"デバッグモード: {DEBUG_MODE}")

# テスト実行
if __name__ == "__main__":
    test_config()
