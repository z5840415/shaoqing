// 工具函数

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// 格式化数字
function formatNumber(num) {
    if (!num && num !== 0) return '-';
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
    }
    return num.toString();
}

// 显示提示消息
function showMessage(message, type = 'info') {
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        background: ${type === 'error' ? '#ff4d4f' : type === 'success' ? '#52c41a' : '#1890ff'};
        color: #fff;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideDown 0.3s ease;
    `;

    document.body.appendChild(messageEl);

    setTimeout(() => {
        messageEl.style.animation = 'slideUp 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(messageEl);
        }, 300);
    }, 3000);
}

// 确认对话框
function confirm(message) {
    return window.confirm(message);
}

// 创建Modal
function createModal(title, content, footer = null) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';

    const modal = document.createElement('div');
    modal.className = 'modal';

    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = `
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close">&times;</button>
    `;

    const body = document.createElement('div');
    body.className = 'modal-body';
    if (typeof content === 'string') {
        body.innerHTML = content;
    } else {
        body.appendChild(content);
    }

    modal.appendChild(header);
    modal.appendChild(body);

    if (footer) {
        const footerEl = document.createElement('div');
        footerEl.className = 'modal-footer';
        if (typeof footer === 'string') {
            footerEl.innerHTML = footer;
        } else {
            footerEl.appendChild(footer);
        }
        modal.appendChild(footerEl);
    }

    overlay.appendChild(modal);

    // 关闭按钮事件
    const closeBtn = header.querySelector('.modal-close');
    closeBtn.onclick = () => {
        document.body.removeChild(overlay);
    };

    // 点击遮罩关闭
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };

    document.body.appendChild(overlay);

    return overlay;
}

// 获取状态标签HTML
function getStatusTag(status) {
    const statusMap = {
        'pending': '待发送',
        'sent': '已发送',
        'replied': '已回复',
        'wechat': '已加微信',
        'signed': '已签约',
        'rejected': '已拒绝',
    };

    const text = statusMap[status] || status;
    return `<span class="status-tag ${status}">${text}</span>`;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 文件选择
function selectFile(accept = '*') {
    return new Promise((resolve) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = accept;
        input.onchange = (e) => {
            resolve(e.target.files[0]);
        };
        input.click();
    });
}

// 检查后端服务状态
async function checkBackendStatus() {
    const statusEl = document.getElementById('backendStatus');
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusEl.querySelector('.text').textContent = '后端服务运行中';
            statusEl.classList.remove('error');
            return true;
        }
    } catch (error) {
        statusEl.querySelector('.text').textContent = '后端服务连接失败';
        statusEl.classList.add('error');
        return false;
    }
}
