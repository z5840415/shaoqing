// 话术库页面逻辑

let currentTemplates = [];

// 初始化话术库页面
async function initTemplatesPage() {
    document.getElementById('createTemplateBtn').onclick = createNewTemplate;
    await loadTemplates();
}

// 加载话术列表
async function loadTemplates() {
    try {
        const templates = await TemplatesAPI.list();
        currentTemplates = templates;
        renderTemplates(templates);
    } catch (error) {
        showMessage('加载话术列表失败: ' + error.message, 'error');
    }
}

// 渲染话术卡片
function renderTemplates(templates) {
    const grid = document.getElementById('templatesGrid');

    if (!templates || templates.length === 0) {
        grid.innerHTML = '<div class="empty-state">暂无话术，请创建新话术</div>';
        return;
    }

    grid.innerHTML = templates.map(template => `
        <div class="template-card ${template.is_default ? 'default' : ''}" onclick="editTemplate(${template.id})">
            <div class="template-header">
                <span class="template-name">${template.name}</span>
                ${template.is_default ? '<span class="template-badge">默认</span>' : ''}
            </div>
            <div class="template-content">${template.content}</div>
            <div class="template-stats">
                <span>使用次数：${template.usage_count}</span>
                <span>回复次数：${template.reply_count}</span>
                <span>回复率：${template.usage_count > 0 ? ((template.reply_count / template.usage_count) * 100).toFixed(1) : 0}%</span>
            </div>
            <div class="template-actions" onclick="event.stopPropagation()">
                ${!template.is_default ? `<button class="btn btn-secondary" onclick="setDefaultTemplate(${template.id})">设为默认</button>` : ''}
                <button class="btn btn-secondary" onclick="editTemplate(${template.id})">编辑</button>
                <button class="btn btn-danger" onclick="deleteTemplate(${template.id})">删除</button>
            </div>
        </div>
    `).join('');
}

// 创建新话术
function createNewTemplate() {
    const content = `
        <div class="form-group">
            <label>话术名称 *</label>
            <input type="text" id="templateName" placeholder="例如：首次触达-标准版" required>
        </div>
        <div class="form-group">
            <label>话术内容 *</label>
            <textarea id="templateContent" placeholder="输入话术内容，支持变量：{昵称} {粉丝数} {微信号} 等" rows="8" required></textarea>
            <div class="form-help">抖音私信限制200字以内</div>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" id="templateDefault">
                设为默认话术
            </label>
        </div>
        <div class="form-group">
            <label>预览效果</label>
            <div id="templatePreview" style="padding: 12px; background: #f5f5f5; border-radius: 4px; min-height: 60px;">
                <span style="color: #999;">请输入话术内容</span>
            </div>
        </div>
    `;

    const footer = `
        <button class="btn btn-secondary" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" onclick="saveNewTemplate()">创建</button>
    `;

    window.currentModal = createModal('创建话术', content, footer);

    // 实时预览
    document.getElementById('templateContent').oninput = (e) => {
        const preview = document.getElementById('templatePreview');
        const content = e.target.value.replace('{昵称}', '张三')
            .replace('{粉丝数}', '2.8万')
            .replace('{微信号}', 'your_wechat_id');
        preview.innerHTML = content || '<span style="color: #999;">请输入话术内容</span>';
    };
}

// 保存新话术
async function saveNewTemplate() {
    try {
        const name = document.getElementById('templateName').value.trim();
        const content = document.getElementById('templateContent').value.trim();
        const isDefault = document.getElementById('templateDefault').checked;

        if (!name || !content) {
            showMessage('请填写完整信息', 'error');
            return;
        }

        if (content.length > 200) {
            showMessage('话术内容不能超过200字', 'error');
            return;
        }

        await TemplatesAPI.create({ name, content, is_default: isDefault });
        showMessage('创建成功！', 'success');
        closeModal();
        await loadTemplates();
    } catch (error) {
        showMessage('创建失败: ' + error.message, 'error');
    }
}

// 编辑话术
function editTemplate(id) {
    const template = currentTemplates.find(t => t.id === id);
    if (!template) return;

    const content = `
        <div class="form-group">
            <label>话术名称 *</label>
            <input type="text" id="templateName" value="${template.name}" required>
        </div>
        <div class="form-group">
            <label>话术内容 *</label>
            <textarea id="templateContent" rows="8" required>${template.content}</textarea>
            <div class="form-help">抖音私信限制200字以内，当前 ${template.content.length} 字</div>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" id="templateDefault" ${template.is_default ? 'checked' : ''}>
                设为默认话术
            </label>
        </div>
        <div class="form-group">
            <label>预览效果</label>
            <div id="templatePreview" style="padding: 12px; background: #f5f5f5; border-radius: 4px;">
                ${template.content.replace('{昵称}', '张三').replace('{粉丝数}', '2.8万')}
            </div>
        </div>
    `;

    const footer = `
        <button class="btn btn-secondary" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" onclick="updateTemplate(${id})">保存</button>
    `;

    window.currentModal = createModal('编辑话术', content, footer);

    // 实时预览
    document.getElementById('templateContent').oninput = (e) => {
        const preview = document.getElementById('templatePreview');
        const helpText = e.target.parentElement.querySelector('.form-help');
        const content = e.target.value.replace('{昵称}', '张三')
            .replace('{粉丝数}', '2.8万')
            .replace('{微信号}', 'your_wechat_id');
        preview.innerHTML = content;
        helpText.textContent = `抖音私信限制200字以内，当前 ${e.target.value.length} 字`;
    };
}

// 更新话术
async function updateTemplate(id) {
    try {
        const name = document.getElementById('templateName').value.trim();
        const content = document.getElementById('templateContent').value.trim();
        const isDefault = document.getElementById('templateDefault').checked;

        if (!name || !content) {
            showMessage('请填写完整信息', 'error');
            return;
        }

        if (content.length > 200) {
            showMessage('话术内容不能超过200字', 'error');
            return;
        }

        await TemplatesAPI.update(id, { name, content, is_default: isDefault });
        showMessage('保存成功！', 'success');
        closeModal();
        await loadTemplates();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

// 设为默认话术
async function setDefaultTemplate(id) {
    try {
        await TemplatesAPI.setDefault(id);
        showMessage('设置成功！', 'success');
        await loadTemplates();
    } catch (error) {
        showMessage('设置失败: ' + error.message, 'error');
    }
}

// 删除话术
async function deleteTemplate(id) {
    if (!confirm('确定要删除这个话术吗？')) return;

    try {
        await TemplatesAPI.delete(id);
        showMessage('删除成功！', 'success');
        await loadTemplates();
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}
