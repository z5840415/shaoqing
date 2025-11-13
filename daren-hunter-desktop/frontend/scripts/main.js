// 主控制脚本

// 页面初始化函数映射
const pageInitializers = {
    'targets': initTargetsPage,
    'templates': initTemplatesPage,
    'send': initSendPage,
    'statistics': initStatisticsPage,
    'settings': initSettingsPage
};

// 当前活动页面
let currentPage = 'targets';

// 应用启动
document.addEventListener('DOMContentLoaded', async () => {
    console.log('达人猎手应用启动...');

    // 检查后端状态
    await checkBackendStatus();
    setInterval(checkBackendStatus, 30000); // 每30秒检查一次

    // 绑定导航事件
    initNavigation();

    // 初始化第一个页面
    await switchPage('targets');
});

// 初始化导航
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', async () => {
            const page = item.dataset.page;
            await switchPage(page);
        });
    });
}

// 切换页面
window.switchPage = async function(pageName) {
    if (currentPage === pageName) return;

    // 更新导航高亮
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 切换页面显示
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // 初始化页面
    currentPage = pageName;
    const initializer = pageInitializers[pageName];
    if (initializer) {
        try {
            await initializer();
        } catch (error) {
            console.error(`初始化${pageName}页面失败:`, error);
            showMessage(`加载页面失败: ${error.message}`, 'error');
        }
    }
};

// 全局错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise拒绝:', event.reason);
});

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }

    @keyframes slideUp {
        from {
            transform: translate(-50%, 0);
            opacity: 1;
        }
        to {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
    }

    .btn-link {
        background: none;
        border: none;
        color: #1890ff;
        cursor: pointer;
        padding: 4px 8px;
        text-decoration: none;
    }

    .btn-link:hover {
        text-decoration: underline;
    }

    code {
        padding: 2px 6px;
        background: #f5f5f5;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
`;
document.head.appendChild(style);

console.log('达人猎手应用初始化完成');
