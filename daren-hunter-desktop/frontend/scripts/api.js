// API基础URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// API工具类
class API {
    static async request(url, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${url}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '请求失败');
            }

            return await response.json();
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }

    static async get(url) {
        return this.request(url, { method: 'GET' });
    }

    static async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    static async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    static async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }

    // 上传文件
    static async upload(url, file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上传失败');
        }

        return await response.json();
    }

    // 下载文件
    static async download(url, filename) {
        const response = await fetch(`${API_BASE_URL}${url}`);
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
    }
}

// 达人管理API
class TargetsAPI {
    static async list(params = {}) {
        const query = new URLSearchParams(params).toString();
        return API.get(`/api/targets/?${query}`);
    }

    static async create(data) {
        return API.post('/api/targets/', data);
    }

    static async update(id, data) {
        return API.put(`/api/targets/${id}`, data);
    }

    static async delete(id) {
        return API.delete(`/api/targets/${id}`);
    }

    static async batchDelete(ids) {
        return API.post('/api/targets/batch-delete', ids);
    }

    static async importExcel(file) {
        return API.upload('/api/targets/import-excel', file);
    }

    static async downloadTemplate() {
        return API.download('/api/targets/download/template', 'daren_import_template.xlsx');
    }

    static async export(ids = null) {
        const url = ids ? `/api/targets/export?ids=${ids.join(',')}` : '/api/targets/export';
        return API.download(url, 'daren_export.xlsx');
    }
}

// 话术模板API
class TemplatesAPI {
    static async list() {
        return API.get('/api/templates/');
    }

    static async create(data) {
        return API.post('/api/templates/', data);
    }

    static async update(id, data) {
        return API.put(`/api/templates/${id}`, data);
    }

    static async delete(id) {
        return API.delete(`/api/templates/${id}`);
    }

    static async setDefault(id) {
        return API.post(`/api/templates/${id}/set-default`, {});
    }

    static async preview(id, variables) {
        return API.post(`/api/templates/${id}/preview`, variables);
    }
}

// 发送任务API
class SendAPI {
    static async start(config) {
        return API.post('/api/send/start', config);
    }

    static async getProgress() {
        return API.get('/api/send/progress');
    }

    static async pause() {
        return API.post('/api/send/pause', {});
    }

    static async resume() {
        return API.post('/api/send/resume', {});
    }

    static async stop() {
        return API.post('/api/send/stop', {});
    }

    static async getLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return API.get(`/api/send/logs?${query}`);
    }

    static async getStatus() {
        return API.get('/api/send/status');
    }
}

// 统计API
class StatisticsAPI {
    static async getOverview() {
        return API.get('/api/statistics/overview');
    }

    static async getTemplateStats() {
        return API.get('/api/statistics/templates');
    }

    static async getBestTime() {
        return API.get('/api/statistics/best-time');
    }

    static async exportReport() {
        return API.download('/api/statistics/export-report', `statistics_report_${new Date().toISOString().split('T')[0]}.xlsx`);
    }
}

// 设置API
class SettingsAPI {
    static async list() {
        return API.get('/api/settings/');
    }

    static async get(key) {
        return API.get(`/api/settings/${key}`);
    }

    static async update(key, data) {
        return API.put(`/api/settings/${key}`, data);
    }

    static async getCookie() {
        return API.get('/api/settings/cookie/get');
    }

    static async saveCookie(data) {
        return API.post('/api/settings/cookie/save', data);
    }

    static async testCookie() {
        return API.post('/api/settings/cookie/test', {});
    }

    static async getSecurityConfig() {
        return API.get('/api/settings/security/get');
    }

    static async saveSecurityConfig(config) {
        return API.post('/api/settings/security/save', config);
    }
}
