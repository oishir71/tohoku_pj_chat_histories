# tohoku_pj_chat_histories
東北プロジェクトにおいて、自治体の方が使用したチャットボットの履歴をCSVまたはXLSXファイルに変換するファイル群が管理されているレポジトリです。

## How to use
お手元にpython環境を用意いただき、`root directory`にある`requirements.txt`を参照し、環境を整えてください。

```bash
python3 -m venv tohoku_pj_chat_histories
source tohoku_pj_chat_histories/bin/activate
cd path/to/root/directory
pip install -r requirements.txt
```

その後、以下の環境変数を設定し、`src directory`に移動していただき、`parser.py`を実行してください。デフォルトでは、`root_directory/histories/sessions.csv`が生成されます。

| 環境変数 | 何者か | 具体例 |
| -- | -- | -- |
| TOHOKU_ORIGIN | オリジン | localhost:8000 |
| TOHOKU_USER_ID | プロジェクトにアクセス可能なユーザー | amin |
| TOHOKU_PASSWORD | ユーザーに設定されているパスワード | password |
| TOHOKU_PROJECT_ID | プロジェクトのID | 631a6a99-0b30-425a-bdf2-af4532ff9451 |

```bash
python parser.py
```

また、引数を用いて上記の環境変数を上書きすることも可能です。出力するファイル形式は2024/11/25現在`csv`または`xlsx`のみに限られることをご留意ください。
```bash
python parser.py \
  --origin https://console.dev.softreef-ai.com \
  --user_id oishir71 \
  --password piyopiyo \
  --project_id ea0ab6c4-212f-431a-82e9-caa2c11f4594 \
  --output_file_name root_directory/histories/sessions.xlsx
```

## What information is retrieved
生成されるファイルは以下の情報が含まれます。各行はユーザーとLLMのやり取りの内1ラリー分に相当し、複数回ラリーが発生したセッションについては複数行に跨って記録されています。
| カラム名 | 実態 | 存在 |
| -- | -- | -- |
| agent_name | エージェント名 | 必ず |
| agent_type | エージェントのタイプ | 必ず |
| agent_context_category | エージェントのカテゴリ、`general`, `prompt`、`rag`のうちいずれかを想定 | 必ず |
| agent_context_description | エージェントに紐付いた内容に対する説明 | `agent_context_category == rag`の場合のみ |
| agent_context_source_text | エージェントに紐付いた内容のソース | `agent_context_category == rag`の場合のみ |
| session_name | セッションの名前 | 必ず |
| session_created_user_name | セッションを作成したユーザーの名前 | 必ず |
| session_message_timestamp | 初めのメッセージが記録された時間 | 必ず |
| session_message_system_content_text | LLMに事前に渡す指示 | `agent_context_category != general`の場合のみ |
| session_message_user_content_text | ユーザーの入力 | 必ず |
| session_message_rag_content_text | LLMに渡されたRAGデータ| `agent_context_category == rag`の場合のみ |
| session_message_assistant_content_text | LLMからの出力 | 必ず |
