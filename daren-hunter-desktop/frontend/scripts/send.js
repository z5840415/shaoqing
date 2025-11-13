// 发送任务页面逻辑

let sendInterval = null;

// 初始化发送任务页面
async function initSendPage() {
    await renderSendConfig();
}

// 渲染发送配置面板
async function renderSendConfig() {
    try {
        // 获取话术列表
        const templates = await TemplatesAPI.list();
        const defaultTemplate = templates.find(t => t.is_default) || templates[0];

        // 获取安全配置
        const securityConfig = await SettingsAPI.getSecurityConfig();

        const panel = document.getElementById('sendConfigPanel');
        panel.innerHTML = `
            <div class="send-config">
                <h3>发送配置</h3>

                <div class="form-group">
                    <label>选中目标</label>
                    <input type="text" id="selectedTargetsDisplay" readonly value="请从达人管理页面选择目标">
                    <div class="form-help">返回达人管理页面选择需要发送的达人</div>
                </div>

                <div class="form-group">
                    <label>话术选择 *</label>
                    <select id="templateSelect" required>
                        ${templates.map(t => `
                            <option value="${t.id}" ${t.id === defaultTemplate?.id ? 'selected' : ''}>
                                ${t.name}${t.is_default ? '（默认）' : ''}
                            </option>
                        `).join('')}
                    </select>
                </div>

                <div class="form-group">
                    <label>发送策略</label>
                    <div>
                        <label><input type="radio" name="sendMode" value="immediate" checked> 立即发送</label>
                        <label style="margin-left: 20px;"><input type="radio" name="sendMode" value="scheduled"> 定时发送</label>
                    </div>
                    <input type="datetime-local" id="scheduledTime" style="margin-top: 8px; display: none;">
                </div>

                <div class="form-group">
                    <label>安全设置</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label>发送间隔（秒）</label>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <input type="number" id="minInterval" value="${securityConfig.min_interval || 30}" min="10" max="120" style="width: 80px;">
                                <span>-</span>
                                <input type="number" id="maxInterval" value="${securityConfig.max_interval || 60}" min="10" max="120" style="width: 80px;">
                            </div>
                        </div>
                        <div>
                            <label>每日上限（条）</label>
                            <input type="number" id="dailyLimit" value="${securityConfig.daily_limit || 100}" min="10" max="500">
                        </div>
                        <div>
                            <label>批次大小（条）</label>
                            <input type="number" id="batchSize" value="${securityConfig.batch_size || 30}" min="5" max="100">
                        </div>
                        <div>
                            <label>批次休息（分钟）</label>
                            <input type="number" id="batchRest" value="${(securityConfig.batch_rest || 600) / 60}" min="1" max="60">
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>登录信息</label>
                    <div id="cookieStatus" style="padding: 12px; background: #f5f5f5; border-radius: 4px;">
                        正在检查...
                    </div>
                </div>

                <div class="form-group" style="margin-top: 24px;">
                    <button class="btn btn-secondary" onclick="window.switchPage('targets')">返回</button>
                    <button class="btn btn-primary" onclick="startSending()" style="margin-left: 12px;">开始发送</button>
                </div>
            </div>
        `;

        // 绑定事件
        document.querySelectorAll('input[name="sendMode"]').forEach(radio => {
            radio.onchange = (e) => {
                document.getElementById('scheduledTime').style.display =
                    e.target.value === 'scheduled' ? 'block' : 'none';
            };
        });

        // 检查Cookie状态
        checkCookieStatus();

    } catch (error) {
        showMessage('加载发送配置失败: ' + error.message, 'error');
    }
}

// 检查Cookie状态
async function checkCookieStatus() {
    const statusEl = document.getElementById('cookieStatus');
    try {
        const result = await SettingsAPI.testCookie();
        if (result.valid) {
            statusEl.innerHTML = '<span style="color: #52c41a;">✓ Cookie有效</span> <button class="btn btn-secondary" onclick="window.switchPage(\'settings\')">重新配置</button>';
        } else {
            statusEl.innerHTML = '<span style="color: #ff4d4f;">✗ Cookie失效或未配置</span> <button class="btn btn-primary" onclick="window.switchPage(\'settings\')">去配置</button>';
        }
    } catch (error) {
        statusEl.innerHTML = '<span style="color: #ff4d4f;">✗ 无法连接到服务</span>';
    }
}

// 开始发送
async function startSending() {
    try {
        // 验证选择的目标
        if (!window.selectedTargetIds || window.selectedTargetIds.length === 0) {
            showMessage('请先选择要发送的达人', 'error');
            return;
        }

        // 获取配置
        const config = {
            target_ids: window.selectedTargetIds,
            template_id: parseInt(document.getElementById('templateSelect').value),
            min_interval: parseInt(document.getElementById('minInterval').value),
            max_interval: parseInt(document.getElementById('maxInterval').value),
            batch_size: parseInt(document.getElementById('batchSize').value),
            batch_rest: parseInt(document.getElementById('batchRest').value) * 60,
            daily_limit: parseInt(document.getElementById('dailyLimit').value),
        };

        // 定时发送
        const sendMode = document.querySelector('input[name="sendMode"]:checked').value;
        if (sendMode === 'scheduled') {
            const scheduledTime = document.getElementById('scheduledTime').value;
            if (!scheduledTime) {
                showMessage('请选择定时发送时间', 'error');
                return;
            }
            config.scheduled_time = scheduledTime;
        }

        // 启动发送
        await SendAPI.start(config);
        showMessage('发送任务已启动', 'success');

        // 显示进度面板
        document.getElementById('sendConfigPanel').classList.add('hidden');
        document.getElementById('sendProgressPanel').classList.remove('hidden');

        // 开始轮询进度
        startProgressPolling();

    } catch (error) {
        showMessage('启动发送失败: ' + error.message, 'error');
    }
}

// 开始轮询进度
function startProgressPolling() {
    if (sendInterval) clearInterval(sendInterval);

    updateProgress();
    sendInterval = setInterval(updateProgress, 2000);
}

// 更新进度
async function updateProgress() {
    try {
        const progress = await SendAPI.getProgress();
        renderProgress(progress);
    } catch (error) {
        // 任务可能已结束
        clearInterval(sendInterval);
        renderProgressComplete();
    }
}

// 渲染进度
function renderProgress(progress) {
    const panel = document.getElementById('sendProgressPanel');
    const percentage = Math.round(progress.progress);

    panel.innerHTML = `
        <div class="send-progress">
            <h3>发送进行中...</h3>

            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percentage}%">
                    ${percentage}%
                </div>
            </div>

            <div class="progress-stats" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0;">
                <div class="stat-card">
                    <div class="stat-label">已发送</div>
                    <div class="stat-value">${progress.sent} / ${progress.total}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">成功</div>
                    <div class="stat-value highlight">${progress.success}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">失败</div>
                    <div class="stat-value" style="color: #ff4d4f;">${progress.failed}</div>
                </div>
            </div>

            <div class="progress-info">
                <div>当前目标：${progress.current_target || '-'}</div>
                <div>剩余：${progress.remaining} 条</div>
            </div>

            <div class="progress-actions" style="margin-top: 24px;">
                <button class="btn btn-secondary" onclick="pauseSending()">暂停</button>
                <button class="btn btn-danger" onclick="stopSending()">停止</button>
            </div>
        </div>
    `;
}

// 渲染完成状态
function renderProgressComplete() {
    const panel = document.getElementById('sendProgressPanel');
    panel.innerHTML = `
        <div class="send-complete">
            <h3>发送完成！</h3>
            <div style="text-align: center; padding: 24px;">
                <svg style="width: 80px; height: 80px; color: #52c41a;" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
            </div>
            <div style="text-align: center; margin-top: 16px;">
                <button class="btn btn-primary" onclick="backToConfig()">返回配置</button>
                <button class="btn btn-secondary" onclick="window.switchPage('statistics')">查看统计</button>
            </div>
        </div>
    `;
}

// 暂停发送
async function pauseSending() {
    try {
        await SendAPI.pause();
        showMessage('已暂停发送', 'info');
    } catch (error) {
        showMessage('暂停失败: ' + error.message, 'error');
    }
}

// 停止发送
async function stopSending() {
    if (!confirm('确定要停止发送吗？')) return;

    try {
        await SendAPI.stop();
        clearInterval(sendInterval);
        showMessage('已停止发送', 'info');
        backToConfig();
    } catch (error) {
        showMessage('停止失败: ' + error.message, 'error');
    }
}

// 返回配置
function backToConfig() {
    clearInterval(sendInterval);
    document.getElementById('sendConfigPanel').classList.remove('hidden');
    document.getElementById('sendProgressPanel').classList.add('hidden');
}

// 导航到发送页面（从达人管理页面调用）
window.navigateToSend = function(targetIds) {
    window.selectedTargetIds = targetIds;
    window.switchPage('send');

    // 更新显示
    setTimeout(() => {
        const display = document.getElementById('selectedTargetsDisplay');
        if (display) {
            display.value = `已选择 ${targetIds.length} 个达人`;
        }
    }, 100);
};
