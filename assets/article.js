// 記事詳細ページ専用JavaScript

class ArticlePageApp {
    constructor() {
        this.init();
    }

    async init() {
        // 記事データを読み込み
        await this.loadArticleData();
        
        this.setupEventListeners();
        this.setupCodeCopyButtons();
        this.setupTableOfContents();
        this.setupCommentSystem();
        this.setupArticleActions();
        this.loadLikedStatus();
    }

    async loadArticleData() {
        const urlParams = new URLSearchParams(window.location.search);
        const articleId = urlParams.get('id');
        
        if (!articleId) {
            this.showError('記事IDが指定されていません。');
            return;
        }

        try {
            // articles.jsonからデータを読み込み
            const response = await fetch('./data/articles.json');
            if (!response.ok) {
                throw new Error('記事データの読み込みに失敗しました');
            }
            
            const articlesData = await response.json();
            const article = articlesData.find(a => a.id === articleId);
            
            if (!article) {
                this.showError('指定された記事が見つかりません。');
                return;
            }
            
            this.renderArticle(article);
            
        } catch (error) {
            console.error('記事読み込みエラー:', error);
            this.showError('記事の読み込みに失敗しました。');
        }
    }

    renderArticle(article) {
        // タイトルとメタデータを更新
        document.title = `${article.title} - TechNote`;
        document.getElementById('article-title').textContent = article.title;
        document.getElementById('article-description').setAttribute('content', article.summary);

        // 記事コンテンツを更新
        const articleContainer = document.querySelector('.article-container');
        if (articleContainer) {
            articleContainer.innerHTML = `
                <article class="article">
                    <header class="article-header">
                        <div class="article-category">
                            <span class="category-tag">${article.category}</span>
                        </div>
                        <h1 class="article-title">${article.title}</h1>
                        <div class="article-meta">
                            <div class="author-info">
                                <img src="https://via.placeholder.com/48x48?text=${article.author_avatar}" alt="${article.author}" class="author-avatar">
                                <div class="author-details">
                                    <span class="author-name">${article.author}</span>
                                    <span class="author-role">${article.author_role}</span>
                                    <time class="publish-date">${this.formatDate(article.publish_date)}</time>
                                </div>
                            </div>
                            <div class="article-stats">
                                <span class="stat">
                                    <i class="fas fa-eye"></i>
                                    ${article.views || 0}
                                </span>
                                <span class="stat" data-article-id="${article.id}">
                                    <i class="far fa-heart"></i>
                                    <span class="like-count">${article.likes || 0}</span>
                                </span>
                            </div>
                        </div>
                    </header>

                    <div class="article-content">
                        ${this.convertMarkdownToHTML(article.content)}
                    </div>

                    <footer class="article-footer">
                        <div class="article-tags">
                            ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="article-actions">
                            <button class="action-btn like-btn" data-article-id="${article.id}">
                                <i class="far fa-heart"></i>
                                いいね
                            </button>
                            <button class="action-btn share-btn" onclick="navigator.share ? navigator.share({title: '${article.title}', url: window.location.href}) : alert('シェア機能はサポートされていません')">
                                <i class="fas fa-share"></i>
                                シェア
                            </button>
                        </div>
                    </footer>
                </article>
            `;
        }
    }

    showError(message) {
        const articleContainer = document.querySelector('.article-container');
        if (articleContainer) {
            articleContainer.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3em; color: #ff6b6b; margin-bottom: 20px;"></i>
                    <h2>エラー</h2>
                    <p>${message}</p>
                    <a href="./index.html" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        記事一覧に戻る
                    </a>
                </div>
            `;
        }
    }

    convertMarkdownToHTML(markdown) {
        // 簡単なMarkdown変換（本格的な変換は外部ライブラリが必要）
        return markdown
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^(.+)$/gm, '<p>$1</p>')
            .replace(/<p><h/g, '<h')
            .replace(/<\/h([1-6])><\/p>/g, '</h$1>')
            .replace(/<p><ul>/g, '<ul>')
            .replace(/<\/ul><\/p>/g, '</ul>');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    setupEventListeners() {
        // スムーズスクロール
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = anchor.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // 記事内の画像クリックで拡大表示
        document.querySelectorAll('.article-content img').forEach(img => {
            img.addEventListener('click', () => {
                this.showImageModal(img.src, img.alt);
            });
        });
    }

    setupCodeCopyButtons() {
        // コードコピー機能
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const codeBlock = e.target.closest('.code-block');
                const code = codeBlock.querySelector('code').textContent;
                
                navigator.clipboard.writeText(code).then(() => {
                    const originalIcon = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i>';
                    btn.style.color = '#00d4aa';
                    
                    setTimeout(() => {
                        btn.innerHTML = originalIcon;
                        btn.style.color = '';
                    }, 2000);
                }).catch(err => {
                    console.error('コピーに失敗しました:', err);
                });
            });
        });
    }

    setupTableOfContents() {
        const toc = document.getElementById('toc');
        if (!toc) return;

        // スクロールで目次のアクティブ項目を更新
        const headings = document.querySelectorAll('.content-section h2, .content-section h3');
        const tocLinks = toc.querySelectorAll('a');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    if (id) {
                        tocLinks.forEach(link => {
                            link.classList.remove('active');
                            if (link.getAttribute('href') === `#${id}`) {
                                link.classList.add('active');
                            }
                        });
                    }
                }
            });
        }, {
            rootMargin: '-20% 0px -70% 0px'
        });

        headings.forEach(heading => {
            if (!heading.id) {
                // IDが無い場合は生成
                const id = heading.textContent.toLowerCase()
                    .replace(/\s+/g, '-')
                    .replace(/[^\w\-]+/g, '');
                heading.id = id;
            }
            observer.observe(heading);
        });
    }

    setupCommentSystem() {
        const commentForm = document.getElementById('comment-input');
        const postCommentBtn = document.getElementById('post-comment');
        
        if (commentForm && postCommentBtn) {
            postCommentBtn.addEventListener('click', () => {
                this.postComment();
            });

            commentForm.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    this.postComment();
                }
            });
        }

        // コメントのいいね機能
        document.querySelectorAll('.comment-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (btn.querySelector('.fa-heart')) {
                    this.toggleCommentLike(btn);
                }
            });
        });

        // さらにコメントを読み込み
        const loadMoreBtn = document.querySelector('.load-more-comments');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMoreComments();
            });
        }
    }

    setupArticleActions() {
        // いいね機能
        document.querySelectorAll('.like-btn, .action-btn.like-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toggleArticleLike(btn);
            });
        });

        // ブックマーク機能
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toggleBookmark(btn);
            });
        });

        // シェア機能
        document.querySelectorAll('.share-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.shareArticle();
            });
        });

        // フォロー機能
        document.querySelectorAll('.follow-btn, .follow-btn-large').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toggleFollow(btn);
            });
        });
    }

    postComment() {
        const commentInput = document.getElementById('comment-input');
        const commentText = commentInput.value.trim();
        
        if (!commentText) {
            alert('コメントを入力してください');
            return;
        }

        // 仮のコメント追加（実際の実装ではAPIに送信）
        const commentsContainer = document.getElementById('comments-list');
        const newComment = this.createCommentElement({
            author: 'あなた',
            avatar: 'YOU',
            content: commentText,
            date: 'たった今',
            likes: 0
        });

        commentsContainer.insertBefore(newComment, commentsContainer.firstChild);
        
        // コメント数を更新
        const commentCount = document.querySelector('.comment-count');
        const currentCount = parseInt(commentCount.textContent.replace(/[()]/g, ''));
        commentCount.textContent = `(${currentCount + 1})`;
        
        // フォームをリセット
        commentInput.value = '';
        
        // 成功メッセージ
        this.showToast('コメントを投稿しました！');
    }

    createCommentElement(comment) {
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment-item';
        commentDiv.innerHTML = `
            <img src="https://via.placeholder.com/40x40?text=${comment.avatar}" alt="${comment.author}" class="comment-avatar">
            <div class="comment-content">
                <div class="comment-header">
                    <span class="commenter-name">${comment.author}</span>
                    <span class="comment-date">${comment.date}</span>
                </div>
                <p class="comment-text">${comment.content}</p>
                <div class="comment-actions-small">
                    <button class="comment-action-btn">
                        <i class="far fa-heart"></i>
                        ${comment.likes}
                    </button>
                    <button class="comment-action-btn">
                        <i class="fas fa-reply"></i>
                        返信
                    </button>
                </div>
            </div>
        `;
        
        // 新しく追加したコメントにもイベントリスナーを設定
        const likeBtn = commentDiv.querySelector('.comment-action-btn');
        likeBtn.addEventListener('click', () => {
            this.toggleCommentLike(likeBtn);
        });
        
        return commentDiv;
    }

    toggleArticleLike(btn) {
        const isLiked = btn.classList.contains('liked');
        const countElement = btn.querySelector('.count');
        const heartIcon = btn.querySelector('.fa-heart');
        let currentCount = parseInt(countElement.textContent);

        if (isLiked) {
            // いいねを取り消し
            btn.classList.remove('liked');
            heartIcon.classList.remove('fas');
            heartIcon.classList.add('far');
            countElement.textContent = currentCount - 1;
        } else {
            // いいねを追加
            btn.classList.add('liked');
            heartIcon.classList.remove('far');
            heartIcon.classList.add('fas');
            countElement.textContent = currentCount + 1;
            
            // アニメーション
            this.animateButton(btn);
        }

        // LocalStorageに保存
        this.saveLikeStatus('article-1', !isLiked);
    }

    toggleCommentLike(btn) {
        const isLiked = btn.classList.contains('liked');
        const heartIcon = btn.querySelector('.fa-heart');
        const countText = btn.textContent.trim();
        const currentCount = parseInt(countText.split(' ')[1] || '0');

        if (isLiked) {
            btn.classList.remove('liked');
            heartIcon.classList.remove('fas');
            heartIcon.classList.add('far');
            btn.innerHTML = `<i class="far fa-heart"></i> ${currentCount - 1}`;
        } else {
            btn.classList.add('liked');
            heartIcon.classList.remove('far');
            heartIcon.classList.add('fas');
            btn.innerHTML = `<i class="fas fa-heart"></i> ${currentCount + 1}`;
            
            this.animateButton(btn);
        }
    }

    toggleBookmark(btn) {
        const isBookmarked = btn.classList.contains('bookmarked');
        const countElement = btn.querySelector('.count');
        const bookmarkIcon = btn.querySelector('.fa-bookmark');
        let currentCount = parseInt(countElement.textContent);

        if (isBookmarked) {
            btn.classList.remove('bookmarked');
            bookmarkIcon.classList.remove('fas');
            bookmarkIcon.classList.add('far');
            countElement.textContent = currentCount - 1;
            this.showToast('ブックマークを解除しました');
        } else {
            btn.classList.add('bookmarked');
            bookmarkIcon.classList.remove('far');
            bookmarkIcon.classList.add('fas');
            countElement.textContent = currentCount + 1;
            this.animateButton(btn);
            this.showToast('ブックマークに追加しました');
        }
    }

    shareArticle() {
        const title = document.getElementById('main-article-title').textContent;
        const url = window.location.href;
        
        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            }).catch(console.error);
        } else {
            // フォールバック: クリップボードにコピー
            navigator.clipboard.writeText(url).then(() => {
                this.showToast('記事のURLをクリップボードにコピーしました');
            }).catch(() => {
                // さらなるフォールバック: 共有メニューを表示
                this.showShareMenu();
            });
        }
    }

    showShareMenu() {
        const shareMenu = document.createElement('div');
        shareMenu.className = 'share-menu';
        shareMenu.innerHTML = `
            <div class="share-menu-content">
                <h4>この記事をシェア</h4>
                <div class="share-buttons">
                    <a href="https://twitter.com/share?url=${encodeURIComponent(window.location.href)}" target="_blank" class="share-btn-twitter">
                        <i class="fab fa-twitter"></i> Twitter
                    </a>
                    <a href="https://www.facebook.com/sharer.php?u=${encodeURIComponent(window.location.href)}" target="_blank" class="share-btn-facebook">
                        <i class="fab fa-facebook"></i> Facebook
                    </a>
                    <button onclick="navigator.clipboard.writeText('${window.location.href}').then(() => this.parentElement.parentElement.parentElement.remove())" class="share-btn-copy">
                        <i class="fas fa-link"></i> URLをコピー
                    </button>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="close-btn">×</button>
            </div>
        `;
        
        document.body.appendChild(shareMenu);
        
        // 背景クリックで閉じる
        shareMenu.addEventListener('click', (e) => {
            if (e.target === shareMenu) {
                shareMenu.remove();
            }
        });
    }

    toggleFollow(btn) {
        const isFollowing = btn.classList.contains('following');
        
        if (isFollowing) {
            btn.classList.remove('following');
            btn.innerHTML = '<i class="fas fa-plus"></i> フォロー';
            this.showToast('フォローを解除しました');
        } else {
            btn.classList.add('following');
            btn.innerHTML = '<i class="fas fa-check"></i> フォロー中';
            this.animateButton(btn);
            this.showToast('フォローしました');
        }
    }

    loadMoreComments() {
        const loadMoreBtn = document.querySelector('.load-more-comments');
        
        // ローディング状態
        const originalHTML = loadMoreBtn.innerHTML;
        loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 読み込み中...';
        loadMoreBtn.disabled = true;
        
        // 2秒後にダミーコメントを追加
        setTimeout(() => {
            const commentsContainer = document.getElementById('comments-list');
            const newComments = [
                {
                    author: 'H.T',
                    avatar: 'HT',
                    content: 'とても勉強になりました。実装の詳細についてもっと知りたいです。',
                    date: '2日前',
                    likes: 5
                },
                {
                    author: 'N.K',
                    avatar: 'NK',
                    content: 'エラーハンドリングの部分、参考になります。ありがとうございます！',
                    date: '3日前',
                    likes: 3
                }
            ];
            
            newComments.forEach(comment => {
                const commentElement = this.createCommentElement(comment);
                commentsContainer.appendChild(commentElement);
            });
            
            loadMoreBtn.innerHTML = originalHTML;
            loadMoreBtn.disabled = false;
            loadMoreBtn.remove(); // 全てのコメントを読み込んだとして削除
        }, 2000);
    }

    animateButton(btn) {
        btn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            btn.style.transform = 'scale(1)';
        }, 200);
    }

    showImageModal(src, alt) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="image-modal-content">
                <img src="${src}" alt="${alt}">
                <button class="close-modal">×</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 閉じるボタンとモーダル背景のクリックで閉じる
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('close-modal')) {
                modal.remove();
                document.body.style.overflow = '';
            }
        });
        
        document.body.style.overflow = 'hidden';
    }

    saveLikeStatus(articleId, isLiked) {
        const likedArticles = JSON.parse(localStorage.getItem('likedArticles') || '{}');
        likedArticles[articleId] = isLiked;
        localStorage.setItem('likedArticles', JSON.stringify(likedArticles));
    }

    loadLikedStatus() {
        const likedArticles = JSON.parse(localStorage.getItem('likedArticles') || '{}');
        
        Object.keys(likedArticles).forEach(articleId => {
            if (likedArticles[articleId]) {
                const likeButtons = document.querySelectorAll(`[data-article-id="${articleId}"], .like-btn`);
                likeButtons.forEach(btn => {
                    btn.classList.add('liked');
                    const heartIcon = btn.querySelector('.fa-heart');
                    if (heartIcon) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                    }
                });
            }
        });
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, 3000);
    }
}

// DOMが読み込まれたらアプリを初期化
document.addEventListener('DOMContentLoaded', () => {
    window.articleApp = new ArticlePageApp();
});

// 追加CSS（動的に追加）
const additionalCSS = `
    /* シェアメニュー */
    .share-menu {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .share-menu-content {
        background: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        position: relative;
        min-width: 300px;
    }
    
    .share-menu-content h4 {
        margin: 0 0 20px;
        text-align: center;
        color: #333;
    }
    
    .share-buttons {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .share-buttons a,
    .share-buttons button {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        border-radius: 8px;
        text-decoration: none;
        border: none;
        font-size: 14px;
        cursor: pointer;
        transition: background 0.3s ease;
    }
    
    .share-btn-twitter {
        background: #1da1f2;
        color: white;
    }
    
    .share-btn-facebook {
        background: #4267b2;
        color: white;
    }
    
    .share-btn-copy {
        background: #f5f5f5;
        color: #666;
    }
    
    .close-btn {
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #999;
    }
    
    /* 画像モーダル */
    .image-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.9);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .image-modal-content {
        position: relative;
        max-width: 90vw;
        max-height: 90vh;
    }
    
    .image-modal-content img {
        max-width: 100%;
        max-height: 90vh;
        object-fit: contain;
        border-radius: 8px;
    }
    
    .close-modal {
        position: absolute;
        top: -40px;
        right: 0;
        background: none;
        border: none;
        color: white;
        font-size: 30px;
        cursor: pointer;
    }
    
    /* トースト通知 */
    .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: #333;
        color: white;
        padding: 12px 24px;
        border-radius: 25px;
        font-size: 14px;
        z-index: 10000;
        opacity: 0;
        transition: all 0.3s ease;
    }
    
    .toast.show {
        transform: translateX(-50%) translateY(0);
        opacity: 1;
    }
    
    /* フォローボタンの状態 */
    .follow-btn.following,
    .follow-btn-large.following {
        background: #e8f5e8;
        color: #2e7d32;
        border-color: #4caf50;
    }
    
    /* ブックマークボタンの状態 */
    .bookmark-btn.bookmarked {
        color: #ffa726;
    }
    
    .bookmark-btn.bookmarked .fa-bookmark {
        color: #ffa726;
    }
`;

// 動的にCSSを追加
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);