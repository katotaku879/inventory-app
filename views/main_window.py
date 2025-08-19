#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メインウィンドウ実装 - 修正版
インポートパスを修正
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import json
from pathlib import Path

# PySide6のUI部品をインポート
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, 
    QComboBox, QLabel, QToolBar, QStatusBar, QMessageBox,
    QHeaderView, QAbstractItemView, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit, QDialogButtonBox,
    QSplitter, QTextBrowser
)
from PySide6.QtCore import Qt, QTimer, Signal, QDate, QSettings
from PySide6.QtGui import QAction, QIcon, QColor, QFont, QKeySequence

# 正しいインポートパス
sys.path.append(str(Path(__file__).parent.parent))
from models.stock_history import StockHistory, create_history_list_from_rows
from models.product import Product, create_product_list_from_rows
from models.database import DatabaseManager

def create_database():
    """データベースとテーブルを作成"""
    
    # schema.sqlファイルを読み込み
    schema_path = Path(__file__).parent.parent / "schema.sql"
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # データベースに接続してスキーマを実行
    conn = sqlite3.connect('inventory.db')
    conn.executescript(schema_sql)
    conn.close()
    
    print("データベースが作成されました")

class HistoryDialog(QDialog):
    """
    在庫履歴表示ダイアログ
    """
    
    def __init__(self, product_id=None, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """
        履歴ダイアログのUI作成
        """
        self.setWindowTitle("在庫履歴")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 履歴表示用テキストブラウザ
        self.history_browser = QTextBrowser()
        self.history_browser.setFont(QFont("Consolas", 10))
        layout.addWidget(self.history_browser)
        
        # 閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def load_history(self):
        """
        履歴データを読み込み
        """
        try:
            # 仮の履歴データ（実際はデータベースから取得）
            history_text = """
<h3>📦 在庫履歴</h3>
<table border='1' style='border-collapse: collapse; width: 100%;'>
<tr style='background-color: #f0f0f0;'>
    <th>日時</th><th>操作</th><th>変更</th><th>残り</th><th>メモ</th>
</tr>
<tr>
    <td>2024-06-04 16:00</td><td>購入</td><td>+5個</td><td>5個</td><td>初回購入</td>
</tr>
<tr>
    <td>2024-06-05 09:30</td><td>使用</td><td>-2個</td><td>3個</td><td>朝の使用</td>
</tr>
<tr>
    <td>2024-06-06 14:20</td><td>使用</td><td>-1個</td><td>2個</td><td>お客様用</td>
</tr>
</table>
<br>
<p><strong>📊 統計情報:</strong></p>
<ul>
<li>総購入回数: 1回</li>
<li>総使用回数: 2回</li>
<li>平均使用間隔: 1.5日</li>
</ul>
            """
            self.history_browser.setHtml(history_text)
            
        except Exception as e:
            self.history_browser.setText(f"履歴の読み込みに失敗しました: {e}")

class SettingsDialog(QDialog):
    """
    設定ダイアログ
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """
        設定ダイアログのUI作成
        """
        self.setWindowTitle("設定")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # フォームレイアウト
        form_layout = QFormLayout()
        
        # 警告設定
        form_layout.addRow(QLabel("<b>警告設定</b>"))
        
        self.expire_warning_days = QSpinBox()
        self.expire_warning_days.setRange(1, 365)
        self.expire_warning_days.setValue(7)
        self.expire_warning_days.setSuffix(" 日前")
        form_layout.addRow("期限切れ警告:", self.expire_warning_days)
        
        self.low_stock_warning = QSpinBox()
        self.low_stock_warning.setRange(1, 100)
        self.low_stock_warning.setValue(3)
        self.low_stock_warning.setSuffix(" 個以下")
        form_layout.addRow("在庫少警告:", self.low_stock_warning)
        
        # 表示設定
        form_layout.addRow(QLabel("<b>表示設定</b>"))
        
        self.auto_refresh = QComboBox()
        self.auto_refresh.addItems(["無効", "1分", "5分", "10分"])
        form_layout.addRow("自動更新:", self.auto_refresh)
        
        self.show_toolbar = QComboBox()
        self.show_toolbar.addItems(["表示", "非表示"])
        form_layout.addRow("ツールバー:", self.show_toolbar)
        
        layout.addLayout(form_layout)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        """
        設定を読み込み
        """
        settings = QSettings("InventoryApp", "Settings")
        
        self.expire_warning_days.setValue(settings.value("expire_warning_days", 7, int))
        self.low_stock_warning.setValue(settings.value("low_stock_warning", 3, int))
        
        auto_refresh_index = settings.value("auto_refresh_index", 0, int)
        self.auto_refresh.setCurrentIndex(auto_refresh_index)
        
        show_toolbar_index = settings.value("show_toolbar", 0, int)
        self.show_toolbar.setCurrentIndex(show_toolbar_index)
    
    def save_settings(self):
        """
        設定を保存
        """
        settings = QSettings("InventoryApp", "Settings")
        
        settings.setValue("expire_warning_days", self.expire_warning_days.value())
        settings.setValue("low_stock_warning", self.low_stock_warning.value())
        settings.setValue("auto_refresh_index", self.auto_refresh.currentIndex())
        settings.setValue("show_toolbar", self.show_toolbar.currentIndex())
        
        QMessageBox.information(self, "設定", "設定を保存しました")
        self.accept()

class SimpleProductDialog(QDialog):
    """
    商品追加・編集ダイアログ
    """
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_edit_mode = product is not None
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_product_data()
    
    def setup_ui(self):
        """
        ダイアログのUI作成
        """
        # ウィンドウ設定
        title = "商品編集" if self.is_edit_mode else "新規商品追加"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 500)
        
        # メインレイアウト
        layout = QVBoxLayout(self)
        
        # フォームレイアウト
        form_layout = QFormLayout()
        
        # 商品名（必須）
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("商品名を入力してください（必須）")
        form_layout.addRow("商品名 *:", self.name_input)
        
        # ブランド
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("ブランド名を入力してください")
        form_layout.addRow("ブランド:", self.brand_input)
        
        # サイズ
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("例: 400ml, 12個入り")
        form_layout.addRow("サイズ:", self.size_input)
        
        # カテゴリ（必須）
        self.category_combo = QComboBox()
        self.category_combo.addItems(["日用品", "洗剤", "食品", "調味料", "飲料", "その他"])
        form_layout.addRow("カテゴリ *:", self.category_combo)
        
        # 現在在庫
        self.current_stock_spin = QSpinBox()
        self.current_stock_spin.setRange(0, 9999)
        self.current_stock_spin.setValue(0)
        form_layout.addRow("現在在庫:", self.current_stock_spin)
        
        # 最小在庫
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(1, 999)
        self.min_stock_spin.setValue(1)
        form_layout.addRow("最小在庫:", self.min_stock_spin)
        
        # 購入場所
        self.purchase_location_combo = QComboBox()
        self.purchase_location_combo.setEditable(True)
        self.purchase_location_combo.addItems([
            "スーパー", "ドラッグストア", "コンビニ", "ネット通販", 
            "ホームセンター", "ドン・キホーテ", "100円ショップ", "その他"
        ])
        form_layout.addRow("購入場所:", self.purchase_location_combo)
        
        # 価格
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.0, 99999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" 円")
        form_layout.addRow("価格:", self.price_spin)
        
        # 保存場所
        self.storage_location_combo = QComboBox()
        self.storage_location_combo.setEditable(True)
        self.storage_location_combo.addItems([
            "キッチン", "冷蔵庫", "冷凍庫", "クローゼット", 
            "お風呂", "トイレ", "洗面所", "その他"
        ])
        form_layout.addRow("保存場所:", self.storage_location_combo)
        
        # 消費期限
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDate(QDate.currentDate().addDays(30))
        self.expiry_date.setSpecialValueText("設定なし")
        form_layout.addRow("消費期限:", self.expiry_date)
        
        layout.addLayout(form_layout)
        
        # 説明文
        note_label = QLabel("* 印の項目は必須です")
        note_label.setStyleSheet("color: red; font-size: 10px;")
        layout.addWidget(note_label)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("保存" if self.is_edit_mode else "追加")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("キャンセル")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def load_product_data(self):
        """
        編集モード時に商品データを読み込み
        """
        if not self.product:
            return
        
        self.name_input.setText(self.product.name)
        self.brand_input.setText(self.product.brand or "")
        self.size_input.setText(self.product.size or "")
        
        # カテゴリ設定
        category_index = self.category_combo.findText(self.product.category)
        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)
        
        self.current_stock_spin.setValue(self.product.current_stock)
        self.min_stock_spin.setValue(self.product.min_stock)
        self.purchase_location_combo.setCurrentText(self.product.purchase_location or "")
        self.price_spin.setValue(self.product.price)
        self.storage_location_combo.setCurrentText(self.product.storage_location or "")
        
        # 消費期限設定
        if self.product.expiry_date:
            try:
                date_parts = self.product.expiry_date.split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    self.expiry_date.setDate(QDate(year, month, day))
            except ValueError:
                pass
    
    def get_product_data(self):
        """
        入力されたデータを辞書形式で取得
        """
        expiry_date_str = None
        if self.expiry_date.date() != QDate.currentDate().addDays(30):
            expiry_date_str = self.expiry_date.date().toString("yyyy-MM-dd")
        
        return {
            'name': self.name_input.text().strip(),
            'brand': self.brand_input.text().strip() or None,
            'size': self.size_input.text().strip() or None,
            'category': self.category_combo.currentText(),
            'current_stock': self.current_stock_spin.value(),
            'min_stock': self.min_stock_spin.value(),
            'purchase_location': self.purchase_location_combo.currentText().strip() or None,
            'price': self.price_spin.value(),
            'storage_location': self.storage_location_combo.currentText().strip() or None,
            'expiry_date': expiry_date_str
        }
    
    def validate_input(self):
        """
        入力データの検証
        """
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "入力エラー", "商品名は必須です。")
            self.name_input.setFocus()
            return False
        
        if self.min_stock_spin.value() <= 0:
            QMessageBox.warning(self, "入力エラー", "最小在庫は1以上である必要があります。")
            self.min_stock_spin.setFocus()
            return False
        
        return True
    
    def accept(self):
        """
        OKボタンが押された時の処理
        """
        if self.validate_input():
            super().accept()

class StockManagementDialog(QDialog):
    """
    在庫増減ダイアログ
    """
    
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.products = products
        self.setup_ui()
    
    def setup_ui(self):
        """
        ダイアログのUI作成
        """
        self.setWindowTitle("在庫増減")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # フォームレイアウト
        form_layout = QFormLayout()
        
        # 商品選択
        self.product_combo = QComboBox()
        for product in self.products:
            self.product_combo.addItem(
                f"{product.name} (現在: {product.current_stock}個)",
                product.product_id
            )
        form_layout.addRow("商品:", self.product_combo)
        
        # 操作種別
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["購入（増加）", "使用（減少）", "調整"])
        form_layout.addRow("操作:", self.operation_combo)
        
        # 変更数量
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999)
        self.quantity_spin.setValue(1)
        form_layout.addRow("数量:", self.quantity_spin)
        
        # メモ
        self.memo_input = QLineEdit()
        self.memo_input.setPlaceholderText("メモ（任意）")
        form_layout.addRow("メモ:", self.memo_input)
        
        layout.addLayout(form_layout)
        
        # 現在の在庫情報表示
        self.info_label = QLabel()
        self.info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        self.update_info_display()
        layout.addWidget(self.info_label)
        
        # シグナル接続
        self.product_combo.currentIndexChanged.connect(self.update_info_display)
        self.operation_combo.currentIndexChanged.connect(self.update_info_display)
        self.quantity_spin.valueChanged.connect(self.update_info_display)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("実行")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("キャンセル")
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def update_info_display(self):
        """
        在庫情報表示を更新
        """
        if not self.products:
            return
        
        # 選択された商品を取得
        current_index = self.product_combo.currentIndex()
        if current_index < 0:
            return
        
        product = self.products[current_index]
        operation = self.operation_combo.currentText()
        quantity = self.quantity_spin.value()
        
        # 操作後の在庫数を計算
        if operation == "購入（増加）":
            new_stock = product.current_stock + quantity
            operation_type = "purchase"
            change = f"+{quantity}"
        elif operation == "使用（減少）":
            new_stock = max(0, product.current_stock - quantity)
            operation_type = "use"
            change = f"-{quantity}"
        else:  # 調整
            new_stock = quantity
            operation_type = "adjust"
            change = f"→{quantity}"
        
        # 情報テキストを作成
        info_text = f"""
商品: {product.name}
現在在庫: {product.current_stock}個
変更: {change}個
操作後: {new_stock}個
最小在庫: {product.min_stock}個
        """.strip()
        
        # 警告表示
        if new_stock <= 0:
            info_text += "\n⚠️ 在庫切れになります"
        elif new_stock <= product.min_stock:
            info_text += "\n⚠️ 在庫が少なくなります"
        
        self.info_label.setText(info_text)
    
    def get_stock_data(self):
        """
        在庫変更データを取得
        """
        current_index = self.product_combo.currentIndex()
        product = self.products[current_index]
        operation = self.operation_combo.currentText()
        quantity = self.quantity_spin.value()
        
        # 操作種別と数量変化を決定
        if operation == "購入（増加）":
            operation_type = "purchase"
            quantity_change = quantity
            new_stock = product.current_stock + quantity
        elif operation == "使用（減少）":
            operation_type = "use"
            quantity_change = -quantity
            new_stock = max(0, product.current_stock - quantity)
        else:  # 調整
            operation_type = "adjust"
            quantity_change = quantity - product.current_stock
            new_stock = quantity
        
        return {
            'product_id': product.product_id,
            'operation_type': operation_type,
            'quantity_change': quantity_change,
            'stock_after': new_stock,
            'memo': self.memo_input.text().strip() or None
        }

class EnhancedProductTable(QTableWidget):
    """
    強化された商品一覧テーブルクラス（期限切れ警告追加）
    """
    # カスタムシグナル定義
    product_selected = Signal(int)
    product_double_clicked = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.original_data = []
        self.filtered_data = []
        self.setup_table()
        self.setup_connections()
        
    def setup_table(self):
        """
        テーブルの詳細設定
        """
        # 列数と列名を設定  
        self.columns = ["ID", "商品名", "ブランド", "カテゴリ", "現在在庫", "最小在庫", "状態", "価格", "保存場所", "消費期限", "⚠️"]
        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(self.columns)
        
        # テーブルの基本設定
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # 列幅の調整
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # ID列を非表示
        self.setColumnHidden(0, True)
        
        # ヘッダーのスタイル設定
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 4px;
                font-weight: bold;
            }
        """)
        
        # 行の高さを調整
        self.verticalHeader().setDefaultSectionSize(25)
        self.verticalHeader().setVisible(False)
        
        print("強化テーブル（期限切れ警告付き）の設定が完了しました")
    
    def setup_connections(self):
        """
        シグナル・スロット接続
        """
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
    def load_products(self, products):
        """
        商品データを読み込んでテーブルに表示
        """
        self.original_data = products
        self.filtered_data = products.copy()
        self.refresh_table()
        
    def refresh_table(self):
        """
        テーブル表示を更新
        """
        self.setSortingEnabled(False)
        self.setRowCount(len(self.filtered_data))
        
        for row, product in enumerate(self.filtered_data):
            self.add_product_to_table(row, product)
        
        self.setSortingEnabled(True)
        print(f"テーブル更新完了: {len(self.filtered_data)}件表示")
    
    def add_product_to_table(self, row, product):
        """
        商品データをテーブルの指定行に追加（期限切れ警告付き）
        """
        # 各列にデータを設定
        self.setItem(row, 0, QTableWidgetItem(str(product.product_id)))
        self.setItem(row, 1, QTableWidgetItem(product.name))
        self.setItem(row, 2, QTableWidgetItem(product.brand or ""))
        self.setItem(row, 3, QTableWidgetItem(product.category))
        
        # 在庫数
        stock_item = QTableWidgetItem()
        stock_item.setData(Qt.DisplayRole, product.current_stock)
        stock_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, stock_item)
        
        # 最小在庫数
        min_stock_item = QTableWidgetItem()
        min_stock_item.setData(Qt.DisplayRole, product.min_stock)
        min_stock_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 5, min_stock_item)
        
        # 在庫状況を日本語で表示
        status_text = self.get_status_text(product.get_stock_status())
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignCenter)
        
        # 在庫状況に応じてフォントスタイルを設定
        self.set_status_style(status_item, product.get_stock_status())
        
        self.setItem(row, 6, status_item)
        
        # 価格
        price_item = QTableWidgetItem(f"¥{product.price:.0f}")
        price_item.setData(Qt.UserRole, product.price)
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setItem(row, 7, price_item)
        
        self.setItem(row, 8, QTableWidgetItem(product.storage_location or ""))
        
        # 消費期限（新機能：期限切れ警告）
        expiry_item = QTableWidgetItem(product.expiry_date or "")
        if product.expiry_date and product.is_expired():
            expiry_item.setForeground(QColor(220, 20, 60))  # 赤色
            expiry_item.setFont(QFont("Arial", 9, QFont.Bold))
        self.setItem(row, 9, expiry_item)
        
        # 警告アイコン列（新機能）
        warning_item = QTableWidgetItem()
        warning_text = self.get_warning_text(product)
        warning_item.setText(warning_text)
        warning_item.setTextAlignment(Qt.AlignCenter)
        if warning_text:
            warning_item.setForeground(QColor(255, 140, 0))  # オレンジ色
            warning_item.setFont(QFont("Arial", 12, QFont.Bold))
        self.setItem(row, 10, warning_item)
        
        # 在庫状況に応じて行の背景色を設定
        self.set_row_color(row, product.get_stock_status(), product.is_expired())
    
    def get_status_text(self, status):
        """
        在庫状況コードを日本語に変換
        """
        status_map = {
            'out_of_stock': '在庫切れ',
            'low_stock': '在庫少',
            'normal': '正常'
        }
        return status_map.get(status, '不明')
    
    def get_warning_text(self, product):
        """
        警告アイコンテキストを取得（新機能）
        """
        warnings = []
        
        # 期限切れチェック
        if product.expiry_date and product.is_expired():
            warnings.append("🚨")
        
        # 在庫切れ・在庫少チェック
        status = product.get_stock_status()
        if status == 'out_of_stock':
            warnings.append("❌")
        elif status == 'low_stock':
            warnings.append("⚠️")
        
        return "".join(warnings)
    
    def set_status_style(self, item, status):
        """
        在庫状況に応じてアイテムのスタイルを設定
        """
        font = QFont()
        if status == 'out_of_stock':
            item.setForeground(QColor(220, 20, 60))  # 深い赤
            font.setBold(True)
        elif status == 'low_stock':
            item.setForeground(QColor(255, 140, 0))  # オレンジ
            font.setBold(True)
        else:
            item.setForeground(QColor(34, 139, 34))  # 緑
        
        item.setFont(font)
    
    def set_row_color(self, row, status, is_expired=False):
        """
        在庫状況と期限切れに応じて行の背景色を設定（新機能）
        """
        # 期限切れが最優先
        if is_expired:
            color = QColor(255, 200, 200)  # 濃い赤
        elif status == 'out_of_stock':
            color = QColor(255, 235, 238)  # 薄い赤
        elif status == 'low_stock':
            color = QColor(255, 248, 225)  # 薄い黄色
        else:
            color = QColor(248, 255, 248)  # 薄い緑
        
        # 行の各セルに背景色を適用
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(color)
    
    def on_selection_changed(self, selected, deselected):
        """
        選択変更時の処理
        """
        selected_indexes = self.selectionModel().selectedRows()
        if selected_indexes:
            row = selected_indexes[0].row()
            product_id = int(self.item(row, 0).text())
            self.product_selected.emit(product_id)
    
    def on_cell_double_clicked(self, row, column):
        """
        セルダブルクリック時の処理
        """
        product_id = int(self.item(row, 0).text())
        self.product_double_clicked.emit(product_id)
    
    def get_selected_product_id(self):
        """
        選択されている商品のIDを取得
        """
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            return int(self.item(row, 0).text())
        return None
    
    def filter_by_text(self, search_text):
        """
        テキストでフィルタリング
        """
        if not search_text:
            self.filtered_data = self.original_data.copy()
        else:
            search_text = search_text.lower()
            self.filtered_data = [
                product for product in self.original_data
                if search_text in product.name.lower() or 
                   search_text in (product.brand or "").lower()
            ]
        
        self.refresh_table()
    
    def filter_by_category(self, category):
        """
        カテゴリでフィルタリング
        """
        if category == "すべて":
            self.filtered_data = self.original_data.copy()
        else:
            self.filtered_data = [
                product for product in self.original_data
                if product.category == category
            ]
        
        self.refresh_table()
    
    def filter_by_stock_status(self, status_filter):
        """
        在庫状況でフィルタリング
        """
        if status_filter == "すべて":
            self.filtered_data = self.original_data.copy()
        else:
            status_map = {
                "在庫切れ": "out_of_stock",
                "在庫少": "low_stock", 
                "正常": "normal"
            }
            target_status = status_map.get(status_filter)
            if target_status:
                self.filtered_data = [
                    product for product in self.original_data
                    if product.get_stock_status() == target_status
                ]
        
        self.refresh_table()


class MainWindow(QMainWindow):
    """
    在庫管理アプリのメインウィンドウクラス - 全機能実装版
    """
    
    def __init__(self):
        """
        メインウィンドウを初期化
        """
        super().__init__()
        
        # データベースマネージャーを初期化
        self.db_manager = DatabaseManager()
        
        # 設定管理
        self.settings = QSettings("InventoryApp", "Settings")
        
        # 現在のフィルタ状態を保持
        self.current_search = ""
        self.current_category = "すべて"
        self.current_status = "すべて"
        
        # 自動更新タイマー
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.load_products)
        
        # UI要素を初期化
        self.setup_ui()
        
        # シグナル・スロット接続を設定
        self.setup_connections()
        
        # 設定を読み込み
        self.load_settings()
        
        # 初期データを読み込み
        self.load_products()
        
        # 期限切れ警告チェック
        self.check_expiry_warnings()
        
        print("全機能実装版メインウィンドウの初期化が完了しました")
    
    def setup_ui(self):
        """
        UI要素を作成・配置
        """
        # ウィンドウの基本設定
        self.setWindowTitle("在庫管理アプリ v0.1 - 全機能版")
        self.setGeometry(100, 100, 1300, 800)
        self.setMinimumSize(1000, 700)
        
        # メインウィジェットとレイアウトを作成
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # メニューバーを作成
        self.create_menubar()
        
        # ツールバーを作成
        self.create_toolbar()
        
        # 検索・フィルタエリアを作成
        search_layout = self.create_search_area()
        main_layout.addLayout(search_layout)
        
        # 強化された商品一覧テーブルを作成
        self.product_table = EnhancedProductTable()
        main_layout.addWidget(self.product_table)
        
        # ステータスバーを作成
        self.create_statusbar()
        
        print("全機能UI要素の作成が完了しました")
    
    def create_menubar(self):
        """
        メニューバーを作成（新機能）
        """
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")
        
        # エクスポート機能（仮実装）
        export_action = QAction("エクスポート(&E)", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 終了
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 表示メニュー
        view_menu = menubar.addMenu("表示(&V)")
        
        # 更新
        refresh_action = QAction("更新(&R)", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.load_products)
        view_menu.addAction(refresh_action)
        
        # 期限切れ警告チェック
        check_expiry_action = QAction("期限切れチェック(&C)", self)
        check_expiry_action.setShortcut(QKeySequence("Ctrl+W"))
        check_expiry_action.triggered.connect(self.check_expiry_warnings)
        view_menu.addAction(check_expiry_action)
        
        # ツールメニュー
        tools_menu = menubar.addMenu("ツール(&T)")
        
        # 履歴表示
        history_action = QAction("在庫履歴(&H)", self)
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
        
        tools_menu.addSeparator()
        
        # 設定
        settings_action = QAction("設定(&S)", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        # バージョン情報
        about_action = QAction("バージョン情報(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """
        ツールバーを作成（キーボードショートカット強化）
        """
        self.toolbar = QToolBar("メインツールバー")
        self.addToolBar(self.toolbar)
        
        # 新規追加ボタン
        self.add_action = QAction("➕ 新規追加", self)
        self.add_action.setStatusTip("新しい商品を追加します")
        self.add_action.setShortcut(QKeySequence("Ctrl+N"))
        self.toolbar.addAction(self.add_action)
        
        # 編集ボタン
        self.edit_action = QAction("✏️ 編集", self)
        self.edit_action.setStatusTip("選択した商品を編集します")
        self.edit_action.setShortcut(QKeySequence("Ctrl+E"))
        self.edit_action.setEnabled(False)
        self.toolbar.addAction(self.edit_action)
        
        # 削除ボタン
        self.delete_action = QAction("🗑️ 削除", self)
        self.delete_action.setStatusTip("選択した商品を削除します")
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.setEnabled(False)
        self.toolbar.addAction(self.delete_action)
        
        self.toolbar.addSeparator()
        
        # 在庫増減ボタン
        self.stock_action = QAction("📦 在庫増減", self)
        self.stock_action.setStatusTip("在庫数を増減します")
        self.stock_action.setShortcut(QKeySequence("Ctrl+S"))
        self.toolbar.addAction(self.stock_action)
        
        # 更新ボタン
        self.refresh_action = QAction("🔄 更新", self)
        self.refresh_action.setStatusTip("商品一覧を更新します")
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.toolbar.addAction(self.refresh_action)
        
        self.toolbar.addSeparator()
        
        # 履歴ボタン（新機能）
        self.history_action = QAction("📈 履歴", self)
        self.history_action.setStatusTip("在庫履歴を表示します")
        self.history_action.setShortcut(QKeySequence("Ctrl+H"))
        self.toolbar.addAction(self.history_action)
        
        # 設定ボタン（新機能）
        self.settings_action = QAction("⚙️ 設定", self)
        self.settings_action.setStatusTip("アプリケーション設定を変更します")
        self.settings_action.setShortcut(QKeySequence("Ctrl+,"))
        self.toolbar.addAction(self.settings_action)
        
        print("強化ツールバーの作成が完了しました")
    
    def create_search_area(self):
        """
        検索・フィルタエリアを作成（検索ショートカット追加）
        """
        search_layout = QHBoxLayout()
        
        # 検索テキストボックス
        search_layout.addWidget(QLabel("検索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("商品名またはブランド名で検索... (Ctrl+F)")
        self.search_input.setMinimumWidth(200)
        
        # 検索ショートカット（新機能）
        search_shortcut = QKeySequence("Ctrl+F")
        search_action = QAction(self)
        search_action.setShortcut(search_shortcut)
        search_action.triggered.connect(self.focus_search)
        self.addAction(search_action)
        
        search_layout.addWidget(self.search_input)
        
        # クリアボタン
        self.clear_search_btn = QPushButton("✖")
        self.clear_search_btn.setMaximumWidth(30)
        self.clear_search_btn.setToolTip("検索クリア")
        search_layout.addWidget(self.clear_search_btn)
        
        search_layout.addWidget(QLabel("  "))
        
        # カテゴリフィルタ
        search_layout.addWidget(QLabel("カテゴリ:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("すべて")
        self.category_combo.addItems(["日用品", "洗剤", "食品", "調味料", "飲料", "その他"])
        self.category_combo.setMinimumWidth(100)
        search_layout.addWidget(self.category_combo)
        
        # 在庫状況フィルタ
        search_layout.addWidget(QLabel("在庫状況:"))
        self.stock_status_combo = QComboBox()
        self.stock_status_combo.addItem("すべて")
        self.stock_status_combo.addItem("在庫切れ")
        self.stock_status_combo.addItem("在庫少")
        self.stock_status_combo.addItem("正常")
        self.stock_status_combo.setMinimumWidth(100)
        search_layout.addWidget(self.stock_status_combo)
        
        # 期限切れフィルタ（新機能）
        search_layout.addWidget(QLabel("期限:"))
        self.expiry_combo = QComboBox()
        self.expiry_combo.addItem("すべて")
        self.expiry_combo.addItem("期限切れ")
        self.expiry_combo.addItem("期限近し")
        self.expiry_combo.setMinimumWidth(100)
        search_layout.addWidget(self.expiry_combo)
        
        # スペーサーを追加
        search_layout.addStretch()
        
        # 選択情報表示
        self.selection_label = QLabel("商品を選択してください")
        self.selection_label.setStyleSheet("color: #666666; font-style: italic;")
        search_layout.addWidget(self.selection_label)
        
        print("強化検索エリアの作成が完了しました")
        return search_layout
    
    def create_statusbar(self):
        """
        ステータスバーを作成
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # ステータス表示用ラベル
        self.status_label = QLabel("準備完了")
        self.status_bar.addWidget(self.status_label)
        
        # フィルタ情報表示用ラベル
        self.filter_label = QLabel("")
        self.status_bar.addWidget(self.filter_label)
        
        # 警告表示用ラベル（新機能）
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_bar.addWidget(self.warning_label)
        
        # 商品数表示用ラベル
        self.count_label = QLabel("商品数: 0件")
        self.status_bar.addPermanentWidget(self.count_label)
        
        print("強化ステータスバーの作成が完了しました")
    
    def setup_connections(self):
        """
        シグナル・スロット接続を設定
        """
        # ツールバーのアクション接続
        self.add_action.triggered.connect(self.add_product)
        self.edit_action.triggered.connect(self.edit_product)
        self.delete_action.triggered.connect(self.delete_product)
        self.stock_action.triggered.connect(self.manage_stock)
        self.refresh_action.triggered.connect(self.load_products)
        self.history_action.triggered.connect(self.show_history)
        self.settings_action.triggered.connect(self.show_settings)
        
        # 検索・フィルタの接続
        self.search_input.textChanged.connect(self.apply_filters)
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.category_combo.currentTextChanged.connect(self.apply_filters)
        self.stock_status_combo.currentTextChanged.connect(self.apply_filters)
        self.expiry_combo.currentTextChanged.connect(self.apply_filters)
        
        # テーブルのシグナル接続
        self.product_table.product_selected.connect(self.on_product_selected)
        self.product_table.product_double_clicked.connect(self.on_product_double_clicked)
        
        print("全シグナル・スロット接続が完了しました")
    
    def load_settings(self):
        """
        設定を読み込み（新機能）
        """
        # ウィンドウサイズ・位置の復元
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # ツールバー表示設定
        show_toolbar = self.settings.value("show_toolbar", 0, int)
        self.toolbar.setVisible(show_toolbar == 0)
        
        # 自動更新設定
        auto_refresh_index = self.settings.value("auto_refresh_index", 0, int)
        intervals = [0, 60000, 300000, 600000]  # 無効, 1分, 5分, 10分
        if auto_refresh_index > 0 and auto_refresh_index < len(intervals):
            self.auto_refresh_timer.start(intervals[auto_refresh_index])
    
    def save_settings(self):
        """
        設定を保存（新機能）
        """
        # ウィンドウサイズ・位置を保存
        self.settings.setValue("window_geometry", self.saveGeometry())
    
    def closeEvent(self, event):
        """
        ウィンドウ閉じる時の処理（新機能）
        """
        self.save_settings()
        event.accept()
    
    # === 新機能メソッド ===
    
    def focus_search(self):
        """
        検索ボックスにフォーカス（Ctrl+F）
        """
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def check_expiry_warnings(self):
        """
        期限切れ警告チェック（新機能）
        """
        try:
            products = self.db_manager.get_products_as_objects()
            
            expired_products = []
            
            for product in products:
                if product.expiry_date:
                    if product.is_expired():
                        expired_products.append(product.name)
            
            # 警告メッセージを作成
            warnings = []
            if expired_products:
                warnings.append(f"期限切れ: {len(expired_products)}件")
            
            if warnings:
                self.warning_label.setText(" | ".join(warnings))
                
                # 警告ダイアログを表示
                warning_msg = "⚠️ 期限切れの商品があります:\n\n"
                warning_msg += "\n".join([f"• {name}" for name in expired_products])
                
                QMessageBox.warning(self, "期限切れ警告", warning_msg)
            else:
                self.warning_label.setText("")
                
        except Exception as e:
            print(f"期限切れチェックエラー: {e}")
    
    def show_settings(self):
        """
        設定ダイアログを表示（新機能）
        """
        dialog = SettingsDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            # 設定変更後の処理
            self.load_settings()
    
    def export_data(self):
        """
        データエクスポート（仮実装）
        """
        QMessageBox.information(
            self, "エクスポート", 
            "CSV形式でのデータエクスポート機能は今後実装予定です。"
        )
    
    def show_about(self):
        """
        バージョン情報を表示
        """
        QMessageBox.about(
            self, "バージョン情報",
            "<h3>在庫管理アプリ v0.1</h3>"
            "<p>全機能実装版</p>"
            "<p>開発者: mkykr</p>"
            "<p>PySide6ベースのデスクトップアプリケーション</p>"
        )
    
    def load_products(self):
        """
        データベースから商品データを読み込んでテーブルに表示
        """
        try:
            products = self.db_manager.get_products_as_objects()
            self.product_table.load_products(products)
            
            self.update_status_display(len(products), len(products))
            self.status_label.setText("商品データを読み込みました")
            
            print(f"全機能版 商品データ読み込み完了: {len(products)}件")
            
        except Exception as e:
            self.status_label.setText("データ読み込みエラー")
            QMessageBox.critical(self, "エラー", f"商品データの読み込みに失敗しました:\n{e}")
            print(f"商品データ読み込みエラー: {e}")
    
    def apply_filters(self):
        """
        すべてのフィルタを適用（期限フィルタ追加）
        """
        self.current_search = self.search_input.text()
        self.current_category = self.category_combo.currentText()
        self.current_status = self.stock_status_combo.currentText()
        current_expiry = self.expiry_combo.currentText()
        
        # 基本フィルタを適用
        if self.current_search:
            self.product_table.filter_by_text(self.current_search)
        
        if self.current_category != "すべて":
            self.product_table.filter_by_category(self.current_category)
        
        if self.current_status != "すべて":
            self.product_table.filter_by_stock_status(self.current_status)
        
        # 期限フィルタ（新機能）
        if current_expiry == "期限切れ":
            self.product_table.filtered_data = [
                product for product in self.product_table.filtered_data
                if product.expiry_date and product.is_expired()
            ]
            self.product_table.refresh_table()
        
        # すべてがデフォルトの場合は全件表示
        if (self.current_search == "" and 
            self.current_category == "すべて" and 
            self.current_status == "すべて" and
            current_expiry == "すべて"):
            self.product_table.filtered_data = self.product_table.original_data.copy()
            self.product_table.refresh_table()
        
        # 表示件数を更新
        total_count = len(self.product_table.original_data)
        filtered_count = len(self.product_table.filtered_data)
        self.update_status_display(filtered_count, total_count)
        
        # フィルタ情報を表示
        self.update_filter_display()
    
    def clear_search(self):
        """
        検索テキストをクリア
        """
        self.search_input.clear()
    
    def update_status_display(self, filtered_count, total_count):
        """
        ステータス表示を更新
        """
        if filtered_count == total_count:
            self.count_label.setText(f"商品数: {total_count}件")
        else:
            self.count_label.setText(f"表示: {filtered_count}件 / 全{total_count}件")
    
    def update_filter_display(self):
        """
        フィルタ情報表示を更新
        """
        filter_parts = []
        
        if self.current_search:
            filter_parts.append(f"検索: '{self.current_search}'")
        
        if self.current_category != "すべて":
            filter_parts.append(f"カテゴリ: {self.current_category}")
        
        if self.current_status != "すべて":
            filter_parts.append(f"状況: {self.current_status}")
        
        current_expiry = self.expiry_combo.currentText()
        if current_expiry != "すべて":
            filter_parts.append(f"期限: {current_expiry}")
        
        if filter_parts:
            self.filter_label.setText(" | ".join(filter_parts))
        else:
            self.filter_label.setText("")
    
    def on_product_selected(self, product_id):
        """
        商品が選択された時の処理
        """
        # ツールバーの編集・削除ボタンを有効化
        self.edit_action.setEnabled(True)
        self.delete_action.setEnabled(True)
        
        # 選択商品情報を表示
        try:
            product = self.db_manager.get_product_object_by_id(product_id)
            if product:
                self.selection_label.setText(f"選択: {product.name} (ID: {product_id})")
                self.status_label.setText(f"'{product.name}' を選択しました")
        except Exception as e:
            print(f"商品情報取得エラー: {e}")
    
    def on_product_double_clicked(self, product_id):
        """
        商品がダブルクリックされた時の処理
        """
        self.edit_product()
    
    # === 基本ボタン機能の実装 ===
    
    def add_product(self):
        """
        新しい商品を追加
        """
        dialog = SimpleProductDialog(parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            try:
                # 入力データを取得
                product_data = dialog.get_product_data()
                
                # 新しい商品オブジェクトを作成
                new_product = Product(**product_data)
                
                # データベースに実際に保存
                success = self.db_manager.add_product(new_product)
                
                if success:
                    # 成功メッセージ
                    QMessageBox.information(
                        self, "成功", 
                        f"商品 '{product_data['name']}' を追加しました。\n"
                        f"商品ID: {new_product.product_id}"
                    )
                    
                    # 商品一覧を更新
                    self.load_products()
                    self.status_label.setText(f"商品 '{product_data['name']}' を追加しました")
                    
                else:
                    # 失敗メッセージ
                    QMessageBox.critical(
                        self, "エラー", 
                        f"商品 '{product_data['name']}' の追加に失敗しました。\n"
                        "データベースエラーが発生しました。"
                    )
                    
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"商品の追加に失敗しました:\n{e}")
                print(f"商品追加エラー: {e}")

    def edit_product(self):
        """
        選択した商品を編集
        """
        product_id = self.product_table.get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "警告", "編集する商品を選択してください")
            return
        
        try:
            # 商品情報を取得
            product = self.db_manager.get_product_object_by_id(product_id)
            if not product:
                QMessageBox.warning(self, "エラー", "商品情報の取得に失敗しました")
                return
            
            # 編集前の在庫数を保存
            old_stock = product.current_stock
            
            # 編集ダイアログを表示
            dialog = SimpleProductDialog(product=product, parent=self)
            
            if dialog.exec() == QDialog.Accepted:
                # 編集されたデータを取得
                updated_data = dialog.get_product_data()
                
                # 商品オブジェクトを更新
                for key, value in updated_data.items():
                    setattr(product, key, value)
                
                # データベースを実際に更新
                success = self.db_manager.update_product(product)
                
                if success:
                    # 成功メッセージ
                    QMessageBox.information(
                        self, "成功", 
                        f"商品 '{updated_data['name']}' を更新しました。"
                    )
                    
                    # 商品一覧を更新
                    self.load_products()
                    self.status_label.setText(f"商品 '{updated_data['name']}' を更新しました")
                    
                else:
                    # 失敗メッセージ
                    QMessageBox.critical(
                        self, "エラー", 
                        f"商品 '{updated_data['name']}' の更新に失敗しました。\n"
                        "データベースエラーが発生しました。"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"商品の編集に失敗しました:\n{e}")
            print(f"商品編集エラー: {e}")

    def delete_product(self):
        """
        選択した商品を削除
        """
        product_id = self.product_table.get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "警告", "削除する商品を選択してください")
            return
        
        try:
            # 商品情報を取得
            product = self.db_manager.get_product_object_by_id(product_id)
            if not product:
                QMessageBox.warning(self, "エラー", "商品情報の取得に失敗しました")
                return
            
            # 削除確認ダイアログ
            confirmation_msg = f"商品 '{product.name}' を削除してもよろしいですか？\n\n"
            confirmation_msg += f"商品ID: {product_id}\n"
            confirmation_msg += f"現在在庫: {product.current_stock}個\n"
            confirmation_msg += "\nこの操作は取り消すことができません。"
            
            reply = QMessageBox.question(
                self, "削除確認",
                confirmation_msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # データベースから実際に削除
                success = self.db_manager.delete_product(product_id)
                
                if success:
                    # 成功メッセージ
                    QMessageBox.information(
                        self, "成功", 
                        f"商品 '{product.name}' を削除しました。"
                    )
                    
                    # 商品一覧を更新
                    self.load_products()
                    self.status_label.setText(f"商品 '{product.name}' を削除しました")
                    
                    # 選択状態をリセット
                    self.edit_action.setEnabled(False)
                    self.delete_action.setEnabled(False)
                    self.selection_label.setText("商品を選択してください")
                    
                else:
                    # 失敗メッセージ
                    QMessageBox.critical(
                        self, "エラー", 
                        f"商品 '{product.name}' の削除に失敗しました。\n"
                        "データベースエラーが発生しました。"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"商品の削除に失敗しました:\n{e}")
            print(f"商品削除エラー: {e}")

    def manage_stock(self):
        """
        在庫数を管理
        """
        try:
            # 全商品を取得
            products = self.db_manager.get_products_as_objects()
            
            if not products:
                QMessageBox.information(self, "情報", "管理する商品がありません")
                return
            
            # 在庫増減ダイアログを表示
            dialog = StockManagementDialog(products=products, parent=self)
            
            if dialog.exec() == QDialog.Accepted:
                # 在庫変更データを取得
                stock_data = dialog.get_stock_data()
                
                # データベースを実際に更新
                success = self.db_manager.update_stock_and_add_history(stock_data)
                
                if success:
                    # 成功メッセージ
                    product = next(p for p in products if p.product_id == stock_data['product_id'])
                    
                    operation_names = {
                        'purchase': '購入',
                        'use': '使用',
                        'adjust': '調整'
                    }
                    operation_name = operation_names.get(stock_data['operation_type'], '不明')
                    
                    success_msg = f"商品 '{product.name}' の在庫を更新しました。\n\n"
                    success_msg += f"操作種別: {operation_name}\n"
                    success_msg += f"変更数量: {stock_data['quantity_change']:+d}個\n"
                    success_msg += f"更新後在庫: {stock_data['stock_after']}個"
                    
                    if stock_data.get('memo'):
                        success_msg += f"\nメモ: {stock_data['memo']}"
                    
                    QMessageBox.information(self, "成功", success_msg)
                    
                    # 商品一覧を更新
                    self.load_products()
                    self.status_label.setText(f"'{product.name}' の在庫を更新しました")
                    
                else:
                    # 失敗メッセージ
                    QMessageBox.critical(
                        self, "エラー", 
                        "在庫の更新に失敗しました。\n"
                        "データベースエラーが発生しました。"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"在庫管理でエラーが発生しました:\n{e}")
            print(f"在庫管理エラー: {e}")

    def show_history(self):
        """
        在庫履歴を表示
        """
        selected_id = self.product_table.get_selected_product_id()
        
        # 履歴ダイアログを表示
        dialog = HistoryDialog(product_id=selected_id, parent=self)
        dialog.exec()


# テスト実行用の関数
def main():
    """
    メインウィンドウのテスト実行
    """
    app = QApplication(sys.argv)
    
    # アプリケーション情報を設定（設定管理用）
    app.setApplicationName("InventoryApp")
    app.setOrganizationName("mkykr")
    
    # メインウィンドウを作成・表示
    window = MainWindow()
    window.show()
    
    # アプリケーションを実行
    sys.exit(app.exec())


if __name__ == "__main__":
    main()