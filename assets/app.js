// TechNote - メインJavaScriptファイル

class TechNoteApp {
    constructor() {
        this.currentTab = 'trending';
        this.articlesData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadArticles();
        this.setupAdSense();
        this.animateStats();
    }

    setupEventListeners() {
        // タブ切り替え
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // 検索機能
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('search-input');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
        }

        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(e.target.value);
                }
            });
        }

        // いいね機能
        document.addEventListener('click', (e) => {
            if (e.target.closest('.stat')) {
                const statElement = e.target.closest('.stat');
                if (statElement.querySelector('.fa-heart')) {
                    this.toggleLike(statElement);
                }
            }
        });

        // 記事カードのクリック機能
        document.addEventListener('click', (e) => {
            const articleCard = e.target.closest('.article-card');
            const articleLink = e.target.closest('a');
            
            // リンクがクリックされた場合はそのまま遷移
            if (articleLink) {
                return true;
            }
            
            // 記事カード全体がクリックされた場合
            if (articleCard && !e.target.closest('.article-stats')) {
                const titleLink = articleCard.querySelector('.article-title a');
                if (titleLink) {
                    window.location.href = titleLink.href;
                }
            }
        });

        // スムーズスクロール
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    switchTab(tabId) {
        // アクティブなタブボタンを更新
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // アクティブなタブコンテンツを更新
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');

        this.currentTab = tabId;
        this.loadTabContent(tabId);
    }

    async loadTabContent(tabId) {
        const tabContent = document.getElementById(tabId);
        
        if (tabId === 'trending') {
            return; // 既にHTMLに含まれているのでスキップ
        }

        // ローディング表示
        tabContent.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                ${this.getLoadingMessage(tabId)}
            </div>
        `;

        // 遅延を追加してリアルな読み込み感を演出
        await this.delay(800);

        // タブ別のコンテンツを生成
        const articles = this.generateArticlesForTab(tabId);
        this.renderArticles(tabContent, articles);
    }

    generateArticlesForTab(tabId) {
        const articlesData = {
            latest: [
                {
                    id: 4,
                    title: "React 18の新機能Concurrent Featuresを深掘り",
                    excerpt: "React 18で導入されたConcurrent Featuresについて、実際のコード例とともに詳しく解説します。パフォーマンス向上のポイントも...",
                    author: { name: "T.K", role: "エンジニア", avatar: "TK" },
                    publishDate: "30分前",
                    tags: ["React", "JavaScript", "フロントエンド"],
                    stats: { likes: 45, comments: 8, views: 234 },
                    featured: false
                },
                {
                    id: 5,
                    title: "Docker Composeで開発環境を劇的に改善する方法",
                    excerpt: "複雑なマイクロサービス環境もDocker Composeで簡単に構築。実際のプロジェクトでの活用例を交えて解説します...",
                    author: { name: "K.H", role: "DevOps", avatar: "KH" },
                    publishDate: "1時間前",
                    tags: ["Docker", "DevOps", "開発環境"],
                    stats: { likes: 67, comments: 12, views: 445 },
                    featured: false
                },
                {
                    id: 6,
                    title: "TypeScript 5.0で変わった型システムの新機能",
                    excerpt: "TypeScript 5.0の新機能を実際のコードで体験。型安全性がさらに向上し、開発体験も大幅に改善されました...",
                    author: { name: "A.M", role: "フロントエンド", avatar: "AM" },
                    publishDate: "2時間前",
                    tags: ["TypeScript", "型システム", "JavaScript"],
                    stats: { likes: 89, comments: 15, views: 567 },
                    featured: true
                }
            ],
            popular: [
                {
                    id: 7,
                    title: "ChatGPT APIで作る高度なチャットボットシステム",
                    excerpt: "OpenAI APIを使用してビジネス級のチャットボットを構築。自然言語処理とコンテキスト管理の実装方法を詳しく解説...",
                    author: { name: "S.J", role: "AI エンジニア", avatar: "SJ" },
                    publishDate: "3日前",
                    tags: ["ChatGPT", "AI", "Python"],
                    stats: { likes: 234, comments: 45, views: 3200 },
                    featured: true
                },
                {
                    id: 8,
                    title: "GitHub Actionsで作るCI/CD完全自動化",
                    excerpt: "GitHub Actionsを使った本格的なCI/CDパイプライン構築。テスト、ビルド、デプロイまで完全自動化を実現...",
                    author: { name: "M.Y", role: "DevOps", avatar: "MY" },
                    publishDate: "5日前",
                    tags: ["GitHub", "CI/CD", "自動化"],
                    stats: { likes: 187, comments: 32, views: 2800 },
                    featured: false
                },
                {
                    id: 9,
                    title: "Vue.js 3 + TypeScriptで作るモダンWebアプリ",
                    excerpt: "Vue.js 3の Composition API と TypeScript を組み合わせた開発手法。実際のプロジェクト構成と実装例...",
                    author: { name: "R.N", role: "フロントエンド", avatar: "RN" },
                    publishDate: "1週間前",
                    tags: ["Vue.js", "TypeScript", "モダン開発"],
                    stats: { likes: 156, comments: 28, views: 2100 },
                    featured: false
                }
            ],
            "ai-generated": [
                {
                    id: 10,
                    title: "【AI生成】最新のJavaScript動向レポート 2024",
                    excerpt: "AI技術を使って最新のJavaScript生態系を分析。フレームワークの動向、新しいライブラリ、コミュニティの変化をレポート...",
                    author: { name: "AI Reporter", role: "AI", avatar: "AI" },
                    publishDate: "6時間前",
                    tags: ["JavaScript", "AI生成", "技術動向"],
                    stats: { likes: 78, comments: 16, views: 890 },
                    featured: false,
                    isAI: true
                },
                {
                    id: 11,
                    title: "【AI生成】Python機械学習ライブラリ比較分析",
                    excerpt: "AIが分析するPython機械学習ライブラリの性能比較。scikit-learn、TensorFlow、PyTorchの特徴と使い分け...",
                    author: { name: "ML Assistant", role: "AI", avatar: "ML" },
                    publishDate: "8時間前",
                    tags: ["Python", "機械学習", "AI生成"],
                    stats: { likes: 92, comments: 21, views: 1100 },
                    featured: true,
                    isAI: true
                },
                {
                    id: 12,
                    title: "【AI生成】クラウドサービス最適化ガイド",
                    excerpt: "AI技術による自動分析で、AWS・Azure・GCPの最適な使い分け方法を提案。コスト削減と性能向上の両立を実現...",
                    author: { name: "Cloud AI", role: "AI", avatar: "CL" },
                    publishDate: "12時間前",
                    tags: ["クラウド", "AWS", "AI生成"],
                    stats: { likes: 65, comments: 11, views: 723 },
                    featured: false,
                    isAI: true
                }
            ]
        };

        return articlesData[tabId] || [];
    }

    renderArticles(container, articles) {
        const articlesHtml = articles.map(article => this.generateArticleCard(article)).join('');
        
        container.innerHTML = `
            <div class="articles-list">
                ${articlesHtml}
            </div>
        `;
    }

    generateArticleCard(article) {
        const featuredClass = article.featured ? 'featured' : '';
        const aiLabel = article.isAI ? '<span class="ai-badge">AI</span>' : '';
        const badgeHtml = article.featured ? '<span class="article-badge trending">注目</span>' : '';
        
        return `
            <article class="article-card ${featuredClass}">
                ${article.image ? `
                    <div class="article-image">
                        <img src="${article.image}" alt="${article.title}">
                        ${badgeHtml}
                    </div>
                ` : ''}
                <div class="article-content">
                    <div class="article-meta">
                        <div class="author-info">
                            <img src="https://via.placeholder.com/32x32?text=${article.author.avatar}" alt="${article.author.name}" class="author-avatar">
                            <span class="author-name">${article.author.name}</span>
                            <span class="author-role">${article.author.role}</span>
                            ${aiLabel}
                        </div>
                        <span class="publish-date">${article.publishDate}</span>
                    </div>
                    <h3 class="article-title">
                        <a href="./article.html?id=${article.id}">${article.title}</a>
                    </h3>
                    <p class="article-excerpt">${article.excerpt}</p>
                    <div class="article-footer">
                        <div class="article-tags">
                            ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="article-stats">
                            <span class="stat" data-article-id="${article.id}">
                                <i class="far fa-heart"></i>
                                <span class="count">0</span>
                            </span>
                            <span class="stat">
                                <i class="fas fa-comment"></i>
                                <span class="count">0</span>
                            </span>
                            <span class="stat">
                                <i class="fas fa-eye"></i>
                                <span class="count">-</span>
                            </span>
                        </div>
                    </div>
                </div>
            </article>
        `;
    }

    getLoadingMessage(tabId) {
        const messages = {
            latest: '新着記事を読み込み中...',
            popular: '人気記事を読み込み中...',
            'ai-generated': 'AI生成記事を読み込み中...'
        };
        return messages[tabId] || '記事を読み込み中...';
    }

    async loadArticles() {
        // 記事データの初期化（実際の実装ではAPIから取得）
        this.articlesData = {
            trending: [], // HTMLに既に含まれている
            latest: [],
            popular: [],
            'ai-generated': []
        };
    }

    performSearch(query) {
        if (!query.trim()) return;
        
        console.log('検索実行:', query);
        
        // 検索結果ページへのリダイレクト（実際の実装）
        // window.location.href = `search.html?q=${encodeURIComponent(query)}`;
        
        // デモ用のアラート
        alert(`"${query}" の検索結果を表示します（実装予定）`);
    }

    toggleLike(statElement) {
        const articleId = statElement.dataset.articleId;
        const likeCountSpan = statElement.textContent.trim();
        const currentCount = parseInt(likeCountSpan);
        
        // いいねの状態を切り替え
        const heartIcon = statElement.querySelector('.fa-heart');
        const isLiked = heartIcon.classList.contains('fas');
        
        if (isLiked) {
            heartIcon.classList.remove('fas');
            heartIcon.classList.add('far');
            statElement.innerHTML = `<i class="far fa-heart"></i> ${currentCount - 1}`;
            statElement.classList.remove('liked');
        } else {
            heartIcon.classList.remove('far');
            heartIcon.classList.add('fas');
            statElement.innerHTML = `<i class="fas fa-heart"></i> ${currentCount + 1}`;
            statElement.classList.add('liked');
            
            // いいねアニメーション
            this.animateLike(statElement);
        }
        
        // localStorage にいいねの状態を保存
        this.saveLikeStatus(articleId, !isLiked);
    }

    animateLike(element) {
        element.style.transform = 'scale(1.2)';
        element.style.color = '#ff6b6b';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 200);
    }

    saveLikeStatus(articleId, isLiked) {
        const likedArticles = JSON.parse(localStorage.getItem('likedArticles') || '{}');
        likedArticles[articleId] = isLiked;
        localStorage.setItem('likedArticles', JSON.stringify(likedArticles));
    }

    loadLikeStatus() {
        const likedArticles = JSON.parse(localStorage.getItem('likedArticles') || '{}');
        
        Object.keys(likedArticles).forEach(articleId => {
            if (likedArticles[articleId]) {
                const statElement = document.querySelector(`[data-article-id="${articleId}"]`);
                if (statElement) {
                    statElement.classList.add('liked');
                    const heartIcon = statElement.querySelector('.fa-heart');
                    if (heartIcon) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                    }
                }
            }
        });
    }

    animateStats() {
        // ページロード時に統計数値をアニメーション
        const stats = [
            { id: 'total-articles', target: 1247 },
            { id: 'total-users', target: 389 },
            { id: 'daily-views', target: 15200, suffix: 'k', divisor: 1000 }
        ];

        stats.forEach(stat => {
            const element = document.getElementById(stat.id);
            if (element) {
                this.countUp(element, stat.target, stat.suffix, stat.divisor);
            }
        });
    }

    countUp(element, target, suffix = '', divisor = 1) {
        let current = 0;
        const increment = target / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            const displayValue = divisor > 1 ? 
                (current / divisor).toFixed(1) + suffix : 
                Math.floor(current).toLocaleString();
            
            element.textContent = displayValue;
        }, 20);
    }

    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num.toString();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    setupAdSense() {
        // AdSense広告の遅延読み込み
        const ads = document.querySelectorAll('.adsbygoogle');
        
        if ('IntersectionObserver' in window) {
            const adObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        try {
                            (adsbygoogle = window.adsbygoogle || []).push({});
                        } catch (e) {
                            console.log('AdSense読み込みエラー:', e);
                        }
                        adObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            ads.forEach(ad => {
                adObserver.observe(ad);
            });
        }
    }
}

// DOMが読み込まれたらアプリを初期化
document.addEventListener('DOMContentLoaded', () => {
    window.techNoteApp = new TechNoteApp();
});

// CSS追加スタイル
const additionalCSS = `
    .ai-badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 0.7em;
        font-weight: bold;
        margin-left: 5px;
    }
    
    .stat.liked {
        color: #ff6b6b;
    }
    
    .stat {
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .stat:hover {
        transform: translateY(-1px);
    }
`;

// 動的にCSSを追加
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);