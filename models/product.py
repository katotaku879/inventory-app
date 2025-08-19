#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品データモデル
商品情報を管理するクラスを定義
"""

from datetime import datetime #日付や時刻を扱うための機能を使えるようにします。
#Optional 値が「ある場合」と「ない場合（None）」の両方を型ヒントで表せるようにします。
#Dict 辞書型（keyとvalueのペアのコレクション）を型ヒントで表現します。
#Dict[str, int] は「キーがstr型、値がint型の辞書」を意味します。
#Any 任意の型を表すための型ヒントで、どんな型でも受け入れられることを示します。
from typing import Optional, Dict, Any
# sqlite3 モジュールを使って、SQLiteデータベースとやり取りできるようにします。
import sqlite3

class Product: # クラス定義（商品の設計図）
    """
    商品情報を管理するクラス
    """
    #商品情報を管理するProductクラスのコンストラクタ（初期化メソッド）**です
    #data引数を使って、データベースから取得した商品情報を初期化することもできます。
    #data が None の場合は、他の引数（nameやbrandなど）で個別に値を指定して初期化します。
    #これにより、「データベースから取得した既存データ」と「新規入力データ」の両方に対応できる柔軟な初期化が可能になります
    #product_id: Optional[int] = None は、商品IDが整数型であることを示し、Noneも許容されることを意味します。
    #name: str = "" は「商品名を文字列で受け取り、省略時は空文字列になる」ことを意味します
    # brand: str = "" は「ブランド名を文字列で受け取り、省略時は空文字列になる」ことを意味します
    # size: str = "" は「サイズを文字列で受け取り、省略時は空文字列になる」ことを意味します
    # category: str = "" は「カテゴリを文字列で受け取り、省略時は空文字列になる」ことを意味します
    # current_stock: int = 0 は「現在の在庫数を整数で受け取り、省略時は0になる」ことを意味します
    # min_stock: int = 1 は「最小在庫数を整数で受け取り、省略時は1になる」ことを意味します
    # purchase_location: str = "" は「購入場所を文字列で受け取り、省略時は空文字列になる」ことを意味します
    # price: float = 0.0 は「価格を浮動小数点数で受け取り、省略時は0.0になる」ことを意味します
    # storage_location: str = "" は「保存場所を文字列で受け取り、省略時は空文字列になる」ことを意味します
    # expiry_date: Optional[str] = None は「消費期限を文字列で受け取り、省略時はNone（未設定）になる」ことを意味します

    def __init__(self, data=None, product_id: Optional[int] = None, name: str = "", 
                brand: str = "", size: str = "", category: str = "",
                current_stock: int = 0, min_stock: int = 1,
                purchase_location: str = "", price: float = 0.0,
                storage_location: str = "", expiry_date: Optional[str] = None):
        #消費期限を「日付」または「未設定（None）」で登録できます。
        """
        商品オブジェクトを初期化
        
        Args:
            data: sqlite3.Rowオブジェクト または 辞書（新規追加）
            product_id: 商品ID（データベースの主キー）
            name: 商品名
            brand: ブランド名
            size: サイズ
            category: カテゴリ
            current_stock: 現在の在庫数
            min_stock: 最小在庫数
            purchase_location: 購入場所
            price: 価格
            storage_location: 保存場所
            expiry_date: 消費期限（YYYY-MM-DD形式）
        """
        #dataがNoneでない場合は、データベースから取得したデータを使って初期化します。
        #データベースから取得したデータ（sqlite3.Rowや辞書型データなど）が渡された場合に、
        # そのデータを使って商品オブジェクトを初期化するための条件分岐
        if data is not None: #データベースから取得したデータがある場合
            #_init_from_dataメソッドを呼び出して、データベースの行データから商品オブジェクトを初期化します。
            #_init_from_dataメソッドは、データベースの行データを使って商品オブジェクトの属性を設定します。
            self._init_from_data(data) #データから初期化
        else: #新規追加の場合
            self.product_id = product_id
            self.name = name
            self.brand = brand
            self.size = size
            self.category = category
            self.current_stock = current_stock
            self.min_stock = min_stock
            self.purchase_location = purchase_location
            self.price = price
            self.storage_location = storage_location
            self.expiry_date = expiry_date
            #オブジェクト（商品データ）が作られた日時を記録するための情報
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #オブジェクトが最後に更新された日時を記録するための情報
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #データベースから取得したデータや辞書型データを使って、
    # Productオブジェクトの各属性を一括でセット（初期化）するための内部メソッド

    def _init_from_data(self, data):
        """
        データベースデータから初期化（内部用）
        
        Args:
            data: sqlite3.Row または 辞書
        """
        try: 
        #「id」または「product_id」というキーの値を優先的に取得して、オブジェクトのIDとして使う
        #オブジェクトのIDとは、「その商品だけを一意に特定できる番号（主キー）」
        #データベースや辞書データから「商品ID」を柔軟に取得できる
        #「id」または「product_id」どちらかのキーが存在すれば、その値をself.product_idにセットします。
            self.product_id = data['id'] if 'id' in data.keys() else (data['product_id'] if 'product_id' in data.keys() else None)
            #データベースや辞書データから「商品名」を安全に取得し、なければ空文字にすることができます。
            #dataは辞書型（またはsqlite3.Rowなど）で、商品情報の各項目がキーと値のペアで格納されています。
            #if 'name' in data.keys()で、dataの中に「name」というキーがあるかを確認します。
            #もし「name」が存在すれば、その値をself.nameにセットします。
            self.name = data['name'] if 'name' in data.keys() else ''
            #データベースや辞書データから「ブランド名」を安全に取得し、なければ空文字にすることができます。
            #if 'brand' in data.keys()で、dataの中に「brand」というキーがあるかを確認します。
            #もし「brand」が存在すれば、その値をself.brandにセットします。
            self.brand = data['brand'] if 'brand' in data.keys() else ''
            #データベースや辞書データから「サイズ」を安全に取得し、なければ空文字にすることができます。
            #if 'size' in data.keys()で、dataの中に「size」というキーがあるかを確認します。
            #もし「size」が存在すれば、その値をself.sizeにセットします。
            self.size = data['size'] if 'size' in data.keys() else ''
            #データベースや辞書データから「カテゴリ」を安全に取得し、なければ空文字にすることができます。
            #if 'category' in data.keys()で、dataの中に「category」というキーがあるかを確認します。
            #もし「category」が存在すれば、その値をself.categoryにセットします。
            self.category = data['category'] if 'category' in data.keys() else ''
            #データベースや辞書データから「現在の在庫数」を安全に取得し、なければ0にすることができます。
            #if 'current_stock' in data.keys()で、dataの中に「current_stock」というキーがあるかを確認します。
            #もし「current_stock」が存在すれば、その値をself.current_stockにセットします。
            #もし「current_stock」が存在しなければ、0をセットします。
            self.current_stock = data['current_stock'] if 'current_stock' in data.keys() else 0
            #データベースや辞書データから「最小在庫数」を安全に取得し、なければ1にすることができます。
            #if 'min_stock' in data.keys()で、dataの中に「min_stock」というキーがあるかを確認します。
            #もし「min_stock」が存在すれば、その値をself.min_stockにセットします。
            #もし「min_stock」が存在しなければ、1をセットします。
            self.min_stock = data['min_stock'] if 'min_stock' in data.keys() else 1
            #データベースや辞書データから「購入場所」を安全に取得し、なければ空文字にすることができます。
            #if 'purchase_location' in data.keys()で、dataの中に「purchase_location」というキーがあるかを確認します。
            #もし「purchase_location」が存在すれば、その値をself.purchase_locationにセットします。
            #もし「purchase_location」が存在しなければ、空文字をセットします。
            self.purchase_location = data['purchase_location'] if 'purchase_location' in data.keys() else ''
            #データベースや辞書データから「価格」を安全に取得し、なければ0.0にすることができます。
            #if 'price' in data.keys()で、dataの中に「price」というキーがあるかを確認します。
            #もし「price」が存在すれば、その値をself.priceにセットします。
            self.price = data['price'] if 'price' in data.keys() else 0.0
            #データベースや辞書データから「保存場所」を安全に取得し、なければ空文字にすることができます。
            #if 'storage_location' in data.keys()で、dataの中に「storage_location」というキーがあるかを確認します。
            #もし「storage_location」が存在すれば、その値をself.storage_locationにセットします。
            #もし「storage_location」が存在しなければ、空文字をセットします。
            self.storage_location = data['storage_location'] if 'storage_location' in data.keys() else ''
            #データベースや辞書データから「消費期限」を安全に取得し、なければNoneにすることができます。
            #if 'expiry_date' in data.keys()で、dataの中に「expiry_date」というキーがあるかを確認します。
            #もし「expiry_date」が存在すれば、その値をself.expiry_dateにセットします。
            #もし「expiry_date」が存在しなければ、Noneをセットします。
            self.expiry_date = data['expiry_date'] if 'expiry_date' in data.keys() else None
            #データベースや辞書データから「作成日時」を安全に取得し、なければNoneにすることができます。
            #if 'created_at' in data.keys()で、dataの中に「created_at」というキーがあるかを確認します。
            #もし「created_at」が存在すれば、その値をself.created_atにセットします。
            #もし「created_at」が存在しなければ、Noneをセットします。
            self.created_at = data['created_at'] if 'created_at' in data.keys() else None
            #データベースや辞書データから「更新日時」を安全に取得し、なければNoneにすることができます。
            #if 'updated_at' in data.keys()で、dataの中に「updated_at」というキーがあるかを確認します。
            #もし「updated_at」が存在すれば、その値をself.updated_atにセットします。
            #もし「updated_at」が存在しなければ、Noneをセットします。
            self.updated_at = data['updated_at'] if 'updated_at' in data.keys() else None  
        #もしdataが辞書型でない場合（例えば、sqlite3.Rowオブジェクトなど）やキーが存在しない場合は、
        except (KeyError, TypeError):
            #データベースや辞書型データから「商品ID」を安全かつ柔軟に取得するためのもの
            #dataの中に「id」または「product_id」というキーが存在しない場合は、Noneをセットします。
            #もしdataが辞書型でない場合やキーが存在しない場合は、product_idをNoneに設定します。
            #この処理により、dataが不正な形式であっても、Productオブジェクトは作成されます。
            #例外が発生した場合は、product_idをNoneに設定します。
            self.product_id = data['id'] if 'id' in data.keys() else (data['product_id'] if 'product_id' in data.keys() else None)
            self.name = data['name'] if 'name' in data.keys() else ''
            self.brand = data['brand'] if 'brand' in data.keys() else ''
            self.size = data['size'] if 'size' in data.keys() else ''
            self.category = data['category'] if 'category' in data.keys() else ''
            self.current_stock = data['current_stock'] if 'current_stock' in data.keys() else 0
            self.min_stock = data['min_stock'] if 'min_stock' in data.keys() else 1
            self.purchase_location = data['purchase_location'] if 'purchase_location' in data.keys() else ''
            self.price = data['price'] if 'price' in data.keys() else 0.0
            self.storage_location = data['storage_location'] if 'storage_location' in data.keys() else ''
            self.expiry_date = data['expiry_date'] if 'expiry_date' in data.keys() else None
            self.created_at = data['created_at'] if 'created_at' in data.keys() else None
            self.updated_at = data['updated_at'] if 'updated_at' in data.keys() else None
 

        
    #商品オブジェクトの在庫状況を判定し、その状態を文字列で返すメソッド
    def get_stock_status(self) -> str: #文字列を返すメソッド
        """
        在庫状況を返す
        
        Returns:
            str: 'out_of_stock', 'low_stock', 'normal'
        """
        if self.current_stock <= 0: # 在庫が0以下
            return 'out_of_stock' # → 在庫切れ
        elif self.current_stock <= self.min_stock: # 在庫が最小在庫以下
            return 'low_stock' # → 在庫少
        else: # それ以外
            return 'normal' # → 正常
    
    #「商品が消費期限切れかどうか」を判定して、期限切れならTrue、そうでなければFalseを返すもの
    #bool 「True（真）」または「False（偽）」の2つの値だけを持つ、Pythonの基本的なデータ型
    def is_expired(self) -> bool:
        """
        期限切れかどうかを判定
        
        Returns:
            bool: 期限切れの場合True
        """
        if not self.expiry_date: # 期限日が設定されていない場合
            return False # 期限切れではない
        
        #消費期限が正しい日付なら期限切れかどうか判定し、もし日付が不正なら「期限切れではない」と判断します
        try:
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d") # 文字列を日付に変換 "2024-06-04" 形式の文字列を期待
            return expiry < datetime.now() # 現在の日付と比較して期限切れかどうかを判定
        except ValueError: # 文字列が日付形式でない場合
            return False
    
    #商品の在庫数を新しい値（new_stock）に更新し、更新日時（updated_at）も記録できるようにします。
    def update_stock(self, new_stock: int):
        """
        在庫数を更新
        
        Args:
            new_stock: 新しい在庫数
        """
        self.current_stock = new_stock
        #日時を「年-月-日 時:分:秒」の文字列に変換します。
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#Productオブジェクトの全ての属性（商品ID、名前、ブランド、在庫数など）を辞書型（dict）に変換して返すメソッド
#to_dict オブジェクトの中身を辞書型に変換して返すメソッド
#Dict[str, Any] は「キーが文字列型、値が任意の型の辞書」を意味します。
#「キー」とは、辞書型（dict）で値を取り出すときに使う“名前”や“ラベル”のこと
#self＝Productクラスのオブジェクト
    def to_dict(self) -> Dict[str, Any]:
        """
        オブジェクトを辞書に変換
        
        Returns:
            Dict[str, Any]: 商品データの辞書
        """
        #Productクラスの to_dict メソッドの返り値
        return {
            #「id」というキーに、オブジェクトが持つ商品ID（product_id）の値をセットし、
            # to_dictメソッドの戻り値の辞書に含めている
            'id': self.product_id,
            #「name」キーに、そのProductオブジェクトが持つ商品名（self.name）をセットして、辞書として返す
            'name': self.name,
            #「brand」キーに、そのProductオブジェクトが持つブランド名（self.brand）をセットして、辞書として返す
            'brand': self.brand,
            #「size」キーに、そのProductオブジェクトが持つサイズ（self.size）をセットして、辞書として返す
            'size': self.size,
            #「category」キーに、そのProductオブジェクトが持つカテゴリ（self.category）をセットして、辞書として返す
            'category': self.category,
            #「current_stock」キーに、そのProductオブジェクトが持つ現在の在庫数（self.current_stock）をセットして、辞書として返す
            'current_stock': self.current_stock,
            #「min_stock」キーに、そのProductオブジェクトが持つ最小在庫数（self.min_stock）をセットして、辞書として返す
            #最小在庫数を取得し、辞書として返す
            'min_stock': self.min_stock,
            #「purchase_location」キーに、そのProductオブジェクトが持つ購入場所（self.purchase_location）をセットして、辞書として返す
            'purchase_location': self.purchase_location,
            #「price」キーに、そのProductオブジェクトが持つ価格（self.price）をセットして、辞書として返す
            #価格を取得し、辞書として返す
            'price': self.price,
            #「storage_location」キーに、そのProductオブジェクトが持つ保存場所（self.storage_location）をセットして、辞書として返す
            'storage_location': self.storage_location,
            #「expiry_date」キーに、そのProductオブジェクトが持つ消費期限（self.expiry_date）をセットして、辞書として返す
            'expiry_date': self.expiry_date,
            #「created_at」キーに、そのProductオブジェクトが持つ作成日時（self.created_at）をセットして、辞書として返す
            'created_at': self.created_at,
            #「updated_at」キーに、そのProductオブジェクトが持つ更新日時（self.updated_at）をセットして、辞書として返す
            #更新日時を取得し、辞書として返す
            'updated_at': self.updated_at
        }
    
    #Productオブジェクトのデータが正しいか（妥当か）をチェックするメソッド
    def validate(self) -> bool:
        """
        データの妥当性をチェック
        
        Returns:
            bool: 有効な場合True
        """
        # 必須項目のチェック
        #商品名（self.name）またはカテゴリ（self.category）が空（未入力や空文字）の場合にTrueとなる条件式
        #not self.name：self.nameが空文字（""）やNoneの場合にTrue
        #not self.category：self.categoryが空文字（""）やNoneの場合にTrue
        # 商品名とカテゴリは必須項目なので、どちらかが空なら無効
        #この条件がTrueになると、validateメソッドはFalseを返します。
        if not self.name or not self.category:
            return False
        
        # 数値項目のチェック
        #現在の在庫数（self.current_stock）または最小在庫数（self.min_stock）が0未満（マイナス）であればTrueになる条件式
        if self.current_stock < 0 or self.min_stock < 0:
            return False
        
        # 価格（self.price）が0未満（マイナス）であればTrueになる条件式
        #価格は0以上でなければならないので、マイナスの場合は無効
        #もしマイナスなら「その商品データは不正」としてバリデーションNG（False）を返すための条件式
        if self.price < 0:
            return False
        
        return True    
    
    #商品情報を文字列で表現するためのメソッド
    #__str__メソッドは、オブジェクトを文字列として表現するための特別なメソッド
    #このメソッドを定義することで、print関数やstr関数でProductオブジェクトを表示したときに、
    #どのような文字列が表示されるかをカスタマイズできます。
    def __str__(self) -> str:
        """
        商品情報を文字列で返す
        """
        #Productクラスのインスタンス（self）の在庫状況を判定し、
        # その状態（'out_of_stock'、'low_stock'、'normal'のいずれか）をstatus変数に代入する処理
        #get_stock_statusメソッドを呼び出して、現在の在庫状況を取得します。
        #status変数には、在庫状況に応じた文字列が格納されます。
        #Productオブジェクトの在庫状況（英語の状態名）を取得し、status変数にセットする処理です
        status = self.get_stock_status()
        #status変数の値に応じて、在庫状況を日本語の文字列に変換する辞書を定義
        #status変数の値が 'out_of_stock' の場合は '在庫切れ'、'low_stock' の場合は '在庫少'、それ以外は '正常' とします。
        status_text = {
            'out_of_stock': '在庫切れ',
            'low_stock': '在庫少',
            'normal': '正常'
        }.get(status, '不明') # # 状態が不明な場合のデフォルト値
        
        #Productクラスのインスタンスをprint関数やstr関数で文字列化したときに表示される内容を定義しています
        #self.name（商品名）、self.brand（ブランド名）、status_text（在庫状況の日本語表現）、
        # self.current_stock（現在の在庫数）を組み合わせて文字列を作成
        #f-stringを使って、商品名、ブランド名、在庫状況、現在の在庫数をフォーマットして返します。
        #f-stringは、文字列の中に変数を埋め込むための便利な方法です。
        return f"{self.name} ({self.brand}) - {status_text} ({self.current_stock}個)"
    
    #デバッグ用の詳細表示を提供するためのメソッド
    #__repr__メソッドは、オブジェクトの詳細な情報を文字列として返すための特別なメソッド
    #このメソッドを定義することで、print関数やrepr関数でProductオブジェクトを表示したときに、
    #どのような文字列が表示されるかをカスタマイズできます。
    #このメソッドは、主にデバッグや開発時にオブジェクトの状態を確認するために使用されます。
    def __repr__(self) -> str:
        """
        デバッグ用の詳細表示
        """
        #Productクラスのインスタンス（self）の商品ID、商品名、現在の在庫数を表示する文字列を返します。
        #f-stringを使って、商品ID、商品名、現在の在庫数をフォーマットして返します。
        #f-stringは、文字列の中に変数を埋め込むための便利な方法です。
        #Productインスタンスの中身（ID・名前・在庫）を分かりやすく表示するための「開発者向けの詳細な文字列表現」を返しています
        return f"Product(id={self.product_id}, name='{self.name}', stock={self.current_stock})"
    
    #データベースから取得した1行分のデータ（row）からProductオブジェクトを作成するファクトリ関数です
    #row引数は、sqlite3.Rowオブジェクトまたは辞書型のデータを受け取ります。
    #「この関数の返り値はProduct型です」という意味の型ヒント
def create_product_from_row(row) -> Product:
    """
    データベース行からProductオブジェクトを作成
    
    Args:
        row: sqlite3.Row または 辞書
        
    Returns:
        Product: 商品オブジェクト
    """
    #「rowの内容をもとにProductオブジェクトを作って返す」という意味
    #Productクラスのコンストラクタを呼び出して、rowのデータを使って新しいProductオブジェクトを作成
    #rowはsqlite3.Rowオブジェクトまたは辞書型のデータで、Productクラスのコンストラクタに渡されます。
    return Product(data=row)

#データベースから取得した複数の行（rows）からProductオブジェクトのリストを作成するファクトリ関数です
#この関数は、データベースから取得した複数の行（rows）を受け取り、それぞれの行からProductオブジェクトを作成して
# リストにまとめて返します。
#rows引数は、sqlite3.Rowオブジェクトのリストを受け取ります。
#list[Product] は「Product型のオブジェクトのリスト」を意味します。
#「Productオブジェクトが複数入ったリスト」を意味します。
def create_product_list_from_rows(rows) -> list[Product]:
    """
    データベース行のリストからProductオブジェクトのリストを作成
    
    Args:
        rows: sqlite3.Rowのリスト
        
    Returns:
        list[Product]: 商品オブジェクトのリスト
    """
    #複数のデータベース行（rows）からProductオブジェクトのリストを一括で生成して返す処理
    #for row in rows 「複数のデータ（rows）」から「1件ずつ（row）」取り出して処理するための基本的なPythonの構文
    return [Product(data=row) for row in rows]    

# テスト用のサンプルデータ作成関数
def create_sample_products():
    """
    テスト用のサンプル商品データを作成
    
    Returns:
        list: Productオブジェクトのリスト
    """
    #商品名、ブランド名、サイズ、カテゴリ、現在の在庫数、最小在庫数、購入場所、価格、保存場所、消費期限
    samples = [
        Product(product_id=1, name="トイレットペーパー", brand="エリエール", size="12ロール", category="日用品", current_stock=3, min_stock=2, purchase_location="ドラッグストア", price=298.0, storage_location="トイレ"),
        Product(product_id=2, name="食器用洗剤", brand="ジョイ", size="400ml", category="洗剤", current_stock=1, min_stock=1, purchase_location="スーパー", price=158.0, storage_location="キッチン"),
        Product(product_id=3, name="シャンプー", brand="パンテーン", size="400ml", category="日用品", current_stock=0, min_stock=1, purchase_location="ドラッグストア", price=698.0, storage_location="お風呂"),
    ]
    return samples

# テスト実行（このファイルが直接実行された場合）
if __name__ == "__main__":
    print("=== 商品データモデルのテスト（拡張版） ===")
    
    # 1. 既存機能テスト
    print("\n1. 従来の手動作成テスト")
    # 手動でProductオブジェクトを作成
    #Productクラスのインスタンス（商品オブジェクト）を手動で生成するためのコード
    product1 = Product(
        #Productクラスのインスタンスを作成する際に「商品名（name）」として "テスト商品" を指定している部分
        name="テスト商品",
        #Productクラスのインスタンスを作成する際に「ブランド名（brand）」として "テストブランド" を指定している部分
        brand="テストブランド",
        #Productクラスのインスタンスを作成する際に「カテゴリ（category）」として "テスト" を指定している部分
        category="テスト",
        #Productクラスのインスタンスを作成する際に「現在の在庫数（current_stock）」として 5 を指定している部分
        current_stock=5,
        #Productクラスのインスタンスを作成する際に「最小在庫数（min_stock）」として 2 を指定している部分
        min_stock=2,
        #Productクラスのインスタンスを作成する際に「価格（price）」として 100.0 を指定している部分
        price=100.0
    )
    #作成した商品情報を日本語で分かりやすく表示する
    print(f"作成した商品: {product1}")
    #product1 の在庫状況を表す英語のコード（'out_of_stock', 'low_stock', 'normal'）がそのまま出力されます
    print(f"在庫状況: {product1.get_stock_status()}")
    #product1 の __repr__ メソッドが呼ばれ、次のようなデバッグ向けの詳細な文字列表現が出力されます。
    print(f"デバッグ表示: {repr(product1)}")
    
    # 2. 新機能：データベース風データから作成テスト
    print("\n2. データベース風データから作成テスト")
    # データベースから取得したデータを模した辞書型データ
    #辞書型データを使ってProductオブジェクトを作成するためのコード
    db_data = {
        'id': 1,
        'name': 'シャンプー',
        'brand': 'パンテーン',
        'category': '日用品',
        'current_stock': 0,
        'min_stock': 1,
        'price': 500.0,
        'created_at': '2024-06-04 15:30:45',
        'updated_at': '2024-06-04 15:30:45'
    }
    #Productクラスのコンストラクタにdb_dataを渡して、Productオブジェクトを作成
    #db_dataは辞書型で、データベースから取得した商品情報を模したものです。
    #Productクラスのインスタンス（商品オブジェクト）をデータベース風のデータから生成するためのコード
    #データベースや辞書形式で用意された商品データ（db_data）から、Productクラスのインスタンス（商品オブジェクト）を生成する
    product2 = Product(data=db_data)
    print(f"作成した商品: {product2}")
    print(f"在庫状況: {product2.get_stock_status()}")
    #product2 の全属性が辞書形式で出力されます
    print(f"辞書変換: {product2.to_dict()}")
    
    # 3. 新機能：バリデーションテスト
    print("\n3. バリデーションテスト")
    #必須項目である「商品名（name）」と「カテゴリ（category）」だけを指定して Product インスタンスを生成する例
    #validate() メソッドは、nameとcategoryが空でないこと、在庫数・最小在庫数・価格が0以上であることをチェックします
    #valid_productはnameとcategoryが指定されているため、valid_product.validate()はTrueを返します
    valid_product = Product(name="有効商品", category="テスト")
    #商品名（name）とカテゴリ（category）の両方が空文字となっている、
    # 無効な（バリデーションに通らない）商品オブジェクトを生成する例
    #validate() メソッドは、nameとcategoryが空であるため、invalid_product.validate()はFalseを返します
    #無効な商品オブジェクトを生成するためのコード
    invalid_product = Product(name="", category="")  # 無効
    
    #valid_product のバリデーション結果が出力されます。
    #invalid_product のバリデーション結果が出力されます。
    #validate() メソッドを呼び出して、商品データの妥当性をチェックします。
    print(f"有効商品の検証: {valid_product.validate()}")
    print(f"無効商品の検証: {invalid_product.validate()}")
    
    # 4. 新機能：ファクトリーメソッドテスト
    print("\n4. ファクトリーメソッドテスト")
    #複数の商品データ（辞書形式）をまとめたリストを作る部分
    sample_rows = [
        #商品データ1件分を表す辞書型（dict）です。
        {'id': 1, 'name': '商品A', 'category': 'カテゴリA', 'current_stock': 5},
        {'id': 2, 'name': '商品B', 'category': 'カテゴリB', 'current_stock': 0},
    ]
    #sample_rows の各辞書（商品データ）から Product オブジェクトが生成され、それらをまとめたリスト products が作られます
    #create_product_list_from_rows 関数は、各行（辞書）ごとに Product(data=row) を呼び出し、Product オブジェクトを生成します
    products = create_product_list_from_rows(sample_rows)
    #作成した商品リストの件数を出力します。
    #products リストの長さを取得して、作成した商品数を表示します。
    print(f"作成した商品リスト: {len(products)}件")
    #products リスト内の各 Product オブジェクトを1件ずつ順番に処理するためのループ構文
    #for product in products: で、products リスト内の各 Product オブジェクトを順番に取り出して処理します。
    #products リスト内の各 Product オブジェクトを表示します。
    for product in products:
        #product の __str__ メソッドが呼ばれ、各商品が日本語で「商品名 (ブランド名) - 在庫状況 (在庫数個)」の形式で表示されます
        print(f"  - {product}")
    
    # 5. 既存機能：サンプルデータテスト
    print("\n5. サンプルデータテスト")
    #テスト用のサンプル商品データ（Productオブジェクトのリスト）が作成されます。
    #create_sample_products 関数を呼び出して、サンプル商品データを生成します。
    #create_sample_products 関数は、あらかじめ定義されたサンプル商品データを返します。
    samples = create_sample_products()
    #samples = create_sample_products() で作成されたサンプル商品のリストから、
    # 各 Product オブジェクトを1件ずつ順番に処理するループ
    for sample in samples:
        #「商品名 (ブランド名) - 在庫状況 (在庫数個)」の日本語表現で出力されます
        print(f"  - {sample}")
        #各サンプル商品の在庫状況が 'out_of_stock'（在庫切れ）、'low_stock'（在庫少）、'normal'（正常）という
        # 英語の状態コードで出力されます
        print(f"    在庫状況: {sample.get_stock_status()}")
        #各サンプル商品の消費期限（expiry_date）が現在日時より前かどうかを判定し、
        # その結果（True または False）が表示されます
        print(f"    期限切れ: {sample.is_expired()}")
    
    print("\n=== テスト完了 ===")
