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
        
        // デモデータも即座に表示（JSONがまだ反映されていない場合）
        if (this.articlesData.length === 0) {
            this.articlesData = this.getDemoArticles();
            this.displayArticles();
        }
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

            // ユーザー投稿記事をLocalStorageから読み込み（静的サイト用）
            const userArticles = JSON.parse(localStorage.getItem('published_articles') || '[]');
            if (userArticles.length > 0) {
                // ユーザー記事を既存記事とマージ（重複排除）
                const existingIds = new Set(this.articlesData.map(a => a.id));
                const newUserArticles = userArticles.filter(a => !existingIds.has(a.id));
                
                // 時系列で並び替え（新しい記事が先頭）
                this.articlesData = [...newUserArticles, ...this.articlesData]
                    .sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date));
            }
        } catch (error) {
            console.log('記事データの読み込みに失敗しました。デモデータを使用します。');
            this.articlesData = this.getDemoArticles();
            
            // ユーザー記事も追加
            const userArticles = JSON.parse(localStorage.getItem('published_articles') || '[]');
            this.articlesData = [...userArticles, ...this.articlesData];
        }
    }

    getDemoArticles() {
        // 実際のarticles.jsonと同じデータのみ返す（フォールバック用）
        return [
            {
                id: "auto_1756565303",
                title: "AR/VRの基礎知識と実践方法",
                summary: "AR/VRについて、初心者にも分かりやすく解説します。実践的なテクニックと最新情報をお届けします。",
                author: "M.Y",
                author_role: "ライフスタイル",
                author_avatar: "MY",
                publish_date: "2025-08-30 23:48",
                category: "副業",
                tags: ["AR/VR", "副業", "初心者向け"],
                views: 0,
                likes: 0,
                comments: 0,
                featured: true
            }
        ];
    }

    displayArticles() {
        // トレンド記事を更新
        this.updateTrendingArticles();
        
        // ランキングリストを更新
        this.updateRankingList();
        
        // その他のタブも更新
        this.updateLatestArticles();
        this.updatePopularArticles();
        this.updateAIArticles();
    }

    updateTrendingArticles() {
        const container = document.getElementById('trending');
        if (!container) return;

        if (this.articlesData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-newspaper" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>記事がまだありません</h3>
                    <p>新しい記事をお待ちください。</p>
                </div>
            `;
        } else {
            // 実在する記事を表示
            const html = this.articlesData.map(article => this.createArticleCard(article)).join('');
            container.innerHTML = `<div class="articles-list">${html}</div>`;
        }
    }

    updateRankingList() {
        const container = document.getElementById('ranking-list');
        if (!container) return;

        if (this.articlesData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>記事がありません</p>
                </div>
            `;
        } else {
            const html = this.articlesData.map((article, index) => `
                <a href="./article.html?id=${article.id}" class="ranking-item">
                    <span class="rank">${index + 1}</span>
                    <div class="rank-content">
                        <h4>${article.title}</h4>
                        <span class="rank-stats">新着</span>
                    </div>
                </a>
            `).join('');
            container.innerHTML = html;
        }
    }

    updateLatestArticles() {
        const container = document.getElementById('latest');
        if (!container) return;
        
        if (this.articlesData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clock" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>新着記事がありません</h3>
                    <p>新しい記事の投稿をお待ちください。</p>
                </div>
            `;
        } else {
            // 最新の記事を時系列で表示
            const latestArticles = [...this.articlesData]
                .sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date));
            const html = latestArticles.map(article => this.createArticleCard(article)).join('');
            container.innerHTML = `<div class="articles-list">${html}</div>`;
        }
    }

    updatePopularArticles() {
        const container = document.getElementById('popular');
        if (!container) return;
        
        if (this.articlesData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-star" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>人気記事がありません</h3>
                    <p>記事が増えるまでお待ちください。</p>
                </div>
            `;
        } else {
            // ビュー数でソート（現在は全て0なので投稿日順）
            const popularArticles = [...this.articlesData]
                .sort((a, b) => new Date(b.publish_date) - new Date(a.publish_date));
            const html = popularArticles.map(article => this.createArticleCard(article)).join('');
            container.innerHTML = `<div class="articles-list">${html}</div>`;
        }
    }

    updateAIArticles() {
        const container = document.getElementById('ai-generated');
        if (!container) return;
        
        // AIが生成した記事のみフィルタ
        const aiArticles = this.articlesData.filter(article => article.id.startsWith('auto_'));
        
        if (aiArticles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>AI記事がありません</h3>
                    <p>AI自動生成機能は準備中です。</p>
                </div>
            `;
        } else {
            const html = aiArticles.map(article => {
                const cardHtml = this.createArticleCard(article);
                return cardHtml.replace('<span class="author-role">', '<span class="ai-badge">AI</span><span class="author-role">');
            }).join('');
            container.innerHTML = `<div class="articles-list">${html}</div>`;
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
                                <i class="far fa-heart"></i>
                                <span class="count">${article.likes || 0}</span>
                            </span>
                            <span class="stat">
                                <i class="fas fa-comment"></i>
                                <span class="count">${article.comments || 0}</span>
                            </span>
                            <span class="stat">
                                <i class="fas fa-eye"></i>
                                <span class="count">${article.views > 0 ? this.formatNumber(article.views) : '-'}</span>
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