// 设置页面逻辑

// 初始化设置页面
async function initSettingsPage() {
    await renderSettings();
}

// 渲染设置页面
async function renderSettings() {
    try {
        const cookieData = await SettingsAPI.getCookie();
        const securityConfig = await SettingsAPI.getSecurityConfig();

        const container = document.getElementById('settingsContainer');

        container.innerHTML = `
            <!-- Cookie登录管理 -->
            <div class="stat-card" style="margin-bottom: 24px;">
                <h3>抖音登录设置</h3>

                <div class="form-group">
                    <label>Cookie导入方式</label>
                    <div style="padding: 12px; background: #f5f5f5; border-radius: 4px; margin-bottom: 12px;">
                        <ol style="margin: 0; padding-left: 20px; line-height: 1.8;">
                            <li>在浏览器中登录 douyin.com</li>
                            <li>按F12打开开发者工具，切换到Console（控制台）</li>
                            <li>输入并执行: <code>document.cookie</code></li>
                            <li>复制输出的Cookie字符串，粘贴到下方</li>
                        </ol>
                    </div>

                    <label>Cookie字符串 *</label>
                    <textarea id="cookieInput" rows="4" placeholder="粘贴Cookie内容...">${cookieData.cookie || ''}</textarea>
                </div>

                <div class="form-group">
                    <label>账号标识（可选）</label>
                    <input type="text" id="accountInput" placeholder="例如：运营账号1" value="${cookieData.account || ''}">
                </div>

                <div class="form-group">
                    <button class="btn btn-primary" onclick="saveCookie()">保存Cookie</button>
                    <button class="btn btn-secondary" onclick="testCookie()">测试连接</button>
                    <button class="btn btn-danger" onclick="clearCookie()">清除Cookie</button>
                </div>

                <div id="cookieTestResult" style="margin-top: 12px;"></div>

                ${cookieData.cookie ? `
                    <div style="margin-top: 12px; padding: 12px; background: #e6f7ff; border-radius: 4px;">
                        <div style="color: #1890ff;">✓ Cookie已配置</div>
                        ${cookieData.account ? `<div style="color: #666; margin-top: 4px;">账号：${cookieData.account}</div>` : ''}
                    </div>
                ` : ''}
            </div>

            <!-- 安全防护设置 -->
            <div class="stat-card">
                <h3>安全防护设置</h3>

                <div class="form-group">
                    <label>安全模式</label>
                    <div>
                        <label style="display: block; margin-bottom: 8px;">
                            <input type="radio" name="securityMode" value="conservative" ${securityConfig.mode === 'conservative' ? 'checked' : ''}>
                            保守模式（30-60秒间隔，每小时30条）
                        </label>
                        <label style="display: block; margin-bottom: 8px;">
                            <input type="radio" name="securityMode" value="standard" ${securityConfig.mode === 'standard' ? 'checked' : ''}>
                            标准模式（20-40秒间隔，每小时50条）
                        </label>
                        <label style="display: block;">
                            <input type="radio" name="securityMode" value="aggressive" ${securityConfig.mode === 'aggressive' ? 'checked' : ''}>
                            激进模式（10-30秒间隔，每小时80条）<span style="color: #ff4d4f;">（不推荐）</span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>发送间隔（秒）</label>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="number" id="secMinInterval" value="${securityConfig.min_interval || 30}" min="10" max="120" style="width: 100px;">
                        <span>-</span>
                        <input type="number" id="secMaxInterval" value="${securityConfig.max_interval || 60}" min="10" max="120" style="width: 100px;">
                        <span style="color: #999;">秒（随机）</span>
                    </div>
                </div>

                <div class="form-group">
                    <label>批次设置</label>
                    <div style="display: flex; gap: 16px;">
                        <div>
                            <label style="font-weight: normal;">每发送</label>
                            <input type="number" id="secBatchSize" value="${securityConfig.batch_size || 30}" min="5" max="100" style="width: 100px;">
                            <span>条</span>
                        </div>
                        <div>
                            <label style="font-weight: normal;">休息</label>
                            <input type="number" id="secBatchRest" value="${(securityConfig.batch_rest || 600) / 60}" min="1" max="60" style="width: 100px;">
                            <span>分钟</span>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>每日上限</label>
                    <input type="number" id="secDailyLimit" value="${securityConfig.daily_limit || 100}" min="10" max="500" style="width: 150px;">
                    <span style="margin-left: 8px;">条</span>
                </div>

                <div class="form-group">
                    <label>行为模拟</label>
                    <div>
                        <label style="display: block; margin-bottom: 8px;">
                            <input type="checkbox" id="secNightPause" ${securityConfig.night_pause ? 'checked' : ''}>
                            夜间暂停（23:00-7:00不发送）
                        </label>
                        <label style="display: block; margin-bottom: 8px;">
                            <input type="checkbox" id="secRandomVisit" ${securityConfig.random_visit ? 'checked' : ''}>
                            随机访问主页（停留2-5秒）
                        </label>
                        <label style="display: block;">
                            <input type="checkbox" id="secSimulateTyping" ${securityConfig.simulate_typing ? 'checked' : ''}>
                            模拟打字速度（非瞬间发送）
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <button class="btn btn-primary" onclick="saveSecurityConfig()">保存设置</button>
                    <button class="btn btn-secondary" onclick="resetSecurityConfig()">恢复默认</button>
                </div>
            </div>
        `;

        // 绑定模式切换事件
        document.querySelectorAll('input[name="securityMode"]').forEach(radio => {
            radio.onchange = (e) => {
                applySecurityMode(e.target.value);
            };
        });

    } catch (error) {
        showMessage('加载设置失败: ' + error.message, 'error');
    }
}

// 应用安全模式预设
function applySecurityMode(mode) {
    const modes = {
        conservative: { min: 30, max: 60, batch: 30, rest: 10 },
        standard: { min: 20, max: 40, batch: 50, rest: 10 },
        aggressive: { min: 10, max: 30, batch: 80, rest: 5 }
    };

    const config = modes[mode];
    if (config) {
        document.getElementById('secMinInterval').value = config.min;
        document.getElementById('secMaxInterval').value = config.max;
        document.getElementById('secBatchSize').value = config.batch;
        document.getElementById('secBatchRest').value = config.rest;
    }
}

// 保存Cookie
async function saveCookie() {
    try {
        const cookie = document.getElementById('cookieInput').value.trim();
        const account = document.getElementById('accountInput').value.trim();

        if (!cookie) {
            showMessage('请输入Cookie', 'error');
            return;
        }

        await SettingsAPI.saveCookie({
            cookie,
            account,
            expire_time: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
        });

        showMessage('Cookie保存成功！', 'success');
        await renderSettings();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

// 测试Cookie
async function testCookie() {
    const resultEl = document.getElementById('cookieTestResult');
    resultEl.innerHTML = '<div style="color: #999;">正在测试...</div>';

    try {
        const result = await SettingsAPI.testCookie();

        if (result.valid) {
            resultEl.innerHTML = '<div style="color: #52c41a;">✓ ' + result.message + '</div>';
        } else {
            resultEl.innerHTML = '<div style="color: #ff4d4f;">✗ ' + result.message + '</div>';
        }
    } catch (error) {
        resultEl.innerHTML = '<div style="color: #ff4d4f;">✗ 测试失败: ' + error.message + '</div>';
    }
}

// 清除Cookie
async function clearCookie() {
    if (!confirm('确定要清除Cookie吗？')) return;

    try {
        await SettingsAPI.saveCookie({ cookie: null, account: null, expire_time: null });
        showMessage('Cookie已清除', 'success');
        await renderSettings();
    } catch (error) {
        showMessage('清除失败: ' + error.message, 'error');
    }
}

// 保存安全配置
async function saveSecurityConfig() {
    try {
        const mode = document.querySelector('input[name="securityMode"]:checked').value;
        const config = {
            mode,
            min_interval: parseInt(document.getElementById('secMinInterval').value),
            max_interval: parseInt(document.getElementById('secMaxInterval').value),
            batch_size: parseInt(document.getElementById('secBatchSize').value),
            batch_rest: parseInt(document.getElementById('secBatchRest').value) * 60,
            daily_limit: parseInt(document.getElementById('secDailyLimit').value),
            night_pause: document.getElementById('secNightPause').checked,
            random_visit: document.getElementById('secRandomVisit').checked,
            simulate_typing: document.getElementById('secSimulateTyping').checked
        };

        await SettingsAPI.saveSecurityConfig(config);
        showMessage('设置保存成功！', 'success');
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

// 恢复默认配置
async function resetSecurityConfig() {
    if (!confirm('确定要恢复默认配置吗？')) return;

    try {
        const defaultConfig = {
            mode: 'standard',
            min_interval: 30,
            max_interval: 60,
            batch_size: 30,
            batch_rest: 600,
            daily_limit: 100,
            night_pause: true,
            random_visit: true,
            simulate_typing: true
        };

        await SettingsAPI.saveSecurityConfig(defaultConfig);
        showMessage('已恢复默认配置', 'success');
        await renderSettings();
    } catch (error) {
        showMessage('恢复失败: ' + error.message, 'error');
    }
}
