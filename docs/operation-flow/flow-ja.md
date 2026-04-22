# 動作方式と詳細フロー (日本語)

## 1) 実行フローの目的
システムは class-registration レスポンスを継続監視し、JSON スナップショットを更新し、person マッピングを抽出して、教員名付き時間割をターミナルに表示します。

## 2) 起動フェーズ

1. ユーザーが `python app.py` (または `python src/main.py`) を実行。
2. `app.py` が `src.main.main()` へ委譲。
3. `main()` が `ensure_output_directories()` を実行して出力フォルダ作成。
4. `main()` が `get_teacher_mapping(cache_file)` を実行:
   - `data/cache/teacher_directory_cache.json` からキャッシュ読込。
   - キャッシュが少ない場合は API から教員データを追加取得。
   - 最後に `MANUAL_TEACHER_DATA` をマージ。
5. `main()` が Playwright を起動し、`run_automation(playwright, teacher_mapping)` を呼び出し。

## 3) ブラウザ自動処理ライフサイクル

`run_automation()` 内:

1. `headless=False` で Chromium 起動。
2. context と page を作成。
3. response ハンドラを登録:
   - 各 response を `process_class_registration_response(response, teacher_mapping)` へ渡す。
4. 履修登録ページへ移動。
5. ユーザーのログイン/認証完了を ENTER 入力で待機。

## 4) class-registration レスポンス処理

`process_class_registration_response()` の処理:

1. URL に `TARGET_URL_PART` が無ければ無視。
2. JSON を解析し `data/raw/class_registration_response.json` へ保存。
3. ターミナル画面をクリア。
4. `extract_hust_schedule_final()` を呼び出し:
   - 科目・クラス・カレンダー情報を集計。
   - `teacher_mapping` で teacherId を教員名へ解決。
   - 曜日/時間帯/時限でソート。
   - 時間割と総単位を表示。

この処理は対象レスポンスが来るたびに繰り返されます。

## 5) ログイン確認後の一回取得処理

`run_automation()` で ENTER 後に実行:

1. `fetch_and_save_student_course_members(page)`:
   - 成績ページへ移動。
   - `STUDENT_COURSE_MEMBERS_API_PART` に一致する GET を待機。
   - `data/raw/student_course_members_response.json` へ保存。
   - `save_person_id_name_file()` で
     `data/derived/student_course_members_person_map.json` を生成。

2. `fetch_and_save_student_timetable(page)`:
   - 時間割ページへ移動。
   - `STUDENT_TIMETABLE_API_PART` に一致する POST を待機。
   - `data/raw/student_timetable_response.json` へ保存。
   - `save_person_id_name_file()` で
     `data/derived/student_timetable_person_map.json` を生成。

3. `merge_person_files_into_mapping(...)` で新しい person マップをメモリ上の teacher mapping に統合。

## 6) person マップ抽出ロジック

`save_person_id_name_file(input_file, output_file)` の流れ:

1. 元 JSON を読み込み。
2. ネスト構造を再帰走査 (`walk_and_collect_person_pairs`)。
3. 各 dict で既知パターン抽出 (`collect_person_pairs_from_dict`):
   - `<prefix>Id + <prefix>Name`
   - `<prefix>Ids + <prefix>Names`
   - `id + fullName`
   - `gradeLogs` の `staffId + staffName` を含む JSON 文字列
4. ID/名前を正規化し不正値除外。
5. `-1` の未知 ID を除外。
6. 同一 ID の競合は安定ルールで解決。
7. ソートして最終 ID->name JSON を保存。

## 7) 継続リフレッシュループ

初期処理後、`run_automation()` は無限ループ:

1. 5 秒ごとに履修登録ページを再読み込み。
2. response ハンドラが継続監視し、新規データで時間割を再描画。
3. 例外または終了時のみブラウザを閉じる。

## 8) データ整合モデル

- `data/raw/*`: 最新レスポンスのスナップショット (同名上書き)。
- `data/derived/*`: raw から決定的に生成される派生データ。
- メモリ内 `teacher_mapping` は次の 3 層合成:
  1) cache/API,
  2) 手入力データ,
  3) runtime 生成 person マップ。

## 9) 耐障害性

- 対象レスポンス待機は 2 回リトライ。
- parse/IO 失敗は多くの箇所で捕捉してログ出力、処理継続を優先。
- 欠損フィールドに fallback を置き、表示処理の破綻を抑制。
