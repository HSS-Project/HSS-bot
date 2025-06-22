# memorization_maker 仕様書

## 概要

`memorization_maker` は、暗記問題（クイズ）の作成・管理・編集・削除・共有などを行うためのロジック群です。  
Discord Bot から呼び出され、ユーザーごとに問題集やジャンルの管理、問題の追加・編集・削除、共有コードによる共有などを実現します。

---

## ファイル構成と主な関数

### base_question_add.py

- `async def add_question(user_id, title, question, answer, choices=None)`  
  **内容:** 指定したタイトル（問題集）に新しい問題を追加します。選択肢付き問題にも対応。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `question`: 問題文  
    - `answer`: 答え  
    - `choices`: 選択肢リスト（省略可）

- `async def add_questions_from_excel(user_id, title, excel_file_path)`  
  **内容:** Excelファイルから複数の問題を一括追加します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `excel_file_path`: Excelファイルのパス

- `async def add_sentence_question(user_id, title, sentence, blanks)`  
  **内容:** 文章穴埋め問題を追加します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `sentence`: 文章  
    - `blanks`: 空欄部分のリスト

---

### base_question_delete.py

- `async def delete_question(user_id, title, question_index)`  
  **内容:** 指定した問題集から特定の問題を削除します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `question_index`: 削除する問題のインデックス

- `async def delete_title(user_id, title)`  
  **内容:** 問題集（タイトル）ごと削除します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル

---

### base_question_edit.py

- `async def edit_question(user_id, title, question_index, new_question, new_answer, new_choices=None)`  
  **内容:** 問題文・答え・選択肢を編集します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `question_index`: 編集する問題のインデックス  
    - `new_question`: 新しい問題文  
    - `new_answer`: 新しい答え  
    - `new_choices`: 新しい選択肢リスト（省略可）

- `async def edit_sentence_question(user_id, title, question_index, new_sentence, new_blanks)`  
  **内容:** 文章穴埋め問題の編集。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `question_index`: 編集する問題のインデックス  
    - `new_sentence`: 新しい文章  
    - `new_blanks`: 新しい空欄リスト

---

### base_question_get.py

- `async def get_titles(user_id)`  
  **内容:** ユーザーが持つ問題集（タイトル）一覧を取得します。  
  **引数:**  
    - `user_id`: ユーザーID

- `async def get_questions(user_id, title)`  
  **内容:** 指定した問題集の全問題を取得します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル

- `async def check_answer(user_id, title, question_index, user_answer)`  
  **内容:** 解答チェックを行い、正誤判定を返します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `question_index`: 問題のインデックス  
    - `user_answer`: ユーザーの解答

---

### genre.py

- `async def create_genre(user_id, genre_name)`  
  **内容:** 新しいジャンル（カテゴリ）を作成します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `genre_name`: ジャンル名

- `async def delete_genre(user_id, genre_name)`  
  **内容:** ジャンルを削除します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `genre_name`: ジャンル名

- `async def move_title_to_genre(user_id, title, genre_name)`  
  **内容:** 問題集を指定ジャンルに移動します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `genre_name`: ジャンル名

- `async def share_genre(user_id, genre_name)`  
  **内容:** ジャンルの共有コードを発行します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `genre_name`: ジャンル名

---

### memorization_vocabulary.py

- `async def import_vocabulary_from_excel(user_id, title, excel_file_path)`  
  **内容:** Excelファイルから英単語問題を自動生成します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title`: 問題集タイトル  
    - `excel_file_path`: Excelファイルのパス

---

### owner_manager.py

- `async def add_owner(title, user_id)`  
  **内容:** 問題集の共同管理者を追加します。  
  **引数:**  
    - `title`: 問題集タイトル  
    - `user_id`: 追加するユーザーID

- `async def remove_owner(title, user_id)`  
  **内容:** 管理者から外します。  
  **引数:**  
    - `title`: 問題集タイトル  
    - `user_id`: 削除するユーザーID

- `async def get_owners(title)`  
  **内容:** 管理者一覧を取得します。  
  **引数:**  
    - `title`: 問題集タイトル

---

### Read_and_Write.py

- `def read_json(file_path)`  
  **内容:** JSONファイルからデータを読み込みます。  
  **引数:**  
    - `file_path`: ファイルパス

- `def write_json(file_path, data)`  
  **内容:** JSONファイルにデータを書き込みます。  
  **引数:**  
    - `file_path`: ファイルパス  
    - `data`: 書き込むデータ

---

### share.py

- `async def generate_share_code(user_id, title_or_genre)`  
  **内容:** 問題集やジャンルの共有コードを生成します。  
  **引数:**  
    - `user_id`: ユーザーID  
    - `title_or_genre`: 問題集タイトルまたはジャンル名

- `async def get_shared_data(share_code)`  
  **内容:** 共有コードから問題集やジャンルのデータを取得します。  
  **引数:**  
    - `share_code`: 共有コード

---

## データ構造

- `memorization_base_v2.json`  
  問題集（タイトルごと）のデータを保存。  
  各問題集は `sharecode` をキーに持ち、`title`, `questions`, `owner` などを保持。

- `memorization_user_v2.json`  
  ユーザーごとのジャンル・進捗・スコア等を保存。

---

## 主な機能

- 問題集（タイトル）の作成・削除・編集
- 問題（記述式・選択式・文章穴埋め）の追加・編集・削除
- ジャンル（カテゴリ）の作成・削除・移動・共有
- 問題集・ジャンルの共有コードによる他ユーザーへの共有
- Excelファイルからの問題インポート
- 問題集のオーナー（管理者）管理

---

## 注意事項

- データはJSONファイルで管理されているため、同時書き込みや破損に注意
- 共有コードは重複しないようランダム生成・チェックを行う
- 問題数やジャンル数には上限がある（例：ジャンルは100個まで等）

---

## 拡張性

- 問題形式やジャンル管理の拡張が容易
- 他のストレージ（DB等）への移行も比較的容易