#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在庫履歴データモデル
在庫変更履歴を管理するクラスを定義
"""
# 日付や時刻を扱うためのモジュール
from datetime import datetime
#この記述は、Pythonの型ヒント（type hint）に使うためのimport文
from typing import Optional, Dict, Any

#在庫管理システムにおける「在庫履歴情報」を扱うためのPythonクラス
class StockHistory:
    """
    在庫履歴情報を管理するクラス
    """
    #StockHistoryクラスのインスタンスを柔軟に初期化するためのもの
    #data引数を使った初期化
    #**kwargsを使った個別指定での初期化 dataが渡されなかった場合は、キーワード引数で個別に属性を指定して初期化できます。
    def __init__(self, data=None, **kwargs):
        """
        在庫履歴オブジェクトを初期化
        
        Args:
            data: sqlite3.Rowオブジェクト または 辞書
            **kwargs: 個別指定での初期化
        """
        #「dataという変数に値がセットされている（Noneではない）場合」にだけ、特定の処理を実行するためのもの
        if data is not None:
            #StockHistoryクラスのインスタンスを、data（辞書やDBの行データ）から初期化するための内部メソッド（
            # _init_from_data）を呼び出しています。
            self._init_from_data(data)
        else:
            #StockHistoryクラスのインスタンスをキーワード引数（kwargs）から初期化するための内部メソッドを呼び出しています。
            self._init_from_kwargs(**kwargs)
    
    #StockHistoryクラスのインスタンスを、辞書やデータベースの行データ（data）から初期化するための内部用メソッド
    def _init_from_data(self, data):
        """
        データベースデータから初期化（内部用）
        """
        try:
            #「在庫履歴データ（data）」から履歴ID（history_id）を柔軟に取得してセットする
            # dataが辞書型の場合、キー 'id' または 'history_id' から履歴IDを取得します。
            # もしどちらのキーも存在しない場合は、Noneをセットします
            self.history_id = data['id'] if 'id' in data.keys() else (data['history_id'] if 'history_id' in data.keys() else None)
            # dataが辞書型の場合、キー 'product_id' から商品IDを取得します。
            # もしキー 'product_id' が存在しない場合は、Noneをセットします。
            # これにより、在庫履歴が関連する商品を識別するためのIDをセットします。
            self.product_id = data['product_id'] if 'product_id' in data.keys() else None
            # dataが辞書型の場合、キー 'operation_type' から操作種別を取得します。
            # もしキー 'operation_type' が存在しない場合は、空文字列をセットします。
            # これにより、在庫の操作種別を表す文字列をセットします。
            # 例えば、'purchase'（購入）、'use'（使用）、'adjust'（調整）などが考えられます。
            self.operation_type = data['operation_type'] if 'operation_type' in data.keys() else ''
            # dataが辞書型の場合、キー 'quantity_change' から数量変化を取得します。
            # もしキー 'quantity_change' が存在しない場合は、0をセットします。
            # これにより、在庫の数量変化を表す整数値をセットします。
            # 例えば、在庫が5個増えた場合は5、3個減った場合は-3などが考えられます。
            self.quantity_change = data['quantity_change'] if 'quantity_change' in data.keys() else 0
            # dataが辞書型の場合、キー 'stock_after' から操作後の在庫数を取得します。
            # もしキー 'stock_after' が存在しない場合は、0をセットします。
            # これにより、在庫操作後の残り在庫数を表す整数値をセットします。
            # 例えば、在庫操作後に残り10個の在庫がある場合は10、
            # 5個の在庫がある場合は5などが考えられます。
            self.stock_after = data['stock_after'] if 'stock_after' in data.keys() else 0
            # dataが辞書型の場合、キー 'memo' からメモを取得します。
            # もしキー 'memo' が存在しない場合は、空文字列をセットします。
            # これにより、在庫履歴に関連するメモやコメントを表す文字列をセットします。
            # 例えば、在庫操作の理由や詳細を記録するためのメモが考えられます。
            # 例えば、「初回購入」や「使用」などのメモが考えられます。
            self.memo = data['memo'] if 'memo' in data.keys() else ''
            # dataが辞書型の場合、キー 'created_at' から作成日時を取得します。
            # もしキー 'created_at' が存在しない場合は、Noneをセットします。
            # これにより、在庫履歴の作成日時を表す文字列をセットします。
            # 例えば、在庫履歴が作成された日時を記録するためのものです。
            self.created_at = data['created_at'] if 'created_at' in data.keys() else None
        # dataが辞書型以外の場合（例: sqlite3.Rowオブジェクトなど）に備えた処理
        # 辞書型以外のデータ構造からも在庫履歴を初期化できるようにしています。
        # 辞書型以外のデータ構造（例: sqlite3.Rowオブジェクトなど）から在庫履歴を初期化するための処理
        except (KeyError, TypeError):   # 辞書以外（例: sqlite3.Rowオブジェクト）
            # dataが辞書型でない場合、キー 'id' または 'history_id' から履歴IDを取得します。
            # もしどちらのキーも存在しない場合は、Noneをセットします
            self.history_id = data['id'] if 'id' in data.keys() else (data['history_id'] if 'history_id' in data.keys() else None)
            self.product_id = data['product_id'] if 'product_id' in data.keys() else None
            self.operation_type = data['operation_type'] if 'operation_type' in data.keys() else ''
            self.quantity_change = data['quantity_change'] if 'quantity_change' in data.keys() else 0
            self.stock_after = data['stock_after'] if 'stock_after' in data.keys() else 0
            self.memo = data['memo'] if 'memo' in data.keys() else ''
            self.created_at = data['created_at'] if 'created_at' in data.keys() else None
    
    #キーワード引数（名前付きの値）から在庫履歴オブジェクトの各属性をセットする内部メソッド
    #キーワード引数から在庫履歴の情報を柔軟にセットできる内部用メソッド
    def _init_from_kwargs(self, **kwargs):
        """
        個別指定から初期化（内部用）
        """
        #キーワード引数から「履歴ID（history_id）」をセットできます。
        # history_id=在庫履歴1件ごとに割り当てられる番号やIDです
        self.history_id = kwargs.get('history_id')
        #キーワード引数から「商品ID（product_id）」をセットできます。
        # product_id=在庫履歴が関連する商品を識別するための
        self.product_id = kwargs.get('product_id')
        #キーワード引数から「操作種別（operation_type）」をセットできます。
        # operation_type=在庫の操作種別を表す文字列です。
        self.operation_type = kwargs.get('operation_type', '')
        #キーワード引数から「数量変化（quantity_change）」をセットできます。
        # quantity_change=在庫の数量変化を表す整数値です。
        self.quantity_change = kwargs.get('quantity_change', 0)
        #キーワード引数から「操作後の在庫数（stock_after）」をセットできます。
        # stock_after=在庫操作後の残り在庫数を表す整数値です。
        self.stock_after = kwargs.get('stock_after', 0)
        #キーワード引数から「メモ（memo）」をセットできます。
        # memo=在庫履歴に関連するメモやコメントを表す文字列です。
        self.memo = kwargs.get('memo', '')
        
        #キーワード引数から「作成日時（created_at）」をセットできます。
        # created_at=在庫履歴の作成日時を表す文字列です
        # kwargs.get('created_at')で、キーワード引数から「created_at」を取得し、
        # もし存在しなければ、現在の日時をデフォルト値としてセットします。
        # これにより、在庫履歴の作成日時が指定されていない場合でも、
        # 現在の日時が自動的に設定されます。
        #明示的に作成日時が与えられていればそれを使う
        if 'created_at' in kwargs and kwargs['created_at']:
            #「在庫履歴」などのオブジェクトを初期化するときに、作成日時（created_at）を外部から指定してセットするための代入文
            self.created_at = kwargs['created_at']
        else:
            #、「作成日時（created_at）」を“今この瞬間の日時”で自動的にセットする処理
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #operation_type（操作種別）の値を、人間にわかりやすい日本語などの表示用文字列に変換して返すメソッド
    def get_operation_display(self) -> str:
        """
        操作種別の日本語表示を返す
        
        Returns:
            str: 操作種別の日本語
        """
        # operation_typeの値に応じて、日本語の操作種別を返す辞書を定義
        # operation_typeは、在庫の操作種別を表す文字列です。
        #「操作種別コード」と「表示用文字列」を対応させる辞書（マッピング）
        operation_map = {
            'purchase': '購入',
            'use': '使用',
            'adjust': '調整'
        }
        #操作種別コードに対応する表示名を返し、該当がなければ「不明」と返します。
        # self.operation_typeの値をキーとして、operation_mapから対応する表示名を取得します。
        return operation_map.get(self.operation_type, '不明')
    
    #在庫が増えた操作かどうかを判定して、True/Falseで返すメソッドです。
    #在庫が増えた場合はTrue、減った場合はFalseを返します。
    def is_increase(self) -> bool:
        """
        在庫増加操作かどうかを判定
        
        Returns:
            bool: 増加操作の場合True
        """
        # 在庫増加操作かどうかを判定
        # quantity_changeが正の値（0より大きい）なら増加操作
        # quantity_changeは在庫の数量変化を表す整数値です。
        # 在庫が増えた場合はTrue、減った場合はFalseを返します。
        # 例えば、在庫が10個増えた場合はquantity_changeが10 
        # となり、is_increase()はTrueを返します。
        # 在庫が5個減った場合はquantity_changeが-5となり、
        # is_increase()はFalseを返します。
        return self.quantity_change > 0
    
    #在庫が減った操作かどうかを判定して、True/Falseで返すメソッドです。
    #在庫が減った場合はTrue、増えた場合はFalseを返します。
    def is_decrease(self) -> bool:
        """
        在庫減少操作かどうかを判定
        
        Returns:
            bool: 減少操作の場合True
        """
        # 在庫減少操作かどうかを判定
        # quantity_changeが負の値（0より小さい）なら減少操作
        # quantity_changeは在庫の数量変化を表す整数値です。
        # 在庫が減った場合はTrue、増えた場合はFalseを返します。
        # 例えば、在庫が5個減った場合はquantity_changeが-5  
        # となり、is_decrease()はTrueを返します。
        # 在庫が10個増えた場合はquantity_changeが10となり、
        # is_decrease()はFalseを返します。
        return self.quantity_change < 0
    
    #在庫履歴オブジェクトを辞書形式に変換して返すメソッドです。
    #オブジェクトの情報を辞書型にまとめて返す、データ連携や出力に便利なメソッドです。
    def to_dict(self) -> Dict[str, Any]:
        """
        オブジェクトを辞書に変換
        """
        return {
            #辞書（dict）のキー 'id' に、オブジェクトの history_id の値をセットしています。
            #'id' というキーで、履歴ID（history_id）を辞書に格納するための記述です。
            'id': self.history_id,
            #辞書（dict）のキー 'product_id' に、オブジェクトの product_id の値をセットしています。
            #'product_id' というキーで、関連する商品のIDを辞書に格納するための記述です。
            'product_id': self.product_id,
            #辞書（dict）のキー 'operation_type' に、オブジェクトの operation_type の値をセットしています。
            #'operation_type' というキーで、在庫操作の種別を辞書に格納するための記述です。
            'operation_type': self.operation_type,
            #辞書（dict）のキー 'quantity_change' に、オブジェクトの quantity_change の値をセットしています。
            #'quantity_change' というキーで、在庫の数量変化を辞書に格納するための記述です。
            'quantity_change': self.quantity_change,
            #辞書（dict）のキー 'stock_after' に、オブジェクトの stock_after の値をセットしています。
            #'stock_after' というキーで、在庫操作後の残り在庫数を辞書に格納するための記述です。 
            'stock_after': self.stock_after,
            #辞書（dict）のキー 'memo' に、オブジェクトの memo の値をセットしています。
            #'memo' というキーで、在庫履歴に関連するメモやコメントを辞書に格納するための記述です。
            'memo': self.memo,
            #辞書（dict）のキー 'created_at' に、オブジェクトの created_at の値をセットしています。
            #'created_at' というキーで、在庫履歴の作成日時を辞書に格納するための記述です。
            'created_at': self.created_at
        }
    
    #在庫履歴のデータが正しいかどうかをチェックするメソッドです。
    #在庫履歴のデータが正しいかどうかをチェックし、妥当であればTrue、不正であればFalseを返します。
    #例えば、必須項目が欠けている場合や、操作種別が不正な場合、在庫数が負の値になっている場合などにFalseを返します。
    #オブジェクトのデータが正しいかどうかをチェックし、結果をTrue/Falseで返すメソッドです。
    def validate(self) -> bool:
        """
        データの妥当性をチェック
        """
        # 必須項目のチェック
        # product_id（商品ID）と operation_type（操作種別）が必須項目として存在するかをチェックします。
        # どちらかが欠けている場合は、Falseを返します。
        if not self.product_id or not self.operation_type:
            return False
        
        # 操作種別のチェック
        #許可された操作種別（operation_type）の一覧をリストで定義しています。
        #有効な操作種別（operation_type）をリストでまとめて管理するための定義です。
        valid_operations = ['purchase', 'use', 'adjust']
        # operation_typeが有効な操作種別のいずれかであるかをチェックします。
        # operation_typeがvalid_operationsに含まれていない場合は、Falseを返します。
        # 例えば、operation_typeが 'purchase'、'use'、'adjust' のいずれかでない場合は不正と判断されます。
        # これにより、在庫履歴の操作種別が正しいかどうかを確認できます。
        if self.operation_type not in valid_operations:
            return False
        
        # 在庫数のチェック
        # stock_after（操作後の在庫数）が0以上であるかをチェックします。
        # stock_afterが負の値（0未満）である場合は、在庫数が不正と判断され、Falseを返します。
        # 例えば、在庫操作後の在庫数が-1や-5など負の値になっている場合は不正と判断されます。
        # これにより、在庫数が正しい範囲内にあるかどうかを確認できます。
        # stock_afterは在庫操作後の残り在庫数を表す整数値です。
        if self.stock_after < 0:
            return False
        
        return True
    
    #在庫履歴の情報を人間にわかりやすい文字列形式で返すメソッドです。
    #在庫履歴の情報をわかりやすい文字列形式で返すメソッドです。
    def __str__(self) -> str:
        """
        履歴情報を文字列で返す
        """
        #在庫履歴の操作種別を日本語表示に変換し、数量変化と残り在庫数を含む文字列を返します。
        # get_operation_display()メソッドを使って、操作種別を日本語表示に変換します。
        operation = self.get_operation_display()
        #数量変化（quantity_change）をわかりやすい形式に変換します。
        # quantity_changeが正の値なら「+」を付けて表示し、
        #負の値ならそのまま表示します。
        # 例えば、quantity_changeが5なら「+5個」、-3なら「-3個」と表示します。
        #quantity_change=在庫の数量変化を表す整数値
        change_text = f"+{self.quantity_change}" if self.quantity_change > 0 else str(self.quantity_change)

#self.created_atに値（作成日時）が入っているかどうかを判定できます。
#self.created_atは、在庫履歴などの「作成日時」を表す属性です。
        if self.created_at:
            date_text = self.created_at[:10]
        else:
            # self.created_atがNoneや空文字の場合は「日付不明」と表示します。
            # これにより、作成日時が不明な場合でも適切な表示ができます。
            # 例えば、在庫履歴の作成日時が設定されていない場合は、
            #「日付不明」と表示されます。
            date_text = "日付不明"
        #在庫履歴の操作種別と数量変化、残り在庫数、作成日時を含む文字列を返します。
        # self.stock_after=在庫操作後の残り在庫数を表す整数値
        # self.created_at=在庫履歴の作成日時を表す文字列
        # 例えば、「購入: +5個 → 残り10個 (2023-10-01)」のような形式で表示されます。
        # これにより、在庫履歴の内容を簡潔に把握
        # できるようになります。
        # operation: 操作種別の日本語表示
        # change_text: 数量変化の表示（+5個や-3個など）
        # self.stock_after: 操作後の残り在庫数
        # date_text: 作成日時の表示（YYYY-MM-DD形式）
        return f"{operation}: {change_text}個 → 残り{self.stock_after}個 ({date_text})"
    
    #在庫履歴オブジェクトのデバッグ用の詳細表示を返すメソッドです。
    #在庫履歴オブジェクトの詳細な情報を表示するためのメソッドです。
    #オブジェクトのID、商品ID、数量変化を含む詳細な文字列を返します。
    #デバッグやログ出力などで、在庫履歴の内容を確認するために使用します。
    def __repr__(self) -> str:
        """
        デバッグ用の詳細表示
        """
        #在庫履歴のID、商品ID、数量変化を含む詳細な文字列を返します。
        # self.history_id=在庫履歴1件ごとに割り当てられる番号やID
        # self.product_id=在庫履歴が関連する商品を識別するためのID
        # self.quantity_change=在庫の数量変化を表す整数値
        # 例えば、「StockHistory(id=1, product_id=100, change=5)」のような形式で表示されます。
        # これにより、在庫履歴の内容を簡潔に把握
        return f"StockHistory(id={self.history_id}, product_id={self.product_id}, change={self.quantity_change})"

# StockHistoryクラスのファクトリーメソッド
#データベースやCSVなどの「1行データ」から、StockHistoryオブジェクトを生成する関数です。
#データベースやCSVファイルからデータを読み込むときに、行データをStockHistoryオブジェクトに変換するための関数です。
#この関数を使うことで、データベースの行データを簡単にStockHistoryオブジェクトに変換できます。
def create_history_from_row(row) -> StockHistory:
    """
    データベース行からStockHistoryオブジェクトを作成
    """
    # rowはデータベースの行データ（sqlite3.Rowオブジェクトなど）を想定しています。
    # StockHistoryクラスのインスタンスを作成し、rowデータを渡して初期化します。
    # row（データベース行などの辞書データ）を、StockHistoryオブジェクトに変換して返しています。
    return StockHistory(data=row)

#複数のデータベース行（rows）から、StockHistoryオブジェクトのリストを作成して返す関数です。

def create_history_list_from_rows(rows) -> list[StockHistory]:
    """
    データベース行のリストからStockHistoryオブジェクトのリストを作成
    """
    #複数のデータベース行（rows）から、StockHistoryオブジェクトのリストを一括で生成して返しています。
    return [StockHistory(data=row) for row in rows]

# テスト実行（このファイルが直接実行された場合）
if __name__ == "__main__":
    print("=== 在庫履歴データモデルのテスト ===")
    
    # 1. 手動作成テスト
    print("\n1. 手動作成テスト")
    history1 = StockHistory(
        product_id=1,
        operation_type='purchase',
        quantity_change=5,
        stock_after=5,
        memo='初回購入'
    )
    print(f"作成した履歴: {history1}")
    print(f"操作種別: {history1.get_operation_display()}")
    print(f"増加操作？: {history1.is_increase()}")
    print(f"減少操作？: {history1.is_decrease()}")
    print(f"デバッグ表示: {repr(history1)}")
    
    # 2. データベース風データから作成テスト
    print("\n2. データベース風データから作成テスト")
    db_data = {
        'id': 1,
        'product_id': 1,
        'operation_type': 'use',
        'quantity_change': -2,
        'stock_after': 3,
        'memo': '使用',
        'created_at': '2024-06-04 16:00:00'
    }
    history2 = StockHistory(data=db_data)
    print(f"作成した履歴: {history2}")
    print(f"操作種別: {history2.get_operation_display()}")
    print(f"増加操作？: {history2.is_increase()}")
    print(f"減少操作？: {history2.is_decrease()}")
    print(f"辞書変換: {history2.to_dict()}")
    
    # 3. バリデーションテスト
    print("\n3. バリデーションテスト")
    valid_history = StockHistory(product_id=1, operation_type='purchase', stock_after=5)
    invalid_history = StockHistory(product_id=None, operation_type='invalid', stock_after=-1)
    
    print(f"有効履歴の検証: {valid_history.validate()}")
    print(f"無効履歴の検証: {invalid_history.validate()}")
    
    # 4. ファクトリーメソッドテスト
    print("\n4. ファクトリーメソッドテスト")
    sample_rows = [
        {'id': 1, 'product_id': 1, 'operation_type': 'purchase', 'quantity_change': 5, 'stock_after': 5, 'memo': '購入'},
        {'id': 2, 'product_id': 1, 'operation_type': 'use', 'quantity_change': -1, 'stock_after': 4, 'memo': '使用'},
        {'id': 3, 'product_id': 2, 'operation_type': 'adjust', 'quantity_change': -1, 'stock_after': 0, 'memo': '調整'},
    ]
    histories = create_history_list_from_rows(sample_rows)
    print(f"作成した履歴リスト: {len(histories)}件")
    for history in histories:
        print(f"  - {history}")
    
    # 5. 操作種別別テスト
    print("\n5. 操作種別別テスト")
    operations = [
        {'type': 'purchase', 'change': 10, 'after': 10},
        {'type': 'use', 'change': -3, 'after': 7},
        {'type': 'adjust', 'change': -1, 'after': 6},
    ]
    
    for op in operations:
        history = StockHistory(
            product_id=1,
            operation_type=op['type'],
            quantity_change=op['change'],
            stock_after=op['after']
        )
        print(f"  {history.get_operation_display()}: {history}")
    
    print("\n=== テスト完了 ===")