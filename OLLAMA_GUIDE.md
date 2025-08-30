# 🚀 Ollama（オーラマ）で完全無料AI記事生成

## Ollamaとは？

**Ollama**は、ChatGPTやClaudeのような高性能AIモデルを**完全無料**で**ローカル環境**で実行できるツールです。

### メリット
- ✅ **完全無料** - API料金なし
- ✅ **高速** - ローカル実行で遅延なし
- ✅ **プライバシー** - データが外部に送信されない
- ✅ **制限なし** - 回数制限・文字数制限なし

## 🔧 簡単セットアップ（5分）

### 方法1: 自動インストール（推奨）
```bash
./install_ollama.sh
```

### 方法2: 手動インストール

#### macOSの場合
```bash
# Homebrewでインストール
brew install ollama

# または公式サイトから
# https://ollama.ai/download
```

#### Linuxの場合
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 📝 記事生成方法

### 1. Ollamaを起動
```bash
ollama serve
```

### 2. モデルをダウンロード（初回のみ）
```bash
# おすすめモデル
ollama pull llama3.2      # 最新・高速（3.8GB）
ollama pull mistral       # バランス良好（4.1GB）
ollama pull gemma2:2b     # 軽量・高速（1.6GB）
```

### 3. 記事を生成

#### 単発生成
```bash
python3 ollama_article_generator.py --keyword "AI ブログ 収益化"
```

#### 複数記事を一括生成
```bash
python3 ollama_article_generator.py --count 5
```

#### モデルを指定
```bash
python3 ollama_article_generator.py --model mistral --keyword "ChatGPT 活用法"
```

## 💰 収益化の仕組み

生成される記事には自動的に以下のアフィリエイトが含まれます：

1. **エックスサーバー** - 1件3,000円
2. **ConoHa WING** - 1件2,500円
3. **ラッコキーワード** - 1件500円

### 収益シミュレーション
- 1日10記事生成
- 月300記事
- 1記事あたり月100PV = 30,000PV
- CTR 1% × CVR 3% = 月9件成約
- 平均単価2,000円 × 9件 = **月18,000円**

## 🚀 実際の使用例

### 例1: トレンド記事の自動生成
```bash
# AIや技術系のトレンド記事を5つ生成
python3 ollama_article_generator.py --count 5
```

### 例2: 特定ジャンルの記事作成
```bash
# 投資系の記事
python3 ollama_article_generator.py --keyword "投資信託 初心者 始め方"

# 副業系の記事
python3 ollama_article_generator.py --keyword "在宅ワーク 副業 稼ぎ方"

# プログラミング系の記事
python3 ollama_article_generator.py --keyword "Python 独学 ロードマップ"
```

### 例3: 長文記事の生成
```bash
# 3000文字の詳細記事
python3 ollama_article_generator.py --keyword "ブログ SEO対策" --length 3000
```

## 📊 モデル比較

| モデル | サイズ | 速度 | 品質 | おすすめ度 |
|--------|--------|------|------|------------|
| llama3.2 | 3.8GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | ★★★★★ |
| mistral | 4.1GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ★★★★☆ |
| gemma2:2b | 1.6GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | ★★★★☆ |
| phi3 | 2.3GB | ⚡⚡⚡ | ⭐⭐⭐ | ★★★☆☆ |

## ⚡ パフォーマンス最適化

### GPUを使用（NVIDIA）
```bash
# GPU使用を確認
ollama run llama3.2 --verbose
```

### メモリ節約モード
```bash
# 小さいモデルを使用
ollama pull gemma2:2b
python3 ollama_article_generator.py --model gemma2:2b
```

## 🔍 トラブルシューティング

### Q: Ollamaが起動しない
```bash
# プロセスを確認
ps aux | grep ollama

# 再起動
pkill ollama
ollama serve
```

### Q: モデルのダウンロードが遅い
```bash
# 軽量モデルから始める
ollama pull phi3
```

### Q: 記事の品質を上げたい
```python
# モデルを変更
python3 ollama_article_generator.py --model mistral
```

## 🎯 今すぐ始める

1. **インストール**（3分）
   ```bash
   ./install_ollama.sh
   ```

2. **テスト記事生成**（1分）
   ```bash
   python3 ollama_article_generator.py --keyword "テスト記事"
   ```

3. **確認**
   ```bash
   ls output/ollama_generated/
   ```

**完全無料**で**制限なし**のAI記事生成を今すぐ始めましょう！

---

💡 **ヒント**: Ollamaは一度セットアップすれば、インターネット接続なしでも動作します。電車の中でも記事生成可能！