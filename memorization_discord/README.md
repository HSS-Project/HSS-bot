# memorization_discord 仕様書

## 概要

`memorization_discord` は、Discord Bot 上で暗記問題（クイズ）の作成・管理・編集・出題・削除・共有などのUI/UXを提供するインターフェース群です。  
ユーザーはボタンやセレクトメニュー、モーダルなどを通じて問題集やジャンルの操作を行います。

---

## ファイル構成と主なクラス・関数

### memorization_maker_add.py

- **クラス: AddQuestionModal**
  - **意味:** 問題追加用のモーダルUI。ユーザーが問題文や答え、選択肢を入力できる。
  - **引数:**  
    - `title`: モーダルのタイトル
  - **主な関数:**
    - `on_submit(interaction)`: モーダル送信時の処理。入力内容を受け取り、問題を追加する。

- **クラス: AddChoiceView**
  - **意味:** 選択肢付き問題の選択肢追加用View。ボタンで選択肢を追加できる。
  - **引数:** なし
  - **主な関数:**
    - `add_choice_callback(interaction)`: 選択肢追加ボタン押下時の処理。

---

### memorization_maker_edit.py

- **クラス: EditQuestionView**
  - **意味:** 問題編集用のView。編集対象の選択や編集モーダルの表示を行う。
  - **引数:**  
    - `questions`: 編集対象の問題リスト
  - **主な関数:**
    - `edit_callback(interaction)`: 編集ボタン押下時の処理。
    - `delete_callback(interaction)`: 削除ボタン押下時の処理。

- **クラス: EditChoiceModal**
  - **意味:** 選択肢編集用のモーダルUI。
  - **引数:**  
    - `choices`: 現在の選択肢リスト
  - **主な関数:**
    - `on_submit(interaction)`: 編集内容の保存処理。

---

### memorization_maker_play.py

- **クラス: PlayQuizView**
  - **意味:** 問題出題・解答用のView。ボタンや選択肢で解答できる。
  - **引数:**  
    - `questions`: 出題する問題リスト
    - `mode`: 出題モード（順番・ランダム等）
  - **主な関数:**
    - `answer_callback(interaction)`: 解答ボタン押下時の処理。
    - `next_callback(interaction)`: 次の問題へ進む処理。

- **クラス: ResultView**
  - **意味:** 結果表示用のView。スコアやミス問題の再出題ボタンなどを持つ。
  - **引数:**  
    - `score`: ユーザーのスコア
    - `missed_questions`: ミスした問題リスト
  - **主な関数:**
    - `retry_callback(interaction)`: ミス問題の再出題処理。

---

### memorization_control.py

- **クラス: ControlPanelView**
  - **意味:** 問題集のコントロールパネル。追加・編集・削除・ジャンル管理・管理者権限管理などのボタンを持つ。
  - **引数:**  
    - `title`: 問題集タイトル
    - `user_id`: 操作ユーザーID
  - **主な関数:**
    - `add_callback(interaction)`: 問題追加ボタン押下時の処理。
    - `edit_callback(interaction)`: 問題編集ボタン押下時の処理。
    - `delete_callback(interaction)`: 問題削除ボタン押下時の処理。
    - `genre_callback(interaction)`: ジャンル管理ボタン押下時の処理。
    - `owner_callback(interaction)`: 管理者権限管理ボタン押下時の処理。

---

### select_title.py

- **クラス: SelectTitleView**
  - **意味:** 問題集やジャンルの選択UI。セレクトメニューで選択し、選択後の処理を行う。
  - **引数:**  
    - `titles`: 選択肢となる問題集タイトルリスト
  - **主な関数:**
    - `on_select(interaction)`: 選択時の処理。

---

### select_mission.py

- **クラス: SelectMissionView**
  - **意味:** 問題単位での選択UI。編集・削除・確認などのViewを提供。
  - **引数:**  
    - `missions`: 問題リスト
  - **主な関数:**
    - `edit_callback(interaction)`: 編集ボタン押下時の処理。
    - `delete_callback(interaction)`: 削除ボタン押下時の処理。
    - `confirm_callback(interaction)`: 確認ボタン押下時の処理。

---

## 引数の意味まとめ

- `user_id`: 操作するユーザーのDiscord ID
- `title`: 問題集タイトル
- `questions` / `missions`: 問題リスト
- `choices`: 選択肢リスト
- `mode`: 出題モード（順番・ランダム等）
- `score`: スコア
- `missed_questions`: ミスした問題リスト

---

## 関数の意味まとめ

- `on_submit`: モーダル送信時の入力内容処理
- `add_callback`: 追加ボタン押下時の処理
- `edit_callback`: 編集ボタン押下時の処理
- `delete_callback`: 削除ボタン押下時の処理
- `genre_callback`: ジャンル管理ボタン押下時の処理
- `owner_callback`: 管理者権限管理ボタン押下時の処理
- `answer_callback`: 解答ボタン押下時の処理
- `next_callback`: 次の問題へ進む処理
- `retry_callback`: ミス問題の再出題処理
- `on_select`: セレクトメニュー選択時の処理
- `confirm_callback`: 確認ボタン押下時の処理

---