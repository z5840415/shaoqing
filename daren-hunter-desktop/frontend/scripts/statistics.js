// 数据统计页面逻辑

// 初始化统计页面
async function initStatisticsPage() {
    document.getElementById('exportReportBtn').onclick = handleExportReport;
    await loadStatistics();
}

// 加载统计数据
async function loadStatistics() {
    try {
        const [overview, templateStats, timeStats] = await Promise.all([
            StatisticsAPI.getOverview(),
            StatisticsAPI.getTemplateStats(),
            StatisticsAPI.getBestTime()
        ]);

        renderStatistics(overview, templateStats, timeStats);
    } catch (error) {
        showMessage('加载统计数据失败: ' + error.message, 'error');
    }
}

// 渲染统计数据
function renderStatistics(overview, templateStats, timeStats) {
    const container = document.getElementById('statsContainer');

    container.innerHTML = `
        <!-- 数据概览 -->
        <div class="stat-card">
            <h3>数据概览</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #e8e8e8;">指标</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">今日</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">本周</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">本月</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px;">发送数量</td>
                        <td style="text-align: center; padding: 8px;">${overview.today_sent}</td>
                        <td style="text-align: center; padding: 8px;">${overview.week_sent}</td>
                        <td style="text-align: center; padding: 8px;">${overview.month_sent}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">回复数量</td>
                        <td style="text-align: center; padding: 8px;">${overview.today_replied}</td>
                        <td style="text-align: center; padding: 8px;">${overview.week_replied}</td>
                        <td style="text-align: center; padding: 8px;">${overview.month_replied}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">回复率</td>
                        <td style="text-align: center; padding: 8px; color: #1890ff; font-weight: 600;">${overview.today_reply_rate}%</td>
                        <td style="text-align: center; padding: 8px; color: #1890ff; font-weight: 600;">${overview.week_reply_rate}%</td>
                        <td style="text-align: center; padding: 8px; color: #1890ff; font-weight: 600;">${overview.month_reply_rate}%</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 话术效果对比 -->
        <div class="stat-card">
            <h3>话术效果对比</h3>
            ${templateStats.length > 0 ? `
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #e8e8e8;">话术名称</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">使用次数</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">回复次数</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">回复率</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${templateStats.map((stat, index) => `
                            <tr>
                                <td style="padding: 8px;">
                                    ${index === 0 ? '⭐ ' : ''}${stat.template_name}
                                </td>
                                <td style="text-align: center; padding: 8px;">${stat.usage_count}</td>
                                <td style="text-align: center; padding: 8px;">${stat.reply_count}</td>
                                <td style="text-align: center; padding: 8px; color: #1890ff; font-weight: 600;">
                                    ${stat.reply_rate}%
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<div class="empty-state">暂无数据</div>'}
        </div>

        <!-- 最佳发送时间 -->
        <div class="stat-card">
            <h3>最佳发送时间</h3>
            ${timeStats.length > 0 ? `
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #e8e8e8;">时间段</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">回复次数</th>
                            <th style="text-align: center; padding: 8px; border-bottom: 1px solid #e8e8e8;">回复率</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${timeStats.map((stat, index) => `
                            <tr>
                                <td style="padding: 8px;">
                                    ${index === 0 ? '⭐ ' : ''}${stat.time_slot}
                                    ${index === 0 ? '<span style="color: #52c41a; margin-left: 8px;">最佳</span>' : ''}
                                </td>
                                <td style="text-align: center; padding: 8px;">${stat.reply_count}</td>
                                <td style="text-align: center; padding: 8px; color: #1890ff; font-weight: 600;">
                                    ${stat.reply_rate}%
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<div class="empty-state">暂无数据</div>'}
        </div>
    `;
}

// 导出报表
async function handleExportReport() {
    try {
        await StatisticsAPI.exportReport();
        showMessage('报表导出成功！', 'success');
    } catch (error) {
        showMessage('导出失败: ' + error.message, 'error');
    }
}
