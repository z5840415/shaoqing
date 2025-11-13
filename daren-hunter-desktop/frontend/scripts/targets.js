// 达人管理页面逻辑

let currentTargets = [];
let selectedTargets = new Set();

// 初始化达人管理页面
async function initTargetsPage() {
    // 绑定事件
    document.getElementById('importExcelBtn').onclick = handleImportExcel;
    document.getElementById('exportTargetsBtn').onclick = handleExportTargets;
    document.getElementById('downloadTemplateBtn').onclick = handleDownloadTemplate;
    document.getElementById('batchSendBtn').onclick = handleBatchSend;
    document.getElementById('batchDeleteBtn').onclick = handleBatchDelete;
    document.getElementById('selectAll').onchange = handleSelectAll;

    // 搜索和筛选
    const searchInput = document.getElementById('searchInput');
    searchInput.oninput = debounce(() => loadTargets(), 500);

    const statusFilter = document.getElementById('statusFilter');
    statusFilter.onchange = () => loadTargets();

    // 加载数据
    await loadTargets();
}

// 加载达人列表
async function loadTargets() {
    try {
        const search = document.getElementById('searchInput').value;
        const status = document.getElementById('statusFilter').value;

        const params = {};
        if (search) params.search = search;
        if (status) params.status = status;

        const data = await TargetsAPI.list(params);
        currentTargets = data.items;
        renderTargetsTable(data.items);
    } catch (error) {
        showMessage('加载达人列表失败: ' + error.message, 'error');
    }
}

// 渲染达人表格
function renderTargetsTable(targets) {
    const tbody = document.getElementById('targetsTableBody');

    if (!targets || targets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">暂无数据，请导入达人信息</td></tr>';
        return;
    }

    tbody.innerHTML = targets.map(target => `
        <tr data-id="${target.id}">
            <td><input type="checkbox" class="target-checkbox" data-id="${target.id}" ${selectedTargets.has(target.id) ? 'checked' : ''}></td>
            <td>${target.nickname}</td>
            <td>${target.douyin_id}</td>
            <td>${formatNumber(target.fans_count)}</td>
            <td>${target.tags || '-'}</td>
            <td>${getStatusTag(target.status)}</td>
            <td>${formatDate(target.created_at)}</td>
            <td>
                <button class="btn-link" onclick="editTarget(${target.id})">编辑</button>
                <button class="btn-link" onclick="deleteTarget(${target.id})">删除</button>
            </td>
        </tr>
    `).join('');

    // 绑定复选框事件
    tbody.querySelectorAll('.target-checkbox').forEach(checkbox => {
        checkbox.onchange = (e) => {
            const id = parseInt(e.target.dataset.id);
            if (e.target.checked) {
                selectedTargets.add(id);
            } else {
                selectedTargets.delete(id);
            }
            updateBatchActions();
        };
    });
}

// 更新批量操作按钮状态
function updateBatchActions() {
    const count = selectedTargets.size;
    document.getElementById('selectedInfo').textContent = `已选：${count}个`;
    document.getElementById('batchSendBtn').disabled = count === 0;
    document.getElementById('batchDeleteBtn').disabled = count === 0;
}

// 全选
function handleSelectAll(e) {
    const checked = e.target.checked;
    selectedTargets.clear();

    if (checked) {
        currentTargets.forEach(target => selectedTargets.add(target.id));
    }

    document.querySelectorAll('.target-checkbox').forEach(checkbox => {
        checkbox.checked = checked;
    });

    updateBatchActions();
}

// 导入Excel
async function handleImportExcel() {
    try {
        const file = await selectFile('.xlsx,.xls');
        if (!file) return;

        showMessage('正在导入...', 'info');
        const result = await TargetsAPI.importExcel(file);

        showMessage(`导入完成！成功: ${result.success}, 失败: ${result.failed}, 重复: ${result.duplicates}`, 'success');

        if (result.errors && result.errors.length > 0) {
            console.error('导入错误:', result.errors);
        }

        await loadTargets();
    } catch (error) {
        showMessage('导入失败: ' + error.message, 'error');
    }
}

// 导出达人
async function handleExportTargets() {
    try {
        const ids = selectedTargets.size > 0 ? Array.from(selectedTargets) : null;
        await TargetsAPI.export(ids);
        showMessage('导出成功！', 'success');
    } catch (error) {
        showMessage('导出失败: ' + error.message, 'error');
    }
}

// 下载模板
async function handleDownloadTemplate() {
    try {
        await TargetsAPI.downloadTemplate();
        showMessage('模板下载成功！', 'success');
    } catch (error) {
        showMessage('下载失败: ' + error.message, 'error');
    }
}

// 批量发送
function handleBatchSend() {
    if (selectedTargets.size === 0) return;

    // 切换到发送任务页面并传递选中的达人
    window.navigateToSend(Array.from(selectedTargets));
}

// 批量删除
async function handleBatchDelete() {
    if (selectedTargets.size === 0) return;

    if (!confirm(`确定要删除选中的 ${selectedTargets.size} 个达人吗？`)) return;

    try {
        await TargetsAPI.batchDelete(Array.from(selectedTargets));
        showMessage('删除成功！', 'success');
        selectedTargets.clear();
        await loadTargets();
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}

// 编辑达人
function editTarget(id) {
    const target = currentTargets.find(t => t.id === id);
    if (!target) return;

    const content = `
        <div class="form-group">
            <label>昵称 *</label>
            <input type="text" id="editNickname" value="${target.nickname}" required>
        </div>
        <div class="form-group">
            <label>抖音ID *</label>
            <input type="text" id="editDouyinId" value="${target.douyin_id}" required>
        </div>
        <div class="form-group">
            <label>主页链接</label>
            <input type="text" id="editHomepage" value="${target.homepage_url || ''}">
        </div>
        <div class="form-group">
            <label>粉丝数</label>
            <input type="number" id="editFans" value="${target.fans_count}">
        </div>
        <div class="form-group">
            <label>标签</label>
            <input type="text" id="editTags" value="${target.tags || ''}" placeholder="多个标签用逗号分隔">
        </div>
        <div class="form-group">
            <label>状态</label>
            <select id="editStatus">
                <option value="pending" ${target.status === 'pending' ? 'selected' : ''}>待发送</option>
                <option value="sent" ${target.status === 'sent' ? 'selected' : ''}>已发送</option>
                <option value="replied" ${target.status === 'replied' ? 'selected' : ''}>已回复</option>
                <option value="wechat" ${target.status === 'wechat' ? 'selected' : ''}>已加微信</option>
                <option value="signed" ${target.status === 'signed' ? 'selected' : ''}>已签约</option>
                <option value="rejected" ${target.status === 'rejected' ? 'selected' : ''}>已拒绝</option>
            </select>
        </div>
        <div class="form-group">
            <label>备注</label>
            <textarea id="editNotes">${target.notes || ''}</textarea>
        </div>
    `;

    const footer = `
        <button class="btn btn-secondary" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" onclick="saveTarget(${id})">保存</button>
    `;

    window.currentModal = createModal('编辑达人', content, footer);
}

// 保存达人
async function saveTarget(id) {
    try {
        const data = {
            nickname: document.getElementById('editNickname').value,
            homepage_url: document.getElementById('editHomepage').value,
            fans_count: parseInt(document.getElementById('editFans').value) || 0,
            tags: document.getElementById('editTags').value,
            status: document.getElementById('editStatus').value,
            notes: document.getElementById('editNotes').value,
        };

        await TargetsAPI.update(id, data);
        showMessage('保存成功！', 'success');
        closeModal();
        await loadTargets();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

// 删除达人
async function deleteTarget(id) {
    if (!confirm('确定要删除这个达人吗？')) return;

    try {
        await TargetsAPI.delete(id);
        showMessage('删除成功！', 'success');
        await loadTargets();
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}

// 关闭Modal
function closeModal() {
    if (window.currentModal) {
        document.body.removeChild(window.currentModal);
        window.currentModal = null;
    }
}
