// 应用状态管理
const AppState = {
    currentTab: 'url',
    isConverting: false,
    selectedFile: null,
    lastResult: null,
    subscribeUrl: null
};

// 安全获取DOM元素的辅助函数
function safeGetElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with id '${id}' not found`);
    }
    return element;
}

function safeQuerySelector(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Element with selector '${selector}' not found`);
    }
    return element;
}

function safeQuerySelectorAll(selector) {
    const elements = document.querySelectorAll(selector);
    if (elements.length === 0) {
        console.warn(`No elements found with selector '${selector}'`);
    }
    return elements;
}

// DOM元素引用
const Elements = {
    // 标签页
    tabButtons: safeQuerySelectorAll('.tab-btn'),
    tabContents: safeQuerySelectorAll('.tab-content'),
    
    // 输入元素
    urlInput: safeGetElement('subscription-url'),
    fileInput: safeGetElement('file-input'),
    uploadArea: safeGetElement('upload-area'),
    
    // 按钮
    convertUrlBtn: safeGetElement('convert-url-btn'),
    convertFileBtn: safeGetElement('convert-file-btn'),
    downloadBtn: safeGetElement('download-btn'),
    retryBtn: safeGetElement('retry-btn'),
    
    // 显示区域
    progressSection: safeGetElement('progress-section'),
    resultSection: safeGetElement('result-section'),
    errorSection: safeGetElement('error-section'),
    
    // 进度条
    progressFill: safeGetElement('progress-fill'),
    progressText: safeGetElement('progress-text'),
    
    // 结果显示
    totalNodes: safeGetElement('total-nodes'),
    stableNodes: safeGetElement('stable-nodes'),
    filteredNodes: safeGetElement('filtered-nodes'),
    regionCount: safeGetElement('region-count'),
    mainPortNodes: safeGetElement('main-port-nodes'),
    regionPorts: safeGetElement('region-ports'),
    regionGrid: safeGetElement('region-grid'),
    downloadFilename: safeGetElement('download-filename'),
    
    // 错误显示
    errorMessage: safeGetElement('error-message')
};

// 地区映射配置
const RegionConfig = {
    '香港': { flag: '🇭🇰', port: 7891, usage: '速度最快' },
    '美国': { flag: '🇺🇸', port: 7892, usage: '内容解锁' },
    '日本': { flag: '🇯🇵', port: 7893, usage: '游戏优化' },
    '新加坡': { flag: '🇸🇬', port: 7894, usage: '东南亚' },
    '台湾': { flag: '🇹🇼', port: 7895, usage: '中文内容' }
};

// 初始化应用
function initApp() {
    console.log('🚀 初始化 Clash 转换器应用');
    setupEventListeners();
    setupFileUpload();
    hideAllSections();
    validateUrlInput(); // 初始验证
}

// 设置事件监听器
function setupEventListeners() {
    // 标签页切换
    Elements.tabButtons.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        }
    });
    
    // 转换按钮
    if (Elements.convertUrlBtn) {
        Elements.convertUrlBtn.addEventListener('click', handleUrlConvert);
    }
    if (Elements.convertFileBtn) {
        Elements.convertFileBtn.addEventListener('click', handleFileConvert);
    }
    
    // 下载按钮
    if (Elements.downloadBtn) {
        Elements.downloadBtn.addEventListener('click', handleDownload);
    }
    
    // 重试按钮
    if (Elements.retryBtn) {
        Elements.retryBtn.addEventListener('click', handleRetry);
    }
    
    // 输入框变化
    if (Elements.urlInput) {
        Elements.urlInput.addEventListener('input', validateUrlInput);
        Elements.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleUrlConvert();
        });
    }
}

// 设置文件上传
function setupFileUpload() {
    if (!Elements.uploadArea || !Elements.fileInput) return;
    
    // 点击上传区域
    Elements.uploadArea.addEventListener('click', () => {
        Elements.fileInput.click();
    });
    
    // 文件选择
    Elements.fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    Elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        Elements.uploadArea.classList.add('dragover');
    });
    
    Elements.uploadArea.addEventListener('dragleave', () => {
        Elements.uploadArea.classList.remove('dragover');
    });
    
    Elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        Elements.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect({ target: { files } });
        }
    });
}

// 标签页切换
function switchTab(tabName) {
    AppState.currentTab = tabName;
    
    // 更新按钮状态
    Elements.tabButtons.forEach(btn => {
        if (btn) {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        }
    });
    
    // 更新内容显示
    Elements.tabContents.forEach(content => {
        if (content) {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        }
    });
    
    // 隐藏结果区域
    hideAllSections();
}

// 验证URL输入
function validateUrlInput() {
    if (!Elements.urlInput || !Elements.convertUrlBtn) return;
    
    const url = Elements.urlInput.value.trim();
    const isValid = url && (url.startsWith('http://') || url.startsWith('https://'));
    
    Elements.convertUrlBtn.disabled = !isValid;
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (!file) {
        AppState.selectedFile = null;
        if (Elements.convertFileBtn) {
            Elements.convertFileBtn.disabled = true;
        }
        updateUploadAreaText('拖拽配置文件到此处或点击选择');
        return;
    }
    
    // 检查文件类型
    const allowedTypes = ['.yaml', '.yml', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
        showError('只支持 .yaml, .yml, .txt 格式的文件');
        if (Elements.fileInput) {
            Elements.fileInput.value = '';
        }
        return;
    }
    
    // 检查文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('文件过大，请确保文件小于16MB');
        if (Elements.fileInput) {
            Elements.fileInput.value = '';
        }
        return;
    }
    
    AppState.selectedFile = file;
    if (Elements.convertFileBtn) {
        Elements.convertFileBtn.disabled = false;
    }
    updateUploadAreaText(`已选择文件: ${file.name}`);
}

// 更新上传区域文本
function updateUploadAreaText(text) {
    if (!Elements.uploadArea) return;
    
    const uploadContent = Elements.uploadArea.querySelector('.upload-text p');
    if (uploadContent) {
        uploadContent.textContent = text;
    }
}

// 处理URL转换
async function handleUrlConvert() {
    if (!Elements.urlInput) return;
    
    const url = Elements.urlInput.value.trim();
    
    if (!url) {
        showError('请输入订阅链接');
        return;
    }
    
    // 获取选择的转换模式
    const modeInput = safeQuerySelector('input[name="convert-mode"]:checked');
    const mode = modeInput ? modeInput.value : 'standard';
    
    await convertConfig('url', { url, mode });
}

// 处理文件转换
async function handleFileConvert() {
    if (!AppState.selectedFile) {
        showError('请先选择一个配置文件');
        return;
    }
    
    // 获取选择的转换模式
    const modeInput = safeQuerySelector('input[name="convert-mode-file"]:checked');
    const mode = modeInput ? modeInput.value : 'standard';
    
    // 创建FormData
    const formData = new FormData();
    formData.append('file', AppState.selectedFile);
    formData.append('mode', mode);
    
    await convertConfig('file', formData);
}

// 转换配置的通用函数
async function convertConfig(type, data) {
    if (AppState.isConverting) return;
    
    try {
        AppState.isConverting = true;
        hideAllSections();
        showProgress();
        animateProgress();
        
        const url = type === 'url' ? '/api/convert/url' : '/api/convert/file';
        const options = {
            method: 'POST'
        };
        
        if (type === 'url') {
            options.headers = {
                'Content-Type': 'application/json'
            };
            options.body = JSON.stringify(data);
        } else {
            options.body = data; // FormData
        }
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        hideProgress();
        
        if (result.success) {
            AppState.lastResult = result;
            showResult(result);
            showNotification('转换成功！', 'success');
        } else {
            showError(result.message || '转换失败，请检查输入内容');
        }
        
    } catch (error) {
        hideProgress();
        console.error('转换错误:', error);
        showError('网络错误，请检查连接后重试');
    } finally {
        AppState.isConverting = false;
    }
}

// 显示进度
function showProgress() {
    if (Elements.progressSection) {
        Elements.progressSection.style.display = 'block';
    }
}

// 隐藏进度
function hideProgress() {
    if (Elements.progressSection) {
        Elements.progressSection.style.display = 'none';
    }
}

// 动画进度条
function animateProgress() {
    if (!Elements.progressFill || !Elements.progressText) return;
    
    let progress = 0;
    const steps = ['初始化...', '获取配置...', '解析节点...', '过滤节点...', '生成配置...', '完成！'];
    let stepIndex = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if (progress > 100) progress = 100;
        
        Elements.progressFill.style.width = progress + '%';
        if (stepIndex < steps.length) {
            Elements.progressText.textContent = steps[stepIndex];
            stepIndex++;
        }
        
        if (progress >= 100) {
            clearInterval(interval);
        }
    }, 500);
}

// 显示结果
function showResult(result) {
    if (!Elements.resultSection) return;
    
    Elements.resultSection.style.display = 'block';
    
    // 更新统计信息
    const stats = result.stats || {};
    if (Elements.totalNodes) Elements.totalNodes.textContent = stats.total_nodes || 0;
    if (Elements.stableNodes) Elements.stableNodes.textContent = stats.stable_nodes || 0;
    if (Elements.filteredNodes) Elements.filteredNodes.textContent = stats.filtered_nodes || 0;
    if (Elements.regionCount) Elements.regionCount.textContent = stats.region_count || 0;
    if (Elements.mainPortNodes) Elements.mainPortNodes.textContent = stats.stable_nodes || 0;
    
    // 更新下载文件名
    if (Elements.downloadFilename && result.filename) {
        Elements.downloadFilename.textContent = `文件名: ${result.filename}`;
    }
    
    // 显示端口配置
    if (result.regions) {
        showPortConfig(result.regions);
        showRegionDistribution(result.regions);
    }
    
    // 显示OpenWrt提示
    if (result.mode === 'openwrt' && result.openwrt_tips) {
        showOpenWrtTips(result.openwrt_tips);
    }
    
    // 设置下载链接
    if (Elements.downloadBtn && result.filename) {
        Elements.downloadBtn.onclick = () => handleDownload(result.filename);
    }
    
    // 设置订阅链接 (只在URL转换时显示)
    const subscribeSection = safeGetElement('subscribe-section');
    const copySubscribeBtn = safeGetElement('copy-subscribe-btn');
    
    if (result.subscribe_url && subscribeSection && copySubscribeBtn) {
        subscribeSection.style.display = 'flex';
        AppState.subscribeUrl = result.subscribe_url;
        copySubscribeBtn.onclick = () => handleCopySubscribe();
    } else if (subscribeSection) {
        subscribeSection.style.display = 'none';
    }
}

// 显示端口配置
function showPortConfig(regions) {
    const portTable = safeQuerySelector('.port-table');
    if (!portTable) return;
    
    // 清除现有的端口行（除了主端口）
    const existingRows = portTable.querySelectorAll('.port-row:not(.main-port)');
    existingRows.forEach(row => row.remove());
    
    // 添加地区端口行
    Object.entries(regions).forEach(([region, nodes]) => {
        const config = RegionConfig[region];
        if (!config || nodes.length === 0) return;
        
        const row = document.createElement('div');
        row.className = 'port-row';
        row.innerHTML = `
            <div class="port-number">
                <span class="port-badge">${config.port}</span>
            </div>
            <div class="port-type">
                <span class="type-badge">SOCKS</span>
            </div>
            <div class="port-region">${config.flag} ${region}</div>
            <div class="port-nodes">${nodes.length}</div>
            <div class="port-usage">${config.usage}</div>
        `;
        portTable.appendChild(row);
    });
}

// 显示地区分布
function showRegionDistribution(regions) {
    if (!Elements.regionGrid) return;
    
    Elements.regionGrid.innerHTML = '';
    
    Object.entries(regions).forEach(([region, nodes]) => {
        const flag = getRegionFlag(region);
        
        const item = document.createElement('div');
        item.className = 'region-item';
        item.innerHTML = `
            <div class="region-flag">${flag}</div>
            <div class="region-name">${region}</div>
            <div class="region-count">${nodes.length} 个节点</div>
        `;
        Elements.regionGrid.appendChild(item);
    });
}

// 获取地区旗帜
function getRegionFlag(regionName) {
    const flagMap = {
        '香港': '🇭🇰', '美国': '🇺🇸', '日本': '🇯🇵', '新加坡': '🇸🇬', '台湾': '🇹🇼',
        '韩国': '🇰🇷', '英国': '🇬🇧', '加拿大': '🇨🇦', '澳大利亚': '🇦🇺', '德国': '🇩🇪',
        '法国': '🇫🇷', '荷兰': '🇳🇱', '俄罗斯': '🇷🇺', '印度': '🇮🇳', '泰国': '🇹🇭'
    };
    return flagMap[regionName] || '🌍';
}

// 显示OpenWrt提示
function showOpenWrtTips(tips) {
    const tipsSection = safeGetElement('openwrt-tips');
    const tipsContent = safeGetElement('tips-content');
    
    if (tipsSection && tipsContent) {
        tipsSection.style.display = 'block';
        tipsContent.innerHTML = tips.join('<br>');
    }
}

// 显示错误
function showError(message) {
    hideAllSections();
    
    if (Elements.errorSection) {
        Elements.errorSection.style.display = 'block';
    }
    if (Elements.errorMessage) {
        Elements.errorMessage.textContent = message;
    }
    
    showNotification(message, 'error');
}

// 隐藏所有区域
function hideAllSections() {
    const sections = [Elements.progressSection, Elements.resultSection, Elements.errorSection];
    sections.forEach(section => {
        if (section) {
            section.style.display = 'none';
        }
    });
    
    // 隐藏OpenWrt提示
    const openwrtTips = safeGetElement('openwrt-tips');
    if (openwrtTips) {
        openwrtTips.style.display = 'none';
    }
}

// 处理重试
function handleRetry() {
    hideAllSections();
    
    if (AppState.currentTab === 'url') {
        handleUrlConvert();
    } else {
        handleFileConvert();
    }
}

// 处理下载
function handleDownload(filename) {
    if (!filename && AppState.lastResult) {
        filename = AppState.lastResult.filename;
    }
    
    if (filename) {
        const link = document.createElement('a');
        link.href = `/download/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification('文件下载开始', 'success');
    } else {
        showError('下载链接无效，请重新转换');
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // 添加样式
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '9999',
        padding: '15px 20px',
        borderRadius: '12px',
        color: '#ffffff',
        fontSize: '14px',
        fontWeight: '500',
        maxWidth: '300px',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        transform: 'translateX(400px)',
        transition: 'transform 0.3s ease',
        background: type === 'success' ? 'rgba(34, 197, 94, 0.9)' : 
                   type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 
                   'rgba(59, 130, 246, 0.9)'
    });
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 动画显示
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 处理复制订阅链接
function handleCopySubscribe() {
    if (!AppState.subscribeUrl) {
        showError('订阅链接无效，请重新转换');
        return;
    }
    
    if (navigator.clipboard && window.isSecureContext) {
        // 使用现代API
        navigator.clipboard.writeText(AppState.subscribeUrl).then(() => {
            showNotification('订阅链接已复制到剪贴板', 'success');
        }).catch(() => {
            fallbackCopyText(AppState.subscribeUrl);
        });
    } else {
        // 降级方案
        fallbackCopyText(AppState.subscribeUrl);
    }
}

// 降级复制方案
function fallbackCopyText(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification('订阅链接已复制到剪贴板', 'success');
        } else {
            showSubscribeUrlDialog(text);
        }
    } catch (err) {
        showSubscribeUrlDialog(text);
    }
    
    document.body.removeChild(textArea);
}

// 显示订阅链接对话框
function showSubscribeUrlDialog(url) {
    const dialog = document.createElement('div');
    dialog.className = 'subscribe-dialog';
    dialog.innerHTML = `
        <div class="subscribe-dialog-backdrop" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div class="subscribe-dialog-content" style="
                background: rgba(30, 41, 59, 0.95);
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                border: 1px solid rgba(71, 85, 105, 0.3);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            ">
                <h3 style="color: #f1f5f9; margin-bottom: 20px; font-size: 1.2rem;">
                    <i class="fas fa-link" style="color: #3b82f6; margin-right: 10px;"></i>
                    订阅链接
                </h3>
                <div style="
                    background: rgba(51, 65, 85, 0.5);
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 20px;
                    border: 1px solid rgba(71, 85, 105, 0.3);
                ">
                    <input type="text" value="${url}" readonly style="
                        width: 100%;
                        background: transparent;
                        border: none;
                        color: #e2e8f0;
                        font-size: 0.9rem;
                        padding: 5px;
                        outline: none;
                        word-break: break-all;
                    ">
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button class="dialog-btn dialog-btn-secondary" style="
                        padding: 10px 20px;
                        border: none;
                        border-radius: 10px;
                        background: rgba(71, 85, 105, 0.5);
                        color: #e2e8f0;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">关闭</button>
                    <button class="dialog-btn dialog-btn-primary" style="
                        padding: 10px 20px;
                        border: none;
                        border-radius: 10px;
                        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                        color: #ffffff;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">手动复制</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    // 事件处理
    const input = dialog.querySelector('input');
    const closeBtn = dialog.querySelector('.dialog-btn-secondary');
    const copyBtn = dialog.querySelector('.dialog-btn-primary');
    
    closeBtn.onclick = () => document.body.removeChild(dialog);
    copyBtn.onclick = () => {
        input.select();
        showNotification('请使用 Ctrl+C 复制链接', 'info');
    };
    
    // 点击背景关闭
    dialog.onclick = (e) => {
        if (e.target === dialog || e.target.classList.contains('subscribe-dialog-backdrop')) {
            document.body.removeChild(dialog);
        }
    };
    
    // 自动选中文本
    input.select();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);

// 添加全局错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise拒绝:', event.reason);
}); 