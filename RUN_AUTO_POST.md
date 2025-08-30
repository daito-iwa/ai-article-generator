# 🤖 自動投稿システムの実行方法

## ⚠️ 重要：APIキーの設定が必要です

### 1. GitHub Personal Access Tokenの取得

1. GitHubにログイン
2. 右上のプロフィール → Settings
3. 左メニューの最下部 → Developer settings
4. Personal access tokens → Tokens (classic)
5. 「Generate new token」をクリック
6. 以下を設定：
   - Note: `AI Article Auto Post`
   - Expiration: `90 days`（お好みで）
   - Select scopes: `repo`にチェック（全てのrepo権限）
7. 「Generate token」をクリック
8. **表示されたトークンをコピー**（二度と表示されません！）

### 2. OpenAI APIキーの取得

1. [OpenAI Platform](https://platform.openai.com/)にログイン
2. 右上のプロフィール → View API keys
3. 「Create new secret key」をクリック
4. キー名を入力（例：`AI Article Generator`）
5. **表示されたキーをコピー**（二度と表示されません！）

### 3. 設定ファイルの更新

`config/auto_post_config.json`を編集：

```json
{
  "github": {
    "repository": "daito-iwa/ai-article-generator",
    "token": "ここにGitHubトークンを貼り付け",
    "branch": "main"
  },
  "openai": {
    "api_key": "ここにOpenAI APIキーを貼り付け",
    "model": "gpt-4o-mini",
    "temperature": 0.8
  },
  "posting": {
    "daily_posts": 3,
    "post_times": ["09:00", "14:00", "19:00"],
    "categories": ["プログラミング", "AI・機械学習", "ビジネス", "投資・副業", "デザイン"]
  }
}
```

## 🚀 自動投稿の開始

### 仮想環境の有効化
```bash
source venv/bin/activate
```

### プログラムの実行
```bash
python auto_post_to_github.py
```

### メニューから選択
```
1. 今すぐ記事を投稿     # テスト投稿
2. デモ記事を生成（5件） # 初期記事の作成
3. 自動投稿スケジューラーを開始 # ← これを選択！
4. 設定を確認
5. 終了
```

**「3」を選択すると、毎日9:00、14:00、19:00に自動投稿されます！**

## 📝 注意事項

### APIの料金について
- **GitHub**: 無料（レート制限あり）
- **OpenAI**: 有料（gpt-4o-miniは格安）
  - 1記事あたり約$0.01-0.02（1-2円）
  - 1日3記事で月額約$1-2（100-200円）

### 実行を続けるには
- ターミナルを閉じないでください
- またはバックグラウンド実行：
  ```bash
  nohup python auto_post_to_github.py > auto_post.log 2>&1 &
  ```

### 停止方法
- Ctrl+C でプログラムを停止
- バックグラウンド実行の場合：
  ```bash
  ps aux | grep auto_post_to_github
  kill プロセスID
  ```

## 🎯 初回セットアップ推奨手順

1. まず「2」でデモ記事5件を生成
2. GitHub Pagesで表示確認
3. 問題なければ「3」で自動投稿開始

これで完全自動でAI記事が投稿され続けます！