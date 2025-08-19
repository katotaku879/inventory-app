#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース管理モジュール - Phase 4 実機能実装版（完全修正版）
SQLiteデータベースの作成・操作を担当
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# パス設定を修正
sys.path.append(str(Path(__file__).parent))

try:
    from stock_history import StockHistory, create_history_list_from_rows
    from product import Product, create_product_list_from_rows
except ImportError:
    # 相対インポートを試行
    try:
        from .stock_history import StockHistory, create_history_list_from_rows
        from .product import Product, create_product_list_from_rows
    except ImportError as e:
        print(f"インポートエラー: {e}")
        print("models/stock_history.py と models/product.py ファイルが存在することを確認してください")
        sys.exit(1)

def create_database():
    """データベースとテーブルを作成"""
    
    # schema.sqlファイルを読み込み
    schema_path = Path(__file__).parent.parent / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ エラー: schema.sqlファイルが見つかりません: {schema_path}")
        return False
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # データベースに接続してスキーマを実行
        conn = sqlite3.connect('inventory.db')
        conn.executescript(schema_sql)
        conn.close()
        
        print("✅ データベースが作成されました")
        return True
        
    except Exception as e:
        print(f"❌ データベース作成エラー: {e}")
        return False

class DatabaseManager:
    """
    データベース操作を管理するクラス - Phase 4 実機能実装版
    """
    
    def __init__(self, db_path: str = 'inventory.db'):
        """
        データベースマネージャーを初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        print(f"データベースマネージャー初期化: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        データベース接続を取得（内部用メソッド）
        
        Returns:
            sqlite3.Connection: データベース接続オブジェクト
        """
        try:
            # データベースに接続
            connection = sqlite3.connect(self.db_path)
            
            # 外部キー制約を有効化（重要！）
            connection.execute("PRAGMA foreign_keys = ON")
            
            # Row factory設定（辞書形式でデータ取得）
            connection.row_factory = sqlite3.Row
            
            return connection

        except sqlite3.Error as e:
            print(f"データベース接続エラー: {e}")
            raise

    # === 商品CRUD操作（Phase 4 新実装） ===
    
    def add_product(self, product) -> bool:
        """
        商品をデータベースに追加
        
        Args:
            product: 追加する商品オブジェクト
            
        Returns:
            bool: 成功時True
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO products (
                        name, brand, size, category, current_stock, min_stock,
                        purchase_location, price, storage_location, expiry_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.name,
                    product.brand,
                    product.size,
                    product.category,
                    product.current_stock,
                    product.min_stock,
                    product.purchase_location,
                    product.price,
                    product.storage_location,
                    product.expiry_date
                ))
                
                # 新しく追加された商品のIDを取得
                product.product_id = cursor.lastrowid
                
                # トランザクションをコミット
                conn.commit()
                
                print(f"✅ 商品追加成功: {product.name} (ID: {product.product_id})")
                return True
                
        except sqlite3.IntegrityError as e:
            print(f"❌ 商品追加失敗（整合性エラー）: {e}")
            return False
        except sqlite3.Error as e:
            print(f"❌ 商品追加失敗（データベースエラー）: {e}")
            return False
        except Exception as e:
            print(f"❌ 商品追加失敗（予期しないエラー）: {e}")
            return False
    
    def update_product(self, product) -> bool:
        """
        商品情報をデータベースで更新
        
        Args:
            product: 更新する商品オブジェクト
            
        Returns:
            bool: 成功時True
        """
        if not hasattr(product, 'product_id') or not product.product_id:
            print("❌ 商品更新失敗: 商品IDが設定されていません")
            return False
        
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    UPDATE products SET
                        name = ?, brand = ?, size = ?, category = ?,
                        current_stock = ?, min_stock = ?, purchase_location = ?,
                        price = ?, storage_location = ?, expiry_date = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    product.name,
                    product.brand,
                    product.size,
                    product.category,
                    product.current_stock,
                    product.min_stock,
                    product.purchase_location,
                    product.price,
                    product.storage_location,
                    product.expiry_date,
                    product.product_id
                ))
                
                # 更新された行数をチェック
                if cursor.rowcount == 0:
                    print(f"❌ 商品更新失敗: ID {product.product_id} の商品が見つかりません")
                    return False
                
                # トランザクションをコミット
                conn.commit()
                
                print(f"✅ 商品更新成功: {product.name} (ID: {product.product_id})")
                return True
                
        except sqlite3.IntegrityError as e:
            print(f"❌ 商品更新失敗（整合性エラー）: {e}")
            return False
        except sqlite3.Error as e:
            print(f"❌ 商品更新失敗（データベースエラー）: {e}")
            return False
        except Exception as e:
            print(f"❌ 商品更新失敗（予期しないエラー）: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """
        商品をデータベースから削除（関連する在庫履歴も削除）
        
        Args:
            product_id: 削除する商品のID
            
        Returns:
            bool: 成功時True
        """
        try:
            with self._get_connection() as conn:
                # まず商品が存在するかチェック
                check_cursor = conn.execute("SELECT name FROM products WHERE id = ?", (product_id,))
                product_row = check_cursor.fetchone()
                
                if not product_row:
                    print(f"❌ 商品削除失敗: ID {product_id} の商品が見つかりません")
                    return False
                
                product_name = product_row['name']
                
                # 関連する在庫履歴を削除
                history_cursor = conn.execute("DELETE FROM stock_history WHERE product_id = ?", (product_id,))
                deleted_history_count = history_cursor.rowcount
                
                # 商品を削除
                product_cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
                
                # トランザクションをコミット
                conn.commit()
                
                print(f"✅ 商品削除成功: {product_name} (ID: {product_id})")
                if deleted_history_count > 0:
                    print(f"   関連履歴も削除: {deleted_history_count}件")
                return True
                
        except sqlite3.Error as e:
            print(f"❌ 商品削除失敗（データベースエラー）: {e}")
            return False
        except Exception as e:
            print(f"❌ 商品削除失敗（予期しないエラー）: {e}")
            return False
    
    def product_exists(self, product_id: int) -> bool:
        """
        商品が存在するかチェック
        
        Args:
            product_id: チェックする商品ID
            
        Returns:
            bool: 存在する場合True
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,))
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    # === 在庫管理操作（Phase 4 新実装） ===
    
    def update_stock_and_add_history(self, stock_data: dict) -> bool:
        """
        在庫を更新し、履歴を記録（トランザクション処理）
        
        Args:
            stock_data: 在庫変更データ
                - product_id: 商品ID
                - operation_type: 操作種別 ('purchase', 'use', 'adjust')
                - quantity_change: 数量変化
                - stock_after: 操作後在庫数
                - memo: メモ（任意）
                
        Returns:
            bool: 成功時True
        """
        try:
            with self._get_connection() as conn:
                # 商品が存在するかチェック
                check_cursor = conn.execute(
                    "SELECT name, current_stock FROM products WHERE id = ?", 
                    (stock_data['product_id'],)
                )
                product_row = check_cursor.fetchone()
                
                if not product_row:
                    print(f"❌ 在庫更新失敗: ID {stock_data['product_id']} の商品が見つかりません")
                    return False
                
                product_name = product_row['name']
                current_stock = product_row['current_stock']
                
                # 在庫数の妥当性チェック
                new_stock = stock_data['stock_after']
                if new_stock < 0:
                    print(f"❌ 在庫更新失敗: 在庫数が負の値になります ({new_stock})")
                    return False
                
                # 商品の在庫数を更新
                update_cursor = conn.execute("""
                    UPDATE products 
                    SET current_stock = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_stock, stock_data['product_id']))
                
                if update_cursor.rowcount == 0:
                    print(f"❌ 在庫更新失敗: 商品の更新に失敗しました")
                    return False
                
                # 在庫履歴を記録
                history_cursor = conn.execute("""
                    INSERT INTO stock_history (
                        product_id, operation_type, quantity_change, 
                        stock_after, memo
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    stock_data['product_id'],
                    stock_data['operation_type'],
                    stock_data['quantity_change'],
                    stock_data['stock_after'],
                    stock_data.get('memo')
                ))
                
                # トランザクションをコミット
                conn.commit()
                
                # 成功ログ
                operation_names = {
                    'purchase': '購入',
                    'use': '使用', 
                    'adjust': '調整'
                }
                operation_name = operation_names.get(stock_data['operation_type'], '不明')
                change = stock_data['quantity_change']
                
                print(f"✅ 在庫更新成功: {product_name}")
                print(f"   操作: {operation_name} ({change:+d}個)")
                print(f"   在庫: {current_stock}個 → {new_stock}個")
                print(f"   履歴ID: {history_cursor.lastrowid}")
                
                return True
                
        except sqlite3.IntegrityError as e:
            print(f"❌ 在庫更新失敗（整合性エラー）: {e}")
            return False
        except sqlite3.Error as e:
            print(f"❌ 在庫更新失敗（データベースエラー）: {e}")
            return False
        except Exception as e:
            print(f"❌ 在庫更新失敗（予期しないエラー）: {e}")
            return False
    
    def get_stock_history(self, product_id: int = None, limit: int = 100) -> List:
        """
        在庫履歴を取得
        
        Args:
            product_id: 商品ID（指定時は該当商品のみ）
            limit: 取得件数の上限
            
        Returns:
            List: 在庫履歴のリスト
        """
        try:
            with self._get_connection() as conn:
                if product_id:
                    cursor = conn.execute("""
                        SELECT h.*, p.name as product_name
                        FROM stock_history h
                        JOIN products p ON h.product_id = p.id
                        WHERE h.product_id = ?
                        ORDER BY h.created_at DESC
                        LIMIT ?
                    """, (product_id, limit))
                else:
                    cursor = conn.execute("""
                        SELECT h.*, p.name as product_name
                        FROM stock_history h
                        JOIN products p ON h.product_id = p.id
                        ORDER BY h.created_at DESC
                        LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                
                # StockHistoryオブジェクトのリストに変換を試行
                try:
                    histories = create_history_list_from_rows(rows)
                except:
                    # 変換に失敗した場合は、そのまま返す
                    histories = rows
                
                print(f"✅ 履歴取得成功: {len(histories)}件")
                return histories
                
        except sqlite3.Error as e:
            print(f"❌ 履歴取得失敗: {e}")
            return []
        except Exception as e:
            print(f"❌ 履歴取得失敗（予期しないエラー）: {e}")
            return []
    
    def get_stock_statistics(self, product_id: int) -> Dict[str, Any]:
        """
        商品の在庫統計情報を取得
        
        Args:
            product_id: 商品ID
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        try:
            with self._get_connection() as conn:
                # 基本統計
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_operations,
                        SUM(CASE WHEN operation_type = 'purchase' THEN 1 ELSE 0 END) as purchase_count,
                        SUM(CASE WHEN operation_type = 'use' THEN 1 ELSE 0 END) as use_count,
                        SUM(CASE WHEN operation_type = 'adjust' THEN 1 ELSE 0 END) as adjust_count,
                        SUM(CASE WHEN operation_type = 'purchase' THEN quantity_change ELSE 0 END) as total_purchased,
                        SUM(CASE WHEN operation_type = 'use' THEN ABS(quantity_change) ELSE 0 END) as total_used,
                        MIN(created_at) as first_operation,
                        MAX(created_at) as last_operation
                    FROM stock_history 
                    WHERE product_id = ?
                """, (product_id,))
                
                stats = cursor.fetchone()
                
                if stats and stats['total_operations'] > 0:
                    return {
                        'total_operations': stats['total_operations'],
                        'purchase_count': stats['purchase_count'],
                        'use_count': stats['use_count'],
                        'adjust_count': stats['adjust_count'],
                        'total_purchased': stats['total_purchased'] or 0,
                        'total_used': stats['total_used'] or 0,
                        'first_operation': stats['first_operation'],
                        'last_operation': stats['last_operation']
                    }
                else:
                    return {
                        'total_operations': 0,
                        'purchase_count': 0,
                        'use_count': 0,
                        'adjust_count': 0,
                        'total_purchased': 0,
                        'total_used': 0,
                        'first_operation': None,
                        'last_operation': None
                    }
                    
        except sqlite3.Error as e:
            print(f"❌ 統計取得失敗: {e}")
            return {}
    
    # === 既存メソッド（変更なし） ===
    
    def get_all_products(self) -> List[sqlite3.Row]:
        """
        すべての商品を取得
        
        Returns:
            List[sqlite3.Row]: 商品データのリスト
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, name, brand, size, category, 
                           current_stock, min_stock, purchase_location, 
                           price, storage_location, expiry_date,
                           created_at, updated_at                  
                    FROM products 
                    ORDER BY name
                """)
                products = cursor.fetchall()
                
            print(f"商品取得完了: {len(products)}件")
            return products
            
        except sqlite3.Error as e:
            print(f"商品取得エラー: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[sqlite3.Row]:
        """
        IDで商品を取得
        
        Args:
            product_id: 商品ID
            
        Returns:
            Optional[sqlite3.Row]: 商品データ（見つからない場合はNone）
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, name, brand, size, category, 
                           current_stock, min_stock, purchase_location, 
                           price, storage_location, expiry_date,
                           created_at, updated_at
                    FROM products 
                    WHERE id = ?
                """, (product_id,))
                product = cursor.fetchone()
                
            if product:
                print(f"商品取得: {product['name']}")
            else:
                print(f"商品が見つかりません: ID={product_id}")
                
            return product

        except sqlite3.Error as e:
            print(f"商品取得エラー: {e}")
            return None  

    def get_products_as_objects(self) -> list:
        """
        すべての商品をProductオブジェクトのリストで取得
        
        Returns:
            list: 商品オブジェクトのリスト
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, name, brand, size, category, 
                           current_stock, min_stock, purchase_location, 
                           price, storage_location, expiry_date,
                           created_at, updated_at
                    FROM products 
                    ORDER BY name
                """)
                rows = cursor.fetchall()
                
            try:
                products = create_product_list_from_rows(rows)
            except:
                # 変換に失敗した場合は、基本的なオブジェクトを作成
                products = []
                for row in rows:
                    try:
                        products.append(Product(data=row))
                    except:
                        # 最終手段として辞書から直接作成
                        product_dict = dict(row)
                        product_dict['product_id'] = product_dict.get('id')
                        products.append(Product(**product_dict))
            
            print(f"商品オブジェクト取得完了: {len(products)}件")
            return products
            
        except sqlite3.Error as e:
            print(f"商品オブジェクト取得エラー: {e}")
            return []
    
    def get_product_object_by_id(self, product_id: int) -> Optional:
        """
        IDで商品をProductオブジェクトとして取得
        
        Args:
            product_id: 商品ID
            
        Returns:
            Optional: 商品オブジェクト（見つからない場合はNone）
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, name, brand, size, category, 
                           current_stock, min_stock, purchase_location, 
                           price, storage_location, expiry_date,
                           created_at, updated_at
                    FROM products 
                    WHERE id = ?
                """, (product_id,))
                row = cursor.fetchone()
                
            if row:
                try:
                    product = Product(data=row)
                except:
                    # 変換に失敗した場合は、辞書から直接作成
                    product_dict = dict(row)
                    product_dict['product_id'] = product_dict.get('id')
                    product = Product(**product_dict)
                
                print(f"商品オブジェクト取得: {product.name}")
                return product
            else:
                print(f"商品が見つかりません: ID={product_id}")
                return None
                
        except sqlite3.Error as e:
            print(f"商品オブジェクト取得エラー: {e}")
            return None

# テスト実行（このファイルが直接実行された場合）
if __name__ == "__main__":
    print("=== Phase 4 データベース管理システムのテスト ===")
    
    # 1. データベース作成
    print("\n1. データベース作成")
    create_database()
    
    # 2. データベースマネージャー初期化
    print("\n2. データベースマネージャー初期化")
    db = DatabaseManager()
    
    print("\n=== テスト完了 ===")