// VRChat Memory Keeper - Main JavaScript

// DOM 加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 VRChat Memory Keeper loaded!');
    
    // 初始化所有功能
    initializeLikeButtons();
    initializeFormValidation();
    initializeSmoothScroll();
    initializeTagFiltering();
    initializeTooltips();
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
window.addEventListener('beforeunload', function(e) {
    // 检查是否有未提交的表单
    const forms = document.querySelectorAll('form');
    let hasUnsavedChanges = false;
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            if (input.value.trim() && !input.dataset.originalValue) {
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
    });
}

// 在页面加载完成后保存表单初始值
document.addEventListener('DOMContentLoaded', saveFormInitialValues);
