# HSS Bot
HSS APIのpythonラッパー`hss.py`の見本用bot。

## 環境構築・実行
1. `pip install -U -r requirements.txt`で必要なライブラリをインストール
2. `token.json`を準備し、以下の内容を書き込む
    ```json
    {"TOKEN_2": "...(Bot TOKEN)"}
    ```
3. helpコマンドのデータは`help.json`を用意して以下のように書き込むことで反映させることができる。
    ```json
    {
        "schedule": {},
        "memorization": {}
    }
    ```
4. `token.json` に Gemini API キーを追加する。
    ```json
    {"TOKEN_2": "...(Bot TOKEN)", "GEMINI_API_KEY": "...(Gemini API Key)"}
    ```
5. `py main.py`などのコマンドで実行すればok

## 暗記メモリ作成

- `m!add_pdf <title>` を使うと、添付したPDFから Gemini API で問題を自動生成できます。
- このコマンドはユーザーID `705264675138568192` のみ実行できます。
- PDFはコマンド送信時にメッセージへ添付してください。
