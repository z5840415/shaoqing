const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// 启动Python后端服务
function startPythonBackend() {
    const pythonScript = path.join(__dirname, '..', 'backend', 'main.py');

    // 判断是开发环境还是生产环境
    const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

    if (isDev) {
        // 开发环境：直接运行Python脚本
        pythonProcess = spawn('python', [pythonScript]);
    } else {
        // 生产环境：运行打包后的可执行文件
        const backendExe = path.join(process.resourcesPath, 'backend', 'backend.exe');
        pythonProcess = spawn(backendExe);
    }

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python输出: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python错误: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python进程退出，代码: ${code}`);
    });

    // 等待后端启动
    return new Promise((resolve) => {
        setTimeout(resolve, 3000); // 等待3秒
    });
}

// 创建主窗口
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'assets', 'icon.png')
    });

    // 加载主页面
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    // 开发环境打开开发者工具
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// 应用准备完成
app.whenReady().then(async () => {
    // 启动Python后端
    await startPythonBackend();

    // 创建窗口
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// 所有窗口关闭
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 应用退出前清理
app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// IPC通信处理
ipcMain.handle('get-backend-url', () => {
    return 'http://127.0.0.1:8000';
});
