# 🏪 日用品在庫管理アプリ
**個人の実体験から生まれた実用的なデスクトップアプリケーション**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-green.svg)](https://doc.qt.io/qtforpython/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-orange.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 プロジェクト概要

### 開発背景・課題解決
一人暮らしをする中で、**日用品の在庫切れに気づかず困る場面が多々発生**していました。トイレットペーパーや洗剤などの必需品が突然切れて、急いで買い物に行く羽目になることが頻繁にありました。

この実体験から「**現在の在庫数を一目で把握し、計画的な買い物ができるアプリ**」の必要性を感じ、自ら開発に取り組みました。

### 解決したこと
- ✅ **在庫状況の可視化**: 一目で在庫切れ・在庫少の商品を把握
- ✅ **買い忘れ防止**: 最小在庫数を下回った時点で警告表示
- ✅ **購入履歴管理**: いつ・何を・どこで買ったかの記録
- ✅ **効率的な買い物**: 在庫状況に基づいた計画的な購入

## 🛠️ 技術スタック

### **フロントエンド**
- **PySide6 (Qt6)** - モダンなクロスプラットフォームGUI
- **カスタムウィジェット** - 独自のテーブル表示とダイアログ

### **バックエンド**
- **Python 3.8+** - 型ヒント活用によるモダンな実装
- **SQLite** - 軽量でファイルベースのデータベース
- **MVC アーキテクチャ** - 保守性を重視した設計

### **データベース設計**
```sql
-- 正規化されたテーブル設計
products (商品マスタ)
├── 基本情報 (名前、ブランド、カテゴリ)
├── 在庫情報 (現在数、最小数)
└── 購入情報 (場所、価格、期限)

stock_history (在庫履歴)
├── 操作記録 (購入、使用、調整)
├── 数量変化と結果
└── 外部キー制約による整合性保証
```

## 🏗️ アーキテクチャ・設計パターン

### **MVCパターンの採用**
```
📁 models/          # データモデル層
├── database.py     # データベース操作
├── product.py      # 商品オブジェクト
└── stock_history.py # 履歴オブジェクト

📁 views/           # ビュー層
├── main_window.py  # メインUI
└── dialogs.py      # ダイアログ類

📁 utils/           # ユーティリティ
└── config.py       # 設定管理
```

### **オブジェクト指向設計**
```python
class Product:
    def get_stock_status(self) -> str:
        """ビジネスロジックをモデルに集約"""
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock <= self.min_stock:
            return 'low_stock'
        return 'normal'
    
    def is_expired(self) -> bool:
        """期限切れ判定ロジック"""
        if not self.expiry_date:
            return False
        
        try:
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
            return expiry < datetime.now()
        except ValueError:
            return False
```

### **データ処理フロー**
```
📊 データ読み取り
SQLite → sqlite3.Row → Product Object → UI Widget → Visual Display

💾 データ更新
User Input → Validation → Object → Database Transaction → UI Refresh

🔍 リアルタイム検索
Search Input → Filter Logic → Data Filtering → Table Refresh
```

## 🎨 UI/UX の工夫

### **視覚的フィードバック**
テーブルの行を在庫状況に応じて色分け表示：
- **🔴 在庫切れ**: 薄い赤色の背景
- **🟡 在庫少**: 薄い黄色の背景  
- **🟢 正常**: 薄い緑色の背景
- **🚨 期限切れ**: 濃い赤色（最優先表示）

```python
def set_row_color(self, row, status, is_expired=False):
    if is_expired:
        color = QColor(255, 200, 200)  # 濃い赤（期限切れ最優先）
    elif status == 'out_of_stock':
        color = QColor(255, 235, 238)  # 薄い赤
    elif status == 'low_stock':
        color = QColor(255, 248, 225)  # 薄い黄色
    else:
        color = QColor(248, 255, 248)  # 薄い緑
```

### **ユーザビリティ向上機能**
- **キーボードショートカット**: `Ctrl+N`(新規), `Ctrl+F`(検索), `F5`(更新), `Delete`(削除)
- **リアルタイム検索**: 入力と同時に結果をフィルタリング
- **複数条件フィルタ**: カテゴリ・在庫状況・期限で絞り込み
- **警告システム**: 在庫切れ・期限切れの即座な通知
- **直感的操作**: ダブルクリック編集、右クリックメニュー

### **データ整合性の保証**
```python
def update_stock_and_add_history(self, stock_data: dict) -> bool:
    """トランザクション処理で在庫更新と履歴記録を同期"""
    try:
        with self._get_connection() as conn:
            # 1. 在庫数更新
            conn.execute("UPDATE products SET current_stock = ?", ...)
            
            # 2. 履歴記録追加
            conn.execute("INSERT INTO stock_history VALUES", ...)
            
            # 両方成功時のみコミット
            conn.commit()
            return True
            
    except Exception as e:
        # 自動ロールバック
        print(f"更新失敗: {e}")
        return False
```

## 📊 主要機能

### **1. 商品管理**
- **詳細情報登録**: 商品名、ブランド、サイズ、価格、購入場所
- **カテゴリ分類**: 日用品、洗剤、食品、調味料、飲料等
- **保存場所管理**: キッチン、冷蔵庫、冷凍庫、トイレ、お風呂等
- **消費期限管理**: 期限切れ警告とアラート表示

### **2. 在庫管理**
- **購入記録**: 在庫増加と購入履歴の自動記録
- **使用記録**: 在庫減少と使用履歴の管理
- **在庫警告**: 最小在庫数を下回った際の自動警告
- **在庫調整**: 実在庫との差異調整機能

### **3. 検索・フィルタリング**
```python
def apply_filters(self):
    """リアルタイム複数条件フィルタリング"""
    search_text = self.search_input.text()
    category = self.category_combo.currentText()
    status = self.stock_status_combo.currentText()
    
    # チェーン方式でフィルタリング実行
    if search_text:
        self.product_table.filter_by_text(search_text)
    if category != "すべて":
        self.product_table.filter_by_category(category)
    if status != "すべて":
        self.product_table.filter_by_stock_status(status)
```

### **4. 履歴・統計機能**
- **操作履歴**: 購入・使用・調整の全記録を時系列表示
- **統計情報**: 商品別の購入回数、使用頻度、総購入量・使用量
- **HTML表示**: 見やすいテーブル形式での履歴表示
- **期間絞り込み**: 日付範囲指定での履歴検索

## 💻 技術的なこだわり

### **型安全性の重視**
```python
from typing import Optional, Dict, Any, List

def get_products_as_objects(self) -> List[Product]:
    """戻り値の型を明確に定義し、IDE支援を活用"""
    try:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM products ORDER BY name")
            rows = cursor.fetchall()
        
        return create_product_list_from_rows(rows)
    except sqlite3.Error as e:
        print(f"取得エラー: {e}")
        return []
```

### **包括的エラーハンドリング**
```python
def add_product(self, product) -> bool:
    try:
        with self._get_connection() as conn:
            cursor = conn.execute("""INSERT INTO products VALUES ...""")
            product.product_id = cursor.lastrowid
            conn.commit()
            return True
            
    except sqlite3.IntegrityError as e:
        print(f"整合性エラー: {e}")
        return False
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False
```

### **ファクトリーパターンの活用**
```python
def create_product_list_from_rows(rows) -> List[Product]:
    """データベース行からオブジェクトへの変換を抽象化"""
    return [Product(data=row) for row in rows]

class Product:
    def __init__(self, data=None, **kwargs):
        """柔軟な初期化パターン"""
        if data is not None:
            self._init_from_data(data)  # DB行から初期化
        else:
            self._init_from_kwargs(**kwargs)  # 直接指定で初期化
```

### **設定管理の外部化**
```python
# utils/config.py - 設定の一元管理
APP_NAME = "在庫管理アプリ"
DEFAULT_CATEGORIES = ["日用品", "洗剤", "食品", "調味料", "飲料", "その他"]
DEFAULT_STORAGE_LOCATIONS = ["キッチン", "冷蔵庫", "冷凍庫", "トイレ", "お風呂", "その他"]
STOCK_COLORS = {
    'out_of_stock': '#ffebee',
    'low_stock': '#fff8e1',
    'normal': '#ffffff'
}
```

## 🚀 パフォーマンス最適化

### **データベースインデックス設計**
```sql
-- 検索性能向上のための戦略的インデックス
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_stock_status ON products(current_stock, min_stock);
CREATE INDEX idx_stock_history_product_id ON stock_history(product_id);
CREATE INDEX idx_stock_history_created_at ON stock_history(created_at);
```

### **UI更新の効率化**
```python
def refresh_table(self):
    """大量データでも高速な表示更新"""
    # ソート機能を一時無効化（描画処理高速化）
    self.setSortingEnabled(False)
    
    # 行数を一度に設定
    self.setRowCount(len(self.filtered_data))
    
    # バッチ処理で全行更新
    for row, product in enumerate(self.filtered_data):
        self.add_product_to_table(row, product)
    
    # ソート機能を再有効化
    self.setSortingEnabled(True)
```

### **メモリ効率の考慮**
- **接続管理**: `with`文によるリソース自動解放
- **データキャッシュ**: フィルタリング用の元データ保持
- **遅延ローディング**: 必要時のみデータ取得

## 📱 実用性・完成度

### **実際の使用を想定した機能設計**
- **買い物前チェック**: 在庫切れ・在庫少の商品を一覧で確認
- **商品使用時記録**: ワンクリックでの在庫減少操作
- **定期棚卸し**: 実在庫と帳簿在庫の照合・調整
- **購入計画**: 過去の使用パターンから次回購入タイミング予測

### **エンタープライズレベルの品質管理**
- **トランザクション処理**: ACID特性を保証した更新処理
- **外部キー制約**: データの参照整合性を強制
- **入力値検証**: ユーザー入力の妥当性チェック
- **例外処理**: 全レイヤーでの適切なエラーハンドリング

### **拡張性を考慮した設計**
- **プラグイン対応**: 新機能追加が容易な構造
- **国際化対応**: 文字列の外部化
- **テーマ対応**: UI色設定の分離

## 🎯 学習・成長のポイント

### **問題解決力**
実生活の具体的課題から要件を整理し、技術的解決策を独力で設計・実装

### **技術選択力**
- **PySide6選択理由**: 
  - クロスプラットフォーム対応
  - 豊富なウィジェット
  - Pythonとの親和性
- **SQLite選択理由**: 
  - 軽量でセットアップ不要
  - ファイルベースで持ち運び容易
  - 標準ライブラリで追加依存なし

### **アーキテクチャ設計力**
- **MVCパターン**: 責任分離による保守性の確保
- **オブジェクト指向**: 拡張性と再利用性を重視した設計
- **データベース正規化**: データの整合性と効率性の両立

### **ユーザー体験への配慮**
- **直感的UI**: 初見でも操作方法が分かるインターフェース
- **視覚的フィードバック**: 色と形による状況の即座な把握
- **効率的操作**: キーボードショートカットによる高速操作

## 🔧 セットアップ・実行方法

### **動作環境**
- **Python**: 3.8以上
- **OS**: Windows / macOS / Linux
- **メモリ**: 512MB以上
- **ストレージ**: 50MB以上

### **インストール手順**
```bash
# 1. リポジトリクローン
git clone https://github.com/katotaku879/inventory-app.git
cd inventory-app

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. アプリケーション実行
python main.py
```

### **初回起動時の自動セットアップ**
1. SQLiteデータベースファイル自動作成
2. テーブル構造の自動構築
3. サンプルデータの投入
4. 設定ファイルの初期化

すぐに動作確認が可能で、追加設定は不要です。

## 📈 今後の拡張可能性

現在は個人利用に最適化されていますが、以下のような展開が可能：

### **技術的拡張**
- **Web版展開**: Django/Flask + React による Web アプリ化
- **モバイル版**: React Native/Flutter によるスマートフォン対応
- **API化**: REST API / GraphQL による外部連携
- **クラウド同期**: AWS/Firebase/Google Cloud との連携

### **機能的拡張**
- **マルチユーザー**: 認証機能と権限管理
- **通知機能**: メール/プッシュ通知による期限切れアラート
- **分析機能**: 購入パターン分析とレコメンド
- **外部連携**: ECサイトAPI連携による価格比較

## 💡 このプロジェクトで身につけたスキル

### **技術スキル**
- ✅ **Python モダン開発**: 型ヒント、dataclass、コンテキストマネージャ
- ✅ **GUI開発**: PySide6によるデスクトップアプリ開発
- ✅ **データベース**: SQLite設計・最適化・運用
- ✅ **アーキテクチャ**: MVC設計パターンの実装
- ✅ **オブジェクト指向**: 継承・ポリモーフィズム・カプセル化
- ✅ **エラーハンドリング**: 包括的な例外処理設計

### **設計・分析スキル**
- ✅ **要件定義**: 実体験からの課題抽出と要件整理
- ✅ **UI/UX設計**: ユーザビリティを重視したインターフェース設計
- ✅ **データモデリング**: 正規化と効率性を両立したDB設計
- ✅ **パフォーマンス**: インデックス設計とクエリ最適化

### **AI活用開発の実践**
- **問題解決力**: AI支援により従来より高速な学習と実装を実現
- **品質向上**: AIによるコードレビューと最適化提案の活用
- **技術習得**: 新技術への適応能力とAIツールとの協働スキル
- **効率的開発**: 定型作業の自動化と創造的作業への集中

## 🎖️ 特に評価していただきたいポイント

### **1. 実用性への徹底的なこだわり**
単なる学習目的ではなく、**実際に日常使用している実用アプリ**として開発。
リアルな使用体験に基づく機能設計と継続的な改善。

### **2. エンタープライズレベルの品質**
- トランザクション処理による整合性保証
- 包括的エラーハンドリング
- 型安全性を重視したモダンなPythonコード
- 拡張性を考慮したアーキテクチャ設計

### **3. ユーザー体験へのこだわり**
- 直感的で分かりやすいUI設計
- 視覚的フィードバックによる情報の即座な把握
- 効率的な操作を実現するキーボードショートカット
- リアルタイム検索による快適な操作感

### **4. 技術的な成長意欲**
- 新しい技術スタック（PySide6）への挑戦
- モダンなPython開発技法の習得と実践
- パフォーマンス最適化への取り組み
- 保守性を重視したコード品質への意識

---

## 📞 連絡先
- **GitHub**: https://github.com/katotaku879
- **プロジェクト**: https://github.com/katotaku879/inventory-app

---

**このアプリケーションは、実際の生活課題を技術で解決したいという想いから生まれました。単なる学習プロジェクトではなく、日常的に使用している実用アプリケーションです。実体験に基づく要件定義から、技術選択、設計、実装まで、一貫して品質にこだわって開発しました。**