# 在庫管理アプリ 
 
PySide6を使用したデスクトップ在庫管理アプリケーション 
 
## 機能 
 
- 商品の追加・編集・削除 
- 在庫数の増減管理 
- 検索・フィルタリング機能 
- 期限切れ警告 
- 在庫状況の色分け表示 
- 在庫履歴の管理 
- データの永続化（SQLite） 
 
## 必要環境 
 
- Python 3.8+ 
- PySide6 
 
## インストール 
 
1. リポジトリをクローン 
```bash 
git clone <your-repository-url> 
cd inventory_app 
``` 
 
2. 仮想環境を作成（推奨） 
```bash 
python -m venv env 
env\Scripts\activate 
``` 
 
3. 依存関係をインストール 
```bash 
pip install -r requirements.txt 
``` 
 
## 使用方法 
 
```bash 
python main.py 
``` 
