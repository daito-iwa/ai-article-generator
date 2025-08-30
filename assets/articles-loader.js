// 記事データを動的に読み込むスクリプト

class ArticlesLoader {
    constructor() {
        this.articlesData = [];
        this.init();
    }

    async init() {
        // 記事データを読み込み
        await this.loadArticles();
        
        // 記事を表示
        this.displayArticles();
    }

    async loadArticles() {
        try {
            // GitHub Pages上のJSONファイルを読み込み
            const response = await fetch('./data/articles.json');
            if (response.ok) {
                this.articlesData = await response.json();
            } else {
                // デモデータを使用
                this.articlesData = this.getDemoArticles();
            }
        } catch (error) {
            console.log('記事データの読み込みに失敗しました。デモデータを使用します。');
            this.articlesData = this.getDemoArticles();
        }
    }

    getDemoArticles() {
        // デモ用の記事データ
        return [
            {
                id: "demo_1",
                title: "ChatGPT APIを使った自動記事生成システムを構築してみた",
                summary: "OpenAI APIを使って記事を自動生成するシステムを作成しました。プロンプトエンジニアリングのコツと実装方法を詳しく解説します。",
                author: "T.K",
                author_role: "AIエンジニア",
                author_avatar: "TK",
                publish_date: "2024-08-30 15:30",
                category: "プログラミング",
                tags: ["ChatGPT", "Python", "API"],
                views: 1234,
                likes: 124,
                comments: 23,
                featured: true
            },
            {
                id: "demo_2",
                title: "副業ブログで月10万円達成した完全ロードマップ",
                summary: "ブログ未経験から始めて6ヶ月で月10万円の収益化に成功。実際の収益推移と具体的な施策を全て公開します。",
                author: "M.Y",
                author_role: "ライフスタイル",
                author_avatar: "MY",
                publish_date: "2024-08-30 10:00",
                category: "副業",
                tags: ["ブログ", "副業", "収益化"],
                views: 956,
                likes: 89,
                comments: 15,
                featured: false
            },
            {
                id: "demo_3",
                title: "GitHub Pages + AI自動化で作る無料収益サイト",
                summary: "完全無料でプロ級のWebサイトを構築し、AI自動化で収益化する方法を解説。初期費用0円から月収50万円を目指すテクニック。",
                author: "S.J",
                author_role: "ビジネス",
                author_avatar: "SJ",
                publish_date: "2024-08-29 14:30",
                category: "ビジネス",
                tags: ["GitHub", "AI", "収益化"],
                views: 2100,
                likes: 156,
                comments: 34,
                featured: false
            }
        ];
    }

    displayArticles() {
        // トレンド記事を更新
        this.updateTrendingArticles();
        
        // その他のタブも更新
        this.updateLatestArticles();
        this.updatePopularArticles();
        this.updateAIArticles();
    }

    updateTrendingArticles() {
        const container = document.querySelector('#trending .articles-list');
        if (!container) return;

        // 最初の3記事をトレンドとして表示
        const trendingArticles = this.articlesData.slice(0, 3);
        const html = trendingArticles.map(article => this.createArticleCard(article)).join('');
        container.innerHTML = html;
    }

    updateLatestArticles() {
        // 新着記事の更新（app.jsの既存機能を上書きしないように注意）
        const container = document.querySelector('#latest .articles-list');
        if (!container || container.innerHTML.includes('loading')) return;
        
        // 最新の記事を時系列で表示
        const latestArticles = [...this.articlesData]
            .sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date))
            .slice(0, 6);
            
        if (window.techNoteApp && window.techNoteApp.renderArticles) {
            window.techNoteApp.renderArticles(
                document.getElementById('latest'),
                latestArticles
            );
        }
    }

    updatePopularArticles() {
        // 人気記事の更新
        const container = document.querySelector('#popular .articles-list');
        if (!container || container.innerHTML.includes('loading')) return;
        
        // ビュー数でソート
        const popularArticles = [...this.articlesData]
            .sort((a, b) => b.views - a.views)
            .slice(0, 6);
            
        if (window.techNoteApp && window.techNoteApp.renderArticles) {
            window.techNoteApp.renderArticles(
                document.getElementById('popular'),
                popularArticles
            );
        }
    }

    updateAIArticles() {
        // AI生成記事の更新
        const container = document.querySelector('#ai-generated .articles-list');
        if (!container || container.innerHTML.includes('loading')) return;
        
        // AIが生成した記事のみフィルタ
        const aiArticles = this.articlesData
            .filter(article => article.id.startsWith('auto_'))
            .slice(0, 6);
            
        if (window.techNoteApp && window.techNoteApp.renderArticles) {
            window.techNoteApp.renderArticles(
                document.getElementById('ai-generated'),
                aiArticles.map(article => ({ ...article, isAI: true }))
            );
        }
    }

    createArticleCard(article) {
        const timeAgo = this.getTimeAgo(article.publish_date);
        const featuredClass = article.featured ? 'featured' : '';
        const imageHtml = article.featured ? `
            <div class="article-image">
                <img src="https://via.placeholder.com/300x200?text=AI+Technology" alt="${article.title}">
                <span class="article-badge trending">トレンド</span>
            </div>
        ` : '';

        return `
            <article class="article-card ${featuredClass}">
                ${imageHtml}
                <div class="article-content">
                    <div class="article-meta">
                        <div class="author-info">
                            <img src="https://via.placeholder.com/32x32?text=${article.author_avatar}" alt="${article.author}" class="author-avatar">
                            <span class="author-name">${article.author}</span>
                            <span class="author-role">${article.author_role}</span>
                        </div>
                        <span class="publish-date">${timeAgo}</span>
                    </div>
                    <h3 class="article-title">
                        <a href="./article.html?id=${article.id}">${article.title}</a>
                    </h3>
                    <p class="article-excerpt">${article.summary}</p>
                    <div class="article-footer">
                        <div class="article-tags">
                            ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="article-stats">
                            <span class="stat">
                                <i class="fas fa-heart"></i>
                                ${article.likes}
                            </span>
                            <span class="stat">
                                <i class="fas fa-comment"></i>
                                ${article.comments}
                            </span>
                            <span class="stat">
                                <i class="fas fa-eye"></i>
                                ${this.formatNumber(article.views)}
                            </span>
                        </div>
                    </div>
                </div>
            </article>
        `;
    }

    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 60) {
            return `${minutes}分前`;
        } else if (hours < 24) {
            return `${hours}時間前`;
        } else if (days < 7) {
            return `${days}日前`;
        } else {
            return date.toLocaleDateString('ja-JP');
        }
    }

    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num.toString();
    }

    // 記事詳細ページ用のデータ取得
    getArticleById(id) {
        return this.articlesData.find(article => article.id === id);
    }
}

// グローバルに公開
window.articlesLoader = new ArticlesLoader();

// 定期的に記事を更新（5分ごと）
setInterval(() => {
    window.articlesLoader.loadArticles().then(() => {
        window.articlesLoader.displayArticles();
    });
}, 300000);