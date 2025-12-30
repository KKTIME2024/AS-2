// VRChat Memory Keeper - Main JavaScript

// DOM 加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('VRChat Memory Keeper loaded!');
    
    // 初始化所有功能
    initializeLikeButtons();
    initializeFormValidation();
    initializeSmoothScroll();
    initializeTagFiltering();
    initializeTooltips();
    initializeKeyboardShortcuts();
});

// 初始化点赞按钮功能
function initializeLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(btn => {
        btn.addEventListener('click', async function(e) {
            // 防止按钮文本选中
            e.preventDefault();
            
            const eventId = this.dataset.eventId;
            const likeCountSpan = this.querySelector('.like-count');
            
            if (!eventId || !likeCountSpan) {
                return;
            }
            
            // 添加加载状态
            this.disabled = true;
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> 点赞中...';
            
            try {
                // 发送点赞请求
                const response = await fetch(`/api/event/${eventId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                if (response.ok) {
                    const data = await response.json();
                    likeCountSpan.textContent = data.likes;
                    
                    // 添加点赞成功动画
                    this.classList.add('like-success');
                    setTimeout(() => {
                        this.classList.remove('like-success');
                    }, 500);
                }
            } catch (error) {
                console.error('点赞失败:', error);
            } finally {
                // 恢复按钮状态
                this.disabled = false;
                this.innerHTML = originalText;
            }
        });
    });
}

// 初始化表单验证
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // 简单的必填字段验证
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // 如果表单无效，阻止提交
            if (!isValid) {
                e.preventDefault();
                // 显示提示信息
                showNotification('请填写所有必填字段', 'error');
            }
        });
        
        // 输入时移除无效状态
        const formInputs = form.querySelectorAll('input, textarea, select');
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    });
}

// 初始化平滑滚动
function initializeSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // 考虑导航栏高度
                    behavior: 'smooth'
                });
            }
        });
    });
}

// 初始化标签筛选功能
function initializeTagFiltering() {
    const tagButtons = document.querySelectorAll('.btn-tag-filter, [href*="tag="]');
    
    tagButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // 添加筛选动画
            const contentArea = document.querySelector('.row');
            if (contentArea) {
                contentArea.style.opacity = '0.5';
                contentArea.style.transition = 'opacity 0.3s ease';
                
                // 恢复不透明度
                setTimeout(() => {
                    contentArea.style.opacity = '1';
                }, 300);
            }
        });
    });
}

// 初始化工具提示
function initializeTooltips() {
    // 检查是否有 Bootstrap 5 工具提示
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// 显示通知
function showNotification(message, type = 'success') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 添加到页面
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// 添加CSS样式到页面
const style = document.createElement('style');
style.textContent = `
    /* 点赞成功动画 */
    .like-success {
        animation: likePulse 0.5s ease-in-out;
    }
    
    @keyframes likePulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.15);
        }
        100% {
            transform: scale(1);
        }
    }
    
    /* 加载动画 */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 平滑过渡效果 */
    .alert {
        transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    .is-invalid {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20%, 60% { transform: translateX(-10px); }
        40%, 80% { transform: translateX(10px); }
    }
`;

document.head.appendChild(style);

// 页面离开确认
let isFormSubmitting = false;

window.addEventListener('beforeunload', function(e) {
    // 如果表单正在提交，不显示提示
    if (isFormSubmitting) {
        return;
    }
    
    // 检查是否有未提交的表单
    const forms = document.querySelectorAll('form');
    let hasUnsavedChanges = false;
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            const originalValue = input.dataset.originalValue || '';
            if (input.value.trim() !== originalValue.trim()) {
                hasUnsavedChanges = true;
            }
        });
    });
    
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '您有未保存的更改，确定要离开吗？';
        return e.returnValue;
    }
});

// 保存表单初始值
function saveFormInitialValues() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.dataset.originalValue = input.value;
        });
        
        // 监听表单提交事件，防止离开提示
        form.addEventListener('submit', function() {
            isFormSubmitting = true;
        });
    });
}

// 在页面加载完成后保存表单初始值
document.addEventListener('DOMContentLoaded', saveFormInitialValues);

// 初始化键盘快捷键
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // 忽略在输入框、文本域或可编辑元素中的按键
        if (e.target.tagName === 'INPUT' || 
            e.target.tagName === 'TEXTAREA' || 
            e.target.tagName === 'SELECT' ||
            e.target.isContentEditable) {
            return;
        }
        
        // 按 '/' 键聚焦到搜索框（如果存在）
        if (e.key === '/' && !e.ctrlKey && !e.altKey && !e.metaKey) {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="搜索"], #search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            } else {
                // 如果没有搜索框，显示提示
                showNotification('当前页面没有搜索功能，请使用其他快捷键。', 'info');
            }
        }
        
        // 按 'c' 键跳转到创建事件页面（如果用户已登录）
        if (e.key === 'c' && !e.ctrlKey && !e.altKey && !e.metaKey) {
            const createEventLink = document.querySelector('a[href*="create_event"], a[aria-label*="创建事件"]');
            if (createEventLink) {
                window.location.href = createEventLink.href;
            }
        }
        
        // 按 'h' 或 '?' 键显示快捷键帮助
        if ((e.key === 'h' || e.key === '?') && !e.ctrlKey && !e.altKey && !e.metaKey) {
            e.preventDefault();
            showKeyboardShortcutsHelp();
        }
        
        // 按 'Escape' 键关闭模态框或清除搜索
        if (e.key === 'Escape') {
            // 关闭所有打开的模态框
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                openModals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                });
            } else {
                // 清除搜索框内容（如果存在）
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="搜索"]');
                if (searchInput && searchInput.value) {
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                    showNotification('搜索已清除', 'info');
                }
            }
        }
        
        // 按 'g' 然后 'h' 跳转到首页（Github风格导航）
        if (e.key === 'g' && !e.ctrlKey && !e.altKey && !e.metaKey) {
            // 设置一个短暂的超时来检测第二个键
            const handleSecondKey = function(e2) {
                if (e2.key === 'h' && !e2.ctrlKey && !e2.altKey && !e2.metaKey) {
                    e2.preventDefault();
                    const homeLink = document.querySelector('a[href="/"], a[href*="index"], .navbar-brand');
                    if (homeLink) {
                        window.location.href = homeLink.href;
                    }
                }
                document.removeEventListener('keydown', handleSecondKey);
            };
            document.addEventListener('keydown', handleSecondKey);
            setTimeout(() => {
                document.removeEventListener('keydown', handleSecondKey);
            }, 1000); // 1秒内检测第二个键
        }
    });
}

// 显示键盘快捷键帮助
function showKeyboardShortcutsHelp() {
    const helpHtml = `
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">键盘快捷键</h5>
            </div>
            <div class="card-body">
                <dl class="row mb-0">
                    <dt class="col-sm-6"><kbd>/</kbd></dt>
                    <dd class="col-sm-6">聚焦搜索框</dd>
                    
                    <dt class="col-sm-6"><kbd>c</kbd></dt>
                    <dd class="col-sm-6">创建新事件（如已登录）</dd>
                    
                    <dt class="col-sm-6"><kbd>g</kbd> <kbd>h</kbd></dt>
                    <dd class="col-sm-6">跳转到首页</dd>
                    
                    <dt class="col-sm-6"><kbd>h</kbd> 或 <kbd>?</kbd></dt>
                    <dd class="col-sm-6">显示此帮助</dd>
                    
                    <dt class="col-sm-6"><kbd>Esc</kbd></dt>
                    <dd class="col-sm-6">关闭模态框或清除搜索</dd>
                    
                    <dt class="col-sm-6"><kbd>j</kbd>/<kbd>k</kbd></dt>
                    <dd class="col-sm-6">在事件列表中上下导航（如果可用）</dd>
                </dl>
                <p class="text-muted small mt-3">
                    提示：快捷键仅在不在输入框中时有效。
                </p>
            </div>
        </div>
    `;
    
    // 创建模态框
    const modalId = 'keyboard-shortcuts-modal';
    let modal = document.getElementById(modalId);
    
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    ${helpHtml}
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // 显示模态框
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// 在页面右下角添加快捷键提示
function addKeyboardShortcutsHint() {
    const hint = document.createElement('div');
    hint.className = 'keyboard-shortcuts-hint';
    hint.innerHTML = `
        <button class="btn btn-sm btn-outline-secondary" 
                onclick="showKeyboardShortcutsHelp()"
                aria-label="查看键盘快捷键帮助">
            <small>快捷键: <kbd>?</kbd></small>
        </button>
    `;
    hint.style.position = 'fixed';
    hint.style.bottom = '20px';
    hint.style.right = '20px';
    hint.style.zIndex = '1000';
    
    document.body.appendChild(hint);
}

// 在页面加载完成后添加快捷键提示
document.addEventListener('DOMContentLoaded', addKeyboardShortcutsHint);
