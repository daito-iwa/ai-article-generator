// 記事データを動的に読み込むスクリプト

class ArticlesLoader {
    constructor() {
        this.articlesData = [];
        this.currentPage = 1;
        this.articlesPerPage = 10;
        this.init();
    }

    async init() {
        // LocalStorageからテスト記事を削除（一度だけ実行）
        this.cleanupTestArticles();
        
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

            // LocalStorageは無視 - 実際のGitHub記事のみ表示
            // 偽のデモ記事を排除するため、LocalStorageからの読み込みを完全に無効化
        } catch (error) {
            console.log('記事データの読み込みに失敗しました。デモデータを使用します。');
            this.articlesData = this.getDemoArticles();
            
            // LocalStorageは無視 - 実際のGitHub記事のみ表示
        }
    }

    getDemoArticles() {
        // フォールバック用 - 空の配列を返してLocalStorageの干渉を防ぐ
        // 実際のデータはGitHub articles.jsonから読み込む
        return [];
    }

    cleanupTestArticles() {
        // テスト記事のタイトルリスト（完全に削除対象）
        const testTitles = [
            'React 18の新機能Concurrent Featuresを深掘り',
            'Docker Composeで開発環境を劇的に改善する方法', 
            'TypeScript 5.0で変わった型システムの新機能',
            'ChatGPT APIを使った自動記事生成システムを構築してみた'
        ];
        
        // テスト記事の作者名（すべて偽の作者）
        const testAuthors = ['T.K', 'K.H', 'A.M'];
        
        try {
            // published_articlesを完全にクリア（静的サイトのためLocalStorageは不要）
            const articles = JSON.parse(localStorage.getItem('published_articles') || '[]');
            const originalLength = articles.length;
            
            // 実際のGitHub記事IDパターンに合致しない記事をすべて削除
            const realArticles = articles.filter(article => {
                // GitHub Actions生成記事のみ保持（IDがauto_で始まる実際のもの）
                const isRealGitHubArticle = article.id && article.id.startsWith('auto_') && 
                                          !testTitles.includes(article.title) &&
                                          !testAuthors.includes(article.author);
                return isRealGitHubArticle && article.user_generated === true;
            });
            
            // LocalStorageを更新（実質的にほぼクリア）
            localStorage.setItem('published_articles', JSON.stringify(realArticles));
            
            if (originalLength > realArticles.length) {
                console.log(`LocalStorageから${originalLength - realArticles.length}件のテスト記事を削除しました`);
            }
            
            // デモンストレーション用のダミーデータもクリア
            if (localStorage.getItem('demo_articles')) {
                localStorage.removeItem('demo_articles');
                console.log('デモ記事データを削除しました');
            }
            
        } catch (error) {
            console.log('LocalStorageのクリーンアップに失敗:', error);
            // エラーの場合は完全にクリア
            localStorage.removeItem('published_articles');
            localStorage.removeItem('demo_articles');
        }
    }

    displayArticles() {
        // 新着記事を更新（メイン）
        this.updateLatestArticles();
        
        // トレンド記事を更新（エンゲージメントベース）
        this.updateTrendingArticles();
        
        // ランキングリストを更新
        this.updateRankingList();
        
        // その他のタブも更新
        this.updatePopularArticles();
        this.updateAIArticles();
    }

    updateTrendingArticles() {
        const container = document.getElementById('trending');
        if (!container) return;

        if (this.articlesData.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-fire" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                    <h3>トレンド記事がありません</h3>
                    <p>記事のエンゲージメントが蓄積されるとトレンドが表示されます。</p>
                </div>
            `;
        } else {
            // エンゲージメントスコアでソート（views + likes * 3 + comments * 5）
            const trendingArticles = [...this.articlesData]
                .map(article => ({
                    ...article,
                    engagementScore: (article.views || 0) + (article.likes || 0) * 3 + (article.comments || 0) * 5
                }))
                .sort((a, b) => {
                    // エンゲージメントスコアが同じ場合は新しい記事を優先
                    if (b.engagementScore === a.engagementScore) {
                        return new Date(b.publish_date) - new Date(a.publish_date);
                    }
                    return b.engagementScore - a.engagementScore;
                })
                .filter(article => article.engagementScore > 0 || this.articlesData.length <= 5); // 記事が少ない場合は全て表示
            
            if (trendingArticles.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-fire" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                        <h3>トレンド記事を準備中</h3>
                        <p>記事への反応（いいね・コメント・ビュー）が増えるとトレンドとして表示されます。</p>
                    </div>
                `;
            } else {
                // ページング処理
                const startIndex = (this.currentPage - 1) * this.articlesPerPage;
                const endIndex = startIndex + this.articlesPerPage;
                const currentArticles = trendingArticles.slice(startIndex, endIndex);
                
                const html = currentArticles.map(article => this.createArticleCard(article)).join('');
                
                // ページネーションを追加
                const totalPages = Math.ceil(trendingArticles.length / this.articlesPerPage);
                const paginationHtml = this.createPagination(totalPages);
                
                container.innerHTML = `
                    <div class="articles-list">${html}</div>
                    ${paginationHtml}
                `;
            }
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
            container.innerHTML = `
                <div class="articles-list">${html}</div>
                <div class="articles-info">
                    <p style="text-align: center; color: #666; margin-top: 30px;">
                        現在${this.articlesData.length}件の記事があります。<br>
                        毎日17:00、23:00、翌朝5:00に新記事が自動投稿されます！
                    </p>
                </div>
            `;
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
            // エンゲージメント（ビュー数・いいね・コメント）でソート
            const popularArticles = [...this.articlesData]
                .sort((a, b) => {
                    const scoreA = (a.views || 0) + (a.likes || 0) * 2 + (a.comments || 0) * 3;
                    const scoreB = (b.views || 0) + (b.likes || 0) * 2 + (b.comments || 0) * 3;
                    
                    // スコアが同じ場合は投稿日順
                    if (scoreB === scoreA) {
                        return new Date(b.publish_date) - new Date(a.publish_date);
                    }
                    return scoreB - scoreA;
                })
                .filter(article => {
                    // エンゲージメントがある記事のみ、または記事が少ない場合は全て表示
                    const score = (article.views || 0) + (article.likes || 0) + (article.comments || 0);
                    return score > 0 || this.articlesData.length <= 5;
                });
            
            if (popularArticles.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-star" style="font-size: 3em; color: #ccc; margin-bottom: 20px;"></i>
                        <h3>人気記事を準備中</h3>
                        <p>記事へのいいねやコメントが増えると人気記事として表示されます。</p>
                    </div>
                `;
            } else {
                const html = popularArticles.map(article => this.createArticleCard(article)).join('');
                container.innerHTML = `<div class="articles-list">${html}</div>`;
            }
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
        // UTC時刻として解釈し、日本時間（+9時間）に変換
        const utcDate = new Date(dateString + ' UTC');
        const jstDate = new Date(utcDate.getTime() + (9 * 60 * 60 * 1000));
        const now = new Date();
        const diff = now - jstDate;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 60) {
            if (minutes <= 0) return '今';
            return `${minutes}分前`;
        } else if (hours < 24) {
            return `${hours}時間前`;
        } else if (days < 7) {
            return `${days}日前`;
        } else {
            return jstDate.toLocaleDateString('ja-JP');
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
    
    // ページネーション作成
    createPagination(totalPages) {
        if (totalPages <= 1) return '';
        
        let paginationHtml = '<div class="pagination">';
        
        // 前へボタン
        if (this.currentPage > 1) {
            paginationHtml += `<button class="page-btn" onclick="window.articlesLoader.changePage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i> 前へ
            </button>`;
        }
        
        // ページ番号
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHtml += `<span class="page-num active">${i}</span>`;
            } else {
                paginationHtml += `<button class="page-num" onclick="window.articlesLoader.changePage(${i})">${i}</button>`;
            }
        }
        
        // 次へボタン
        if (this.currentPage < totalPages) {
            paginationHtml += `<button class="page-btn" onclick="window.articlesLoader.changePage(${this.currentPage + 1})">
                次へ <i class="fas fa-chevron-right"></i>
            </button>`;
        }
        
        paginationHtml += '</div>';
        
        // 記事数表示
        const start = (this.currentPage - 1) * this.articlesPerPage + 1;
        const end = Math.min(this.currentPage * this.articlesPerPage, this.articlesData.length);
        paginationHtml += `<div class="articles-count">全${this.articlesData.length}件中 ${start}-${end}件を表示</div>`;
        
        return paginationHtml;
    }
    
    // ページ変更
    changePage(page) {
        this.currentPage = page;
        this.displayArticles();
        window.scrollTo(0, 0);
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