# プロジェクト構造 (日本語)

## 1) プロジェクトの目的
このプロジェクトは Playwright を使って HUST 学生ページの API レスポンスを自動取得し、JSON を解析して教員名付きの時間割を見やすく表示します。

## 2) 主要ディレクトリ

- `app.py`
  - 起動用エントリ。`src.main.main()` を呼び出します。
- `src/`
  - メインのソースコード。
- `data/`
  - 取得した JSON と生成データ。
- `.venv/`
  - Python 仮想環境。
- `docs/`
  - ドキュメント。

## 3) ソース構成 (詳細)

### `src/main.py`
- `main()`
  - 実行全体のオーケストレーション。
  - 出力フォルダ作成。
  - 教員マッピング読み込み。
  - Playwright 自動処理開始。

### `src/config.py`
- 設定定数を定義:
  - 各ページ URL と API 判定文字列。
  - デフォルト timeout。
  - 出力ファイルパス。
- `ensure_output_directories()`
  - `data/raw`, `data/derived`, `data/cache` を作成。

### `src/services/browser/`
- `run_automation.py`
  - ブラウザ自動処理のメインループ。
- `process_class_registration_response.py`
  - class-registration レスポンスを判定し、時間割表示処理を起動。
- `fetch_and_save_student_course_members.py`
  - course-members レスポンスを取得・保存。
  - person-id-name マップを生成。
- `fetch_and_save_student_timetable.py`
  - timetable レスポンスを取得・保存。
  - person-id-name マップを生成。

### `src/services/teacher_mapping/`
- `manual_teacher_data.py`
  - 手入力の教員 ID -> 氏名データ。
- `get_teacher_mapping.py`
  - キャッシュ読込、必要に応じて API 追加取得、手入力データをマージ。
- `merge_person_files_into_mapping.py`
  - 生成された person マップを既存マッピングへ追加 (既存キーは上書きしない)。

### `src/services/person_extractor/`
- `constants.py`
  - 人物情報キー検出用ヒント定数。
- `is_person_key.py`
  - キー名が人物系か判定。
- `to_string_id.py`
  - ID を安全な文字列へ正規化。
- `split_names.py`
  - 複数名文字列を分割して整形。
- `add_person_pair.py`
  - `(id, name)` ペアを検証して追加。
- `collect_person_pairs_from_dict.py`
  - 単一 dict から既知パターンで person ペア抽出。
- `walk_and_collect_person_pairs.py`
  - ネスト JSON を再帰的に走査して person ペアを収集。
- `save_person_id_name_file.py`
  - 元 JSON から ID->name マッピング JSON を生成。

### `src/services/schedule_printer.py`
- `extract_hust_schedule_final()`
  - class-registration JSON 読込。
  - 授業データと単位数を集計。
  - 整形済み時間割を表示。

## 4) データ構造

### `data/raw/`
生レスポンス:
- `class_registration_response.json`
- `student_course_members_response.json`
- `student_timetable_response.json`

### `data/derived/`
解析後の生成データ:
- `student_course_members_person_map.json`
- `student_timetable_person_map.json`

### `data/cache/`
キャッシュ:
- `teacher_directory_cache.json`

## 5) コンポーネント連携 (要約)

1. `app.py` から `src/main.py` を起動。
2. `config` が出力フォルダ作成。
3. 教員マッピング初期化。
4. ブラウザ自動処理で必要 API を取得。
5. 生データを `data/raw` に保存。
6. person マップを `data/derived` に生成。
7. マッピングを統合。
8. class-registration レスポンス受信時に時間割を解析・表示。
