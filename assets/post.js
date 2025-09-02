// 記事投稿ページのJavaScript

class PostEditor {
    constructor() {
        this.editor = null;
        this.isPreviewMode = false;
        this.currentDraft = null;
        this.autoSaveInterval = null;
        this.init();
    }

    init() {
        this.setupEditor();
        this.setupEventListeners();
        this.setupAutoSave();
        this.loadDraft();
        this.initializeCharacterCounters();
    }

    setupEditor() {
        const textarea = document.getElementById('markdown-editor');
        
        // CodeMirrorエディタを初期化
        this.editor = CodeMirror.fromTextArea(textarea, {
            mode: 'markdown',
            theme: 'github',
            lineNumbers: true,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            placeholder: 'こちらにMarkdownで記事の内容を書いてください...',
            extraKeys: {
                'Ctrl-S': () => this.saveDraft(),
                'Cmd-S': () => this.saveDraft(),
                'Ctrl-P': () => this.togglePreview(),
                'Cmd-P': () => this.togglePreview()
            }
        });

        // エディタの変更を監視
        this.editor.on('change', () => {
            this.updateCounters();
            this.updatePreview();
        });

        // エディタのスタイリング
        this.editor.getWrapperElement().style.height = '460px';
        this.editor.getWrapperElement().style.border = 'none';
        this.editor.getWrapperElement().style.fontSize = '14px';
    }

    setupEventListeners() {
        // タブ切り替え
        document.querySelectorAll('.editor-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabType = e.currentTarget.dataset.tab;
                this.switchTab(tabType);
            });
        });

        // ツールバー
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.executeToolAction(action);
            });
        });

        // フォーム送信
        const form = document.getElementById('article-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.publishArticle();
        });

        // 下書き保存
        document.getElementById('save-draft-btn').addEventListener('click', () => {
            this.saveDraft();
        });

        document.getElementById('save-draft').addEventListener('click', () => {
            this.saveDraft();
        });

        // 文字数カウンター
        document.getElementById('article-title').addEventListener('input', this.updateTitleCounter);
        document.getElementById('article-summary').addEventListener('input', this.updateSummaryCounter);

        // プレビューモード切り替え
        document.getElementById('preview-toggle').addEventListener('click', () => {
            this.togglePreview();
        });

        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveDraft();
            }
        });
    }

    switchTab(tabType) {
        // タブボタンの状態更新
        document.querySelectorAll('.editor-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabType}"]`).classList.add('active');

        // パネルの表示切り替え
        document.querySelectorAll('.editor-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        if (tabType === 'editor') {
            document.getElementById('editor-panel').classList.add('active');
            this.isPreviewMode = false;
            setTimeout(() => this.editor.refresh(), 100);
        } else if (tabType === 'preview') {
            document.getElementById('preview-panel').classList.add('active');
            this.isPreviewMode = true;
            this.updatePreview();
        }
    }

    executeToolAction(action) {
        const cursor = this.editor.getCursor();
        const selectedText = this.editor.getSelection();
        let insertText = '';
        let cursorOffset = 0;

        switch (action) {
            case 'bold':
                insertText = selectedText ? `**${selectedText}**` : '**太字**';
                cursorOffset = selectedText ? 0 : -2;
                break;
            case 'italic':
                insertText = selectedText ? `*${selectedText}*` : '*斜体*';
                cursorOffset = selectedText ? 0 : -1;
                break;
            case 'heading':
                insertText = selectedText ? `## ${selectedText}` : '## 見出し';
                cursorOffset = selectedText ? 0 : -2;
                break;
            case 'link':
                insertText = selectedText ? `[${selectedText}](URL)` : '[リンクテキスト](URL)';
                cursorOffset = selectedText ? -4 : -13;
                break;
            case 'image':
                insertText = '![画像の説明](画像URL)';
                cursorOffset = -6;
                break;
            case 'code':
                if (selectedText.includes('\\n')) {
                    insertText = `\\`\\`\\`\\n${selectedText}\\n\\`\\`\\``;
                } else {
                    insertText = selectedText ? `\`${selectedText}\`` : '`コード`';
                    cursorOffset = selectedText ? 0 : -1;
                }
                break;
            case 'list':
                insertText = selectedText ? `- ${selectedText}` : '- リスト項目';
                cursorOffset = selectedText ? 0 : -4;
                break;
            case 'quote':
                insertText = selectedText ? `> ${selectedText}` : '> 引用文';
                cursorOffset = selectedText ? 0 : -3;
                break;
        }

        if (selectedText) {
            this.editor.replaceSelection(insertText);
        } else {
            this.editor.replaceRange(insertText, cursor);
            if (cursorOffset !== 0) {
                const newPos = {
                    line: cursor.line,
                    ch: cursor.ch + insertText.length + cursorOffset
                };
                this.editor.setCursor(newPos);
            }
        }

        this.editor.focus();
    }

    updatePreview() {
        if (!this.isPreviewMode) return;
        
        const markdownContent = this.editor.getValue();
        const previewContent = document.getElementById('preview-content');
        
        if (markdownContent.trim()) {
            previewContent.innerHTML = marked.parse(markdownContent);
        } else {
            previewContent.innerHTML = '<p class="preview-placeholder">プレビューするコンテンツがありません。エディタに内容を入力してください。</p>';
        }
    }

    updateCounters() {
        const content = this.editor.getValue();
        document.getElementById('content-count').textContent = content.length;
        document.getElementById('line-count').textContent = this.editor.lineCount();
    }

    updateTitleCounter() {
        const title = this.value;
        document.getElementById('title-count').textContent = title.length;
        
        const counter = document.getElementById('title-count');
        if (title.length > 90) {
            counter.style.color = '#ff6b6b';
        } else {
            counter.style.color = '#999';
        }
    }

    updateSummaryCounter() {
        const summary = this.value;
        document.getElementById('summary-count').textContent = summary.length;
        
        const counter = document.getElementById('summary-count');
        if (summary.length > 150) {
            counter.style.color = '#ff6b6b';
        } else {
            counter.style.color = '#999';
        }
    }

    initializeCharacterCounters() {
        this.updateCounters();
    }

    togglePreview() {
        const currentTab = document.querySelector('.editor-tab.active').dataset.tab;
        if (currentTab === 'editor') {
            this.switchTab('preview');
        } else {
            this.switchTab('editor');
        }
    }

    // 下書き保存機能
    saveDraft() {
        const formData = this.getFormData();
        localStorage.setItem('article-draft', JSON.stringify({
            ...formData,
            savedAt: new Date().toISOString()
        }));
        
        this.showMessage('下書きを保存しました', 'success');
    }

    loadDraft() {
        const draft = localStorage.getItem('article-draft');
        if (draft) {
            try {
                const draftData = JSON.parse(draft);
                
                // 確認ダイアログ
                if (confirm('保存された下書きがあります。復元しますか？')) {
                    this.restoreDraft(draftData);
                }
            } catch (e) {
                console.error('下書きの読み込みに失敗しました:', e);
            }
        }
    }

    restoreDraft(draftData) {
        document.getElementById('article-title').value = draftData.title || '';
        document.getElementById('article-summary').value = draftData.summary || '';
        document.getElementById('article-category').value = draftData.category || '';
        document.getElementById('article-tags').value = draftData.tags || '';
        document.getElementById('author-name').value = draftData.author || '';
        
        if (this.editor && draftData.content) {
            this.editor.setValue(draftData.content);
        }
        
        this.updateCounters();
        this.showMessage('下書きを復元しました', 'success');
    }

    setupAutoSave() {
        // 30秒ごとに自動保存
        this.autoSaveInterval = setInterval(() => {
            const formData = this.getFormData();
            if (formData.title || formData.content) {
                this.saveDraft();
            }
        }, 30000);
    }

    getFormData() {
        return {
            title: document.getElementById('article-title').value.trim(),
            summary: document.getElementById('article-summary').value.trim(),
            category: document.getElementById('article-category').value,
            tags: document.getElementById('article-tags').value.trim(),
            author: document.getElementById('author-name').value.trim(),
            content: this.editor ? this.editor.getValue() : '',
            allowComments: document.getElementById('allow-comments').checked,
            publishImmediately: document.getElementById('publish-immediately').checked,
            seoOptimize: document.getElementById('seo-optimize').checked
        };
    }

    validateForm(formData) {
        const errors = [];

        if (!formData.title) {
            errors.push('記事タイトルは必須です');
        } else if (formData.title.length > 100) {
            errors.push('タイトルは100文字以内で入力してください');
        }

        if (!formData.author) {
            errors.push('著者名は必須です');
        }

        if (!formData.category) {
            errors.push('カテゴリを選択してください');
        }

        if (!formData.content || formData.content.trim().length < 100) {
            errors.push('記事の内容は100文字以上で入力してください');
        }

        if (formData.summary && formData.summary.length > 160) {
            errors.push('概要は160文字以内で入力してください');
        }

        return errors;
    }

    async publishArticle() {
        this.showLoadingOverlay('記事を公開しています...');
        
        try {
            const formData = this.getFormData();
            const errors = this.validateForm(formData);
            
            if (errors.length > 0) {
                this.hideLoadingOverlay();
                this.showMessage(errors.join('<br>'), 'error');
                return;
            }

            // TODO: GitHub Issues APIに投稿
            await this.submitToGitHub(formData);
            
            // 成功処理
            localStorage.removeItem('article-draft');
            this.showMessage('記事が公開されました！', 'success');
            
            setTimeout(() => {
                window.location.href = './index.html';
            }, 2000);
            
        } catch (error) {
            console.error('記事の公開に失敗しました:', error);
            this.showMessage('記事の公開に失敗しました。もう一度お試しください。', 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    async submitToGitHub(formData) {
        // 記事データを作成
        const article = {
            title: formData.title,
            summary: formData.summary || `${formData.title}について、詳しく解説します。`,
            content: formData.content,
            tags: Utils.normalizeTags(formData.tags),
            category: this.getCategoryName(formData.category),
            author: formData.author,
            author_role: "寄稿者",
            author_avatar: formData.author.split(' ').map(n => n[0]).join('').toUpperCase(),
            publish_date: new Date().toISOString().slice(0, 16).replace('T', ' '),
            id: `user_${Date.now()}`,
            views: 0,
            likes: 0,
            comments: 0,
            user_generated: true
        };

        // 既存記事を読み込み
        let articles = [];
        try {
            const response = await fetch('./data/articles.json');
            if (response.ok) {
                articles = await response.json();
            }
        } catch (error) {
            console.warn('既存記事の読み込みに失敗しました:', error);
        }

        // 新しい記事を追加
        articles.unshift(article);

        // LocalStorageに保存（静的サイトのため）
        localStorage.setItem('user_articles', JSON.stringify(articles));
        
        // 公開記事リストにも追加
        let publishedArticles = JSON.parse(localStorage.getItem('published_articles') || '[]');
        publishedArticles.unshift(article);
        localStorage.setItem('published_articles', JSON.stringify(publishedArticles));

        console.log('記事を公開しました:', article);
        return Promise.resolve(article);
    }

    getCategoryName(categoryValue) {
        const categoryMap = {
            'programming': 'プログラミング',
            'ai': 'AI・機械学習',
            'business': 'ビジネス',
            'design': 'デザイン',
            'lifestyle': 'ライフスタイル',
            'finance': '投資・副業',
            'career': 'キャリア',
            'other': 'その他'
        };
        return categoryMap[categoryValue] || 'その他';
    }

    showMessage(message, type) {
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            <span>${message}</span>
        `;

        const form = document.querySelector('.article-form');
        form.insertBefore(messageDiv, form.firstChild);

        // 5秒後に自動削除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    showLoadingOverlay(message) {
        let overlay = document.querySelector('.loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>${message}</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    hideLoadingOverlay() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // クリーンアップ
    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.postEditor = new PostEditor();

    // ページを離れる前の確認
    window.addEventListener('beforeunload', (e) => {
        const formData = window.postEditor.getFormData();
        if (formData.title || formData.content) {
            const message = '編集中の内容が失われる可能性があります。ページを離れますか？';
            e.returnValue = message;
            return message;
        }
    });
});

// Markdownヘルパー関数
const MarkdownHelper = {
    // テーブル生成
    createTable: (rows = 3, cols = 3) => {
        let table = '';
        for (let i = 0; i <= rows; i++) {
            let row = '|';
            for (let j = 0; j < cols; j++) {
                if (i === 0) {
                    row += ` Header ${j + 1} |`;
                } else if (i === 1) {
                    row += ' --- |';
                } else {
                    row += ` Cell ${i},${j + 1} |`;
                }
            }
            table += row + '\\n';
        }
        return table;
    },

    // チェックリスト生成
    createChecklist: (items) => {
        return items.map(item => `- [ ] ${item}`).join('\\n');
    },

    // コードブロック生成
    createCodeBlock: (language, code) => {
        return `\`\`\`${language}\\n${code}\\n\`\`\``;
    }
};

// 追加のユーティリティ関数
const Utils = {
    // 文字数カウント（日本語対応）
    countChars: (text) => {
        return text.length;
    },

    // 読了時間計算（日本語: 400文字/分）
    calculateReadingTime: (text) => {
        const charCount = Utils.countChars(text);
        const minutes = Math.ceil(charCount / 400);
        return `${minutes}分で読める`;
    },

    // タグの正規化
    normalizeTags: (tagString) => {
        return tagString
            .split(/[,，、]/)
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0)
            .slice(0, 10); // 最大10個
    },

    // URLの検証
    isValidUrl: (string) => {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
};