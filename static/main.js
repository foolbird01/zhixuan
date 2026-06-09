/* ========================================
   智选平台 - 前端交互逻辑
   就像餐厅的"服务员"
   负责：接收客户点单、传递后厨、上菜
   ======================================== */

/* ---------- 全局变量 ---------- */
let selectedFile = null;          // 用户选中的文件（点单内容）
let selectedModels = [];          // 用户选中的模型（要测哪些模型）
let currentReportId = null;       // 当前评估任务的报告ID
let pollTimer = null;             // 轮询定时器（用来取消）

/* ---------- 页面加载完成后执行 ---------- */
document.addEventListener('DOMContentLoaded', function() {
    /*
     * DOMContentLoaded 事件：当HTML文档加载完成并解析完毕时触发
     * 就像"餐厅开门"，可以接待客户了
     */
    
    // 根据当前页面，初始化不同的功能
    if (document.getElementById('upload-area')) {
        // 如果在"上传任务"页面，初始化上传功能
        initUploadPage();
    }
    
    if (document.getElementById('model-selection')) {
        // 如果在"选择模型"页面，加载模型列表
        loadAvailableModels();
    }
    
    // 如果在结果页面，自动开始轮询
    if (document.getElementById('results-container')) {
        initResultsPage();
    }
});

/* ========================================
   上传任务页面功能
   ======================================== */

function initUploadPage() {
    /*
     * 初始化上传页面
     * 就像"准备点菜单"：告诉客户怎么点单
     */
    
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const startBtn = document.getElementById('start-evaluation');
    
    // ========== 点击上传区域，触发文件选择 ==========
    uploadArea.addEventListener('click', () => {
        /*
         * addEventListener：添加事件监听器
         * 就像"服务员盯着客户"，客户一点击，就弹出一个文件选择框
         */
        fileInput.click();  // 模拟点击隐藏的 <input type="file"> 元素
    });
    
    // ========== 文件选择变化（客户选了文件）==========
    fileInput.addEventListener('change', (e) => {
        /*
         * change 事件：当 <input> 的值变化时触发
         * 就像"客户把菜单递给服务员"
         */
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);  // 处理选中的文件
        }
    });
    
    // ========== 拖拽上传功能 ==========
    uploadArea.addEventListener('dragover', (e) => {
        /*
         * dragover 事件：当文件被拖到上传区域上方时触发
         * 就像"服务员看到客户拿着菜单走过来"
         */
        e.preventDefault();  // 阻止默认行为（防止浏览器打开文件）
        uploadArea.style.borderColor = '#667eea';  // 高亮边框（提示可以松手了）
    });
    
    uploadArea.addEventListener('dragleave', () => {
        /*
         * dragleave 事件：当文件拖离上传区域时触发
         * 就像"客户走开了"
         */
        uploadArea.style.borderColor = '#ddd';  // 恢复默认边框颜色
    });
    
    uploadArea.addEventListener('drop', (e) => {
        /*
         * drop 事件：当文件被拖放到上传区域时触发
         * 就像"客户把菜单放在柜台上"
         */
        e.preventDefault();  // 阻止默认行为
        uploadArea.style.borderColor = '#ddd';  // 恢复边框颜色
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);  // 处理拖放的文件
        }
    });
    
    // ========== 清除文件按钮 ==========
    document.getElementById('clear-file').addEventListener('click', () => {
        clearFileSelection();  // 清除文件选择
    });
    
    // ========== 权重滑块 ==========
    initWeightSliders();  // 初始化评估权重滑块
    
    // ========== 使用示例任务按钮 ==========
    document.getElementById('use-sample').addEventListener('click', () => {
        useSampleTasks();  // 使用示例任务
    });
    
    // ========== 开始评估按钮 ==========
    startBtn.addEventListener('click', () => {
        startEvaluation();  // 启动评估任务
    });
}

function handleFileSelect(file) {
    /*
     * 处理文件选择
     * 就像"服务员接过客户的菜单，检查有没有问题"
     */
    
    // 检查文件类型（必须是 .json 文件）
    if (!file.name.endsWith('.json')) {
        alert('请上传 JSON 格式的文件');  // alert：弹出警告框
        return;  // return：终止函数执行（就像"退单"）
    }
    
    selectedFile = file;  // 保存选中的文件
    
    // 显示文件信息（文件名、大小）
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('file-info').style.display = 'block';  // 显示文件信息区域
    document.getElementById('upload-area').style.display = 'none';  // 隐藏上传区域
    
    checkStartButton();  // 检查"开始评估"按钮是否可以点击
}

function clearFileSelection() {
    /*
     * 清除文件选择
     * 就像"客户说不要这个菜单了"
     */
    selectedFile = null;  // 清空选中的文件
    document.getElementById('file-input').value = '';  // 清空 <input> 的值
    document.getElementById('file-info').style.display = 'none';  // 隐藏文件信息
    document.getElementById('upload-area').style.display = 'block';  // 显示上传区域
    
    checkStartButton();  // 重新检查"开始评估"按钮
}

function formatFileSize(bytes) {
    /*
     * 格式化文件大小（字节 → KB/MB）
     * 就像"把重量从克转换成斤"
     */
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/* ========================================
   模型选择功能
   ======================================== */

async function loadAvailableModels() {
    /*
     * 加载可用的模型列表（从后端API获取）
     * 就像"展示菜单上有哪些菜"
     */
    
    try {
        // 调用后端API：GET /api/available-models
        const response = await fetch('/api/available-models');
        const data = await response.json();  // 解析JSON响应
        
        const modelSelection = document.getElementById('model-selection');
        modelSelection.innerHTML = '';  // 清空现有内容（防止重复加载）
        
        // 遍历模型列表，生成复选框
        data.models.forEach(model => {
            const checkbox = document.createElement('div');  // 创建一个 <div> 元素
            checkbox.className = 'model-checkbox';  // 设置CSS类名
            checkbox.innerHTML = `
                <label>
                    <input type="checkbox" value="${model.name}">
                    <strong>${model.display_name}</strong>
                    <span class="model-price">$${model.price_input}/1k tokens</span>
                </label>
            `;
            
            // 点击复选框，添加到 selectedModels 数组
            checkbox.querySelector('input').addEventListener('change', (e) => {
                const modelName = e.target.value;
                if (e.target.checked) {
                    selectedModels.push(modelName);  // 添加模型
                    checkbox.classList.add('selected');  // 添加选中样式
                } else {
                    selectedModels = selectedModels.filter(m => m !== modelName);  // 移除模型
                    checkbox.classList.remove('selected');  // 移除选中样式
                }
                checkStartButton();  // 重新检查"开始评估"按钮
            });
            
            modelSelection.appendChild(checkbox);  // 把复选框添加到页面
        });
        
        // 全选/全不选按钮
        document.getElementById('select-all').addEventListener('click', () => {
            selectAllModels(true);  // 全选
        });
        
        document.getElementById('deselect-all').addEventListener('click', () => {
            selectAllModels(false);  // 全不选
        });
        
    } catch (error) {
        console.error('加载模型列表失败：', error);  // 在浏览器控制台打印错误
        alert('加载模型列表失败，请刷新页面重试');
    }
}

function selectAllModels(select) {
    /*
     * 全选/全不选模型
     * 就像"服务员帮客户把所有菜都勾上"
     */
    const checkboxes = document.querySelectorAll('#model-selection input[type="checkbox"]');
    selectedModels = [];  // 清空已选模型
    
    checkboxes.forEach(cb => {
        cb.checked = select;  // 设置复选框状态
        if (select) {
            selectedModels.push(cb.value);  // 添加到数组
            cb.parentElement.parentElement.classList.add('selected');  // 添加选中样式
        } else {
            cb.parentElement.parentElement.classList.remove('selected');  // 移除选中样式
        }
    });
    
    checkStartButton();  // 重新检查"开始评估"按钮
}

/* ========================================
   评估权重滑块
   ======================================== */

function initWeightSliders() {
    /*
     * 初始化评估权重滑块
     * 就像"让客户调整口味偏好（咸淡）"
     */
    
    const costSlider = document.getElementById('cost-weight');
    const speedSlider = document.getElementById('speed-weight');
    const qualitySlider = document.getElementById('quality-weight');
    
    // 更新滑块值的显示
    function updateSliderDisplay() {
        document.getElementById('cost-weight-value').textContent = costSlider.value + '%';
        document.getElementById('speed-weight-value').textContent = speedSlider.value + '%';
        document.getElementById('quality-weight-value').textContent = qualitySlider.value + '%';
    }
    
    // 监听滑块变化
    [costSlider, speedSlider, qualitySlider].forEach(slider => {
        slider.addEventListener('input', () => {
            updateSliderDisplay();
            
            // 检查权重总和是否为100%
            const total = parseInt(costSlider.value) + parseInt(speedSlider.value) + parseInt(qualitySlider.value);
            const hint = document.querySelector('#advanced-section .hint');
            if (total !== 100) {
                hint.style.color = '#f5576c';  // 红色警告
                hint.textContent = `权重总和为 ${total}%，需要调整到100%`;
            } else {
                hint.style.color = '#888';  // 恢复灰色
                hint.textContent = '权重总和需为100%';
            }
        });
    });
    
    updateSliderDisplay();  // 初始化显示
}

/* ========================================
   启动评估任务
   ======================================== */

async function startEvaluation() {
    /*
     * 启动评估任务
     * 增强版：带详细状态反馈和错误提示
     */
    
    const startBtn = document.getElementById('start-evaluation');
    
    // 立即给按钮反馈：禁用+改变文字
    startBtn.disabled = true;
    const originalText = startBtn.textContent;
    startBtn.textContent = '⏳ 正在启动...';
    
    try {
        // 校验1：任务
        const fileNameEl = document.getElementById('file-name');
        const fileName = fileNameEl ? fileNameEl.textContent : '';
        const hasTask = selectedFile !== null || (fileName && fileName.includes('示例任务'));
        
        if (!hasTask) {
            alert('请先上传任务文件或点击"使用示例任务"');
            resetStartBtn(startBtn, originalText);
            return;
        }
        
        // 校验2：模型
        if (selectedModels.length === 0) {
            alert('请至少选择一个模型（勾选第二步里的模型复选框）');
            resetStartBtn(startBtn, originalText);
            return;
        }
        
        console.log('[智选] 开始评估，模型:', selectedModels.join(', '));
        
        // 读取文件内容（如果是上传的文件）
        let batchId = 'sample';  // 默认用示例任务
        
        if (selectedFile) {
            // 上传文件到后端
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('name', selectedFile.name);
            formData.append('description', '');
            
            startBtn.textContent = '📤 上传文件中...';
            
            try {
                const uploadResponse = await fetch('/api/upload-tasks', {
                    method: 'POST',
                    body: formData,
                });
                
                if (!uploadResponse.ok) {
                    let errMsg = '未知错误';
                    try { const ed = await uploadResponse.json(); errMsg = ed.detail || errMsg; } catch {}
                    alert('文件上传失败：' + errMsg);
                    resetStartBtn(startBtn, originalText);
                    return;
                }
                
                const uploadData = await uploadResponse.json();
                batchId = uploadData.batch_id;
                console.log('[智选] 文件上传成功，batchId:', batchId);
            } catch (error) {
                alert('文件上传网络失败：' + error.message);
                resetStartBtn(startBtn, originalText);
                return;
            }
        } else {
            console.log('[智选] 使用示例任务，batchId=sample');
        }
        
        // 获取评估权重
        const weights = {
            "cost": parseInt(document.getElementById('cost-weight').value) / 100,
            "speed": parseInt(document.getElementById('speed-weight').value) / 100,
            "quality": parseInt(document.getElementById('quality-weight').value) / 100,
        };
        
        // 调用后端API
        startBtn.textContent = '🚀 启动评估中...';
        
        const response = await fetch('/api/start-evaluation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                batch_id: batchId,
                model_names: selectedModels,
                weights: weights,
            }),
        });
        
        if (!response.ok) {
            let errMsg = `HTTP ${response.status}`;
            try { const ed = await response.json(); errMsg = ed.detail || errMsg; } catch {}
            alert('启动评估失败：' + errMsg + '\n\n请检查：\n1. 是否已选择至少一个模型\n2. 后台服务是否正常运行');
            resetStartBtn(startBtn, originalText);
            return;
        }
        
        const data = await response.json();
        
        if (!data.report_id) {
            alert('启动评估失败：后端未返回报告ID（可能服务异常）');
            resetStartBtn(startBtn, originalText);
            return;
        }
        
        currentReportId = data.report_id;
        console.log('[智选] 评估已启动，reportId:', currentReportId);
        
        // 显示进度区域
        document.getElementById('progress-section').style.display = 'block';
        
        // 初始化日志
        const detailLog = document.getElementById('detail-log');
        if (detailLog) {
            detailLog.innerHTML = '';
            addDetailLog(detailLog, '🚀 评估任务已提交，等待后台处理...', 'success');
            addDetailLog(detailLog, `📋 选中模型: ${selectedModels.join(', ')}`, 'info');
            addDetailLog(detailLog, `⚖️ 权重: 成本${(weights.cost*100).toFixed(0)}% / 速度${(weights.speed*100).toFixed(0)}% / 质量${(weights.quality*100).toFixed(0)}%`, 'info');
        }
        
        // 保持按钮禁用状态
        startBtn.textContent = '⏳ 评估进行中...';
        
        // 开始轮询
        pollEvaluationStatus(currentReportId);
        
    } catch (error) {
        console.error('[智选] startEvaluation 异常:', error);
        alert('发生未知错误：' + error.message + '\n\n请按 F12 打开控制台查看详细错误信息');
        resetStartBtn(startBtn, originalText);
    }
}

/* ---------- 恢复按钮状态 ---------- */
function resetStartBtn(btn, text) {
    btn.disabled = false;
    btn.textContent = text;
}

async function pollEvaluationStatus(reportId) {
    /*
     * 轮询评估进度（每隔2秒查询一次）
     * 增强版：显示评估细节（当前阶段、当前任务、模型状态、实时日志）
     */
    
    if (!reportId) {
        console.error('pollEvaluationStatus: reportId 无效', reportId);
        return;
    }
    
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const viewReportBtn = document.getElementById('view-report');
    
    // 细节面板元素
    const detailStage = document.getElementById('detail-stage');
    const detailTaskInfo = document.getElementById('detail-task-info');
    const detailModelStatus = document.getElementById('detail-model-status');
    const detailLog = document.getElementById('detail-log');
    const toggleDetail = document.getElementById('toggle-detail');
    const detailContent = document.getElementById('eval-detail-content');
    
    // 切换显示/隐藏细节
    if (toggleDetail) {
        toggleDetail.addEventListener('change', () => {
            detailContent.style.display = toggleDetail.checked ? 'block' : 'none';
        });
    }
    
    // 日志计数器，避免重复添加
    let lastLogCount = 0;
    
    try {
        const response = await fetch(`/api/evaluation-status/${reportId}`);
        
        if (!response.ok) {
            progressText.textContent = '查询进度失败（报告不存在或已过期）';
            addDetailLog(detailLog, '❌ 查询失败：报告不存在或已过期', 'error');
            return;
        }
        
        const status = await response.json();
        
        // 更新进度条
        progressFill.style.width = status.progress + '%';
        progressText.textContent = status.message;
        
        // ====== 更新细节面板 ======
        if (status.message) {
            // 解析当前阶段
            let stageText = '';
            if (status.message.includes('初始化')) {
                stageText = '🔧 阶段：初始化环境';
            } else if (status.message.includes('准备模型')) {
                stageText = '⚙️ 阶段：准备模型配置';
            } else if (status.message.includes('评估任务')) {
                stageText = '📋 阶段：逐任务评估中';
                // 提取任务信息: "正在评估任务 3/10: task_003"
                const taskMatch = status.message.match(/评估任务\s*(\d+)\/(\d+)\s*:\s*(.+)/);
                if (taskMatch) {
                    detailTaskInfo.innerHTML = `📝 当前任务：<strong>${taskMatch[3]}</strong>（${taskMatch[1]}/${taskMatch[2]}）`;
                    addDetailLog(detailLog, `▶️ 开始评估任务 ${taskMatch[1]}/${taskMatch[2]}: ${taskMatch[3]}`, 'info');
                }
            } else if (status.message.includes('汇总统计')) {
                stageText = '📊 阶段：生成汇总统计';
                addDetailLog(detailLog, '📊 正在计算汇总统计数据...', 'info');
            } else if (status.message.includes('推荐结论')) {
                stageText = '🏆 阶段：生成推荐结论';
                addDetailLog(detailLog, '🏆 正在分析最优模型...', 'info');
            } else if (status.message.includes('成本预测')) {
                stageText = '💰 阶段：生成成本预测';
                addDetailLog(detailLog, '💰 正在计算成本预测...', 'info');
            } else if (status.message.includes('报告')) {
                stageText = '📄 阶段：生成报告';
                addDetailLog(detailLog, '📄 正在生成最终报告...', 'info');
            } else if (status.message.includes('完成')) {
                stageText = '✅ 阶段：全部完成';
            } else if (status.message.includes('失败')) {
                stageText = '❌ 阶段：评估失败';
            } else {
                stageText = '⏳ 阶段：' + status.message;
            }
            
            if (detailStage) detailStage.textContent = stageText;
        }
        
        // 显示模型状态（从 completed_tasks 和 total_tasks 推断）
        if (status.total_tasks && status.completed_tasks !== undefined) {
            detailModelStatus.innerHTML = `✅ 已完成任务：<strong>${status.completed_tasks}</strong> / ${status.total_tasks}（${status.progress}%）`;
        }
        
        if (status.status === 'completed') {
            // 评估完成
            progressText.textContent = '评估完成！正在跳转...';
            viewReportBtn.style.display = 'inline-block';
            addDetailLog(detailLog, '🎉 评估全部完成！', 'success');
            viewReportBtn.onclick = () => {
                window.location.href = `/results/${reportId}`;
            };
            // 3秒后自动跳转
            setTimeout(() => {
                window.location.href = `/results/${reportId}`;
            }, 3000);
        } else if (status.status === 'failed') {
            progressText.textContent = '评估失败：' + status.message;
            progressFill.style.background = '#f5576c';
            addDetailLog(detailLog, '❌ 评估失败：' + status.message, 'error');
        } else {
            // 仍在运行，2秒后继续查询
            pollTimer = setTimeout(() => pollEvaluationStatus(reportId), 2000);
        }
        
    } catch (error) {
        console.error('查询进度失败：', error);
        addDetailLog(detailLog, '⚠️ 网络请求失败：' + error.message, 'warn');
        if (!pollEvaluationStatus.retryCount) {
            pollEvaluationStatus.retryCount = 0;
        }
        pollEvaluationStatus.retryCount++;
        
        if (pollEvaluationStatus.retryCount <= 3) {
            pollTimer = setTimeout(() => pollEvaluationStatus(reportId), 5000);
        } else {
            progressText.textContent = '查询进度失败，请刷新页面重试';
            addDetailLog(detailLog, '❌ 多次重试仍失败，请刷新页面', 'error');
        }
    }
}

/* ---------- 添加日志到细节面板 ---------- */
function addDetailLog(logElement, message, level = 'info') {
    /*
     * 在日志区域追加一行
     * level: info(蓝) / success(绿) / warn(橙) / error(红)
     */
    if (!logElement) return;
    
    const colors = { info: '#667eea', success: '#28a745', warn: '#f0ad4e', error: '#dc3545' };
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    
    const line = document.createElement('div');
    line.style.color = colors[level] || '#333';
    line.textContent = `[${time}] ${message}`;
    logElement.appendChild(line);
    logElement.scrollTop = logElement.scrollHeight;  // 自动滚动到底部
}

/* ========================================
   结果页面功能
   ======================================== */

function initResultsPage() {
    /*
     * 初始化结果页面
     * 就像"服务员把菜端上桌"
     */
    
    // 从URL获取报告ID
    const pathParts = window.location.pathname.split('/');
    const reportId = pathParts[pathParts.length - 1];
    
    if (reportId && reportId !== 'results') {
        currentReportId = reportId;
        // 开始轮询报告状态（如果报告还在生成中）
        pollEvaluationStatus(currentReportId);
    }
}

/* ========================================
   示例任务功能
   ======================================== */

function useSampleTasks() {
    /*
     * 使用示例任务
     * 就像"客户说：我不知道点什么，你推荐一下"
     */
    selectedFile = null;  // 清除上传的文件
    document.getElementById('file-name').textContent = '示例任务（5个测试任务）';
    document.getElementById('file-size').textContent = '';
    document.getElementById('file-info').style.display = 'block';
    document.getElementById('upload-area').style.display = 'none';
    
    checkStartButton();
}

function checkStartButton() {
    /*
     * 检查"开始评估"按钮是否可以点击
     * 就像"服务员检查：客户点完单了吗？可以下单了吗？"
     */
    
    const startBtn = document.getElementById('start-evaluation');
    const hint = document.getElementById('submit-hint');
    
    // 条件：有任务文件（或示例任务）且至少选择了一个模型
    const hasTask = selectedFile !== null || document.getElementById('file-name').textContent.includes('示例任务');
    const hasModels = selectedModels.length > 0;
    
    if (hasTask && hasModels) {
        startBtn.disabled = false;  // 启用按钮
        hint.style.display = 'none';  // 隐藏提示文字
    } else {
        startBtn.disabled = true;   // 禁用按钮
        hint.style.display = 'block';  // 显示提示文字
    }
}

/* ========================================
   工具函数
   ======================================== */

function showLoading(button, text = '处理中...') {
    /*
     * 显示加载状态（按钮变成"处理中..."并禁用）
     * 就像"服务员贴出'稍等'的牌子"
     */
    button.disabled = true;
    button.textContent = text;
}

function hideLoading(button, originalText) {
    /*
     * 隐藏加载状态（恢复按钮原样）
     * 就像"服务员把'稍等'的牌子收起来"
     */
    button.disabled = false;
    button.textContent = originalText;
}

function showError(message) {
    /*
     * 显示错误信息
     * 就像"服务员跟客户说：不好意思，出错了"
     */
    alert('错误：' + message);  // 简单用 alert 弹窗（正式项目应该用更友好的提示）
}

function showSuccess(message) {
    /*
     * 显示成功信息
     */
    alert('成功：' + message);
}
