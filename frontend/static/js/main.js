/**
 * EchoTrack前端通用JS
 */

// 公共变量
const refreshInterval = 60000; // 60秒自动刷新
const animationDuration = 300; // 动画持续时间（毫秒）

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 激活当前页面的导航项
    activateCurrentNavItem();
    
    // 设置页面自动刷新（如果当前页面有需要的话）
    setupAutoRefresh();
    
    // 添加卡片悬停效果
    setupCardHoverEffects();
    
    // 设置表单验证
    setupFormValidation();
    
    // 添加页面过渡动画
    addPageTransitions();
});

// 激活当前页面的导航项
function activateCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// 设置页面自动刷新
function setupAutoRefresh() {
    // 检查页面是否有refreshData函数
    if (typeof window.refreshData === 'function') {
        setInterval(() => {
            window.refreshData();
        }, refreshInterval);
    }
}

// 设置卡片悬停效果
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card:not(.status-card)');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = 'var(--box-shadow-hover)';
            this.style.transition = `all ${animationDuration}ms ease`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// 设置表单验证
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// 添加页面过渡动画
function addPageTransitions() {
    const contentContainer = document.querySelector('.container.fade-in');
    if (contentContainer) {
        contentContainer.style.opacity = '0';
        contentContainer.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            contentContainer.style.transition = `all ${animationDuration}ms ease-out`;
            contentContainer.style.opacity = '1';
            contentContainer.style.transform = 'translateY(0)';
        }, 100);
    }
}

// 通用错误处理
function handleFetchError(error, message = '操作失败') {
    console.error(error);
    showToast(message, 'danger');
}

// 显示消息提示
function showToast(message, type = 'success') {
    // 检查是否已有toast容器
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        // 创建toast容器
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // 创建toast元素
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // 设置toast内容
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'danger') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <i class="fas fa-${icon} me-2"></i>
            <strong class="me-auto">EchoTrack</strong>
            <small>刚刚</small>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // 添加到容器
    toastContainer.appendChild(toast);
    
    // 显示toast
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 3000 });
    bsToast.show();
    
    // 添加进入动画
    toast.style.transform = 'translateY(20px)';
    toast.style.opacity = '0';
    
    setTimeout(() => {
        toast.style.transition = 'all 300ms ease-out';
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    }, 50);
    
    // 监听隐藏事件，添加退出动画
    toast.addEventListener('hide.bs.toast', function() {
        toast.style.transform = 'translateY(20px)';
        toast.style.opacity = '0';
    });
    
    // 监听隐藏完成事件，移除DOM元素
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// 格式化日期时间
function formatDateTime(date) {
    if (!date) return '-';
    
    const d = new Date(date);
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出公共函数
window.showToast = showToast;
window.handleFetchError = handleFetchError;
window.formatDateTime = formatDateTime;
window.debounce = debounce;
window.throttle = throttle; 