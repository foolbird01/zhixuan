[Uploading 智选平台使用说明书.md…]()
# 智选平台使用说明书
## —— 逐行代码解析，小白也能懂

> **写给谁看的？**
> - 完全不懂代码，但想用AI模型选型的老板/CTO/技术负责人
> - 会一点代码，但想深入了解平台原理的开发者
> - 需要给企业做AI选型报告的分析师/咨询师
> 
> **本文特点：**
> - 用生活类比解释技术概念（像"餐厅点单"一样好懂）
> - 逐行解析代码（每一行都告诉你"这行是干嘛的"）
> - 配流程图和示例（看完就能上手）

---

## 目录

1. [项目介绍](#1-项目介绍)（用餐厅类比解释）
2. [安装配置](#2-安装配置)（手把手教）
3. [准备任务文件](#3-准备任务文件)（JSON格式说明）
4. [启动平台](#4-启动平台)（点击就能用）
5. [使用平台](#5-使用平台)（网页操作指南）
6. [解读评估报告](#6-解读评估报告)（每个数字的含义）
7. [逐文件代码解析](#7-逐文件代码解析)（核心！）
   - config.py 配置文件
   - models.py 数据模型
   - api_client.py API调用封装
   - evaluator.py 评估器
   - report_generator.py 报告生成器
   - main.py 主程序
8. [常见问题FAQ](#8-常见问题faq)

---

## 1. 项目介绍

### 1.1 这个平台能干什么？

**一句话概括：**
> 上传你的业务场景任务 → 平台自动调用多个AI模型执行 → 从成本、速度、质量三个维度打分 → 生成《AI模型选型与投资回报分析报告》

**生活类比：餐厅点菜**
> 你（企业）要办一场宴席（用AI处理业务），但不知道选哪家餐厅（哪个AI模型）。
> 
> "智选"平台就像"美食评委"：
> 1. 你把宴席菜单（业务任务）给评委
> 2. 评委去各家餐厅试菜（调用各个AI模型API）
> 3. 评委从口味（质量）、上菜速度（响应时间）、价格（成本）打分
> 4. 最后给你一份《餐厅推荐报告》（选型报告）

### 1.2 支持评估哪些模型？

| 服务商 | 模型名称 | 特点 | 价格（参考） |
|--------|---------|------|--------------|
| OpenAI | GPT-4o | 质量最高，价格中等 | $2.5/1M tokens 输入 |
| OpenAI | GPT-4o-mini | 便宜，速度最快 | $0.15/1M tokens 输入 |
| Anthropic | Claude 3.5 Sonnet | 长文本理解强 | $3/1M tokens 输入 |
| Anthropic | Claude 3 Haiku | 便宜，速度快 | $0.25/1M tokens 输入 |
| 阿里云 | 通义千问（Qwen-Turbo） | 国产，超便宜 | ¥0.3/1M tokens 输入 |
| DeepSeek | DeepSeek-Chat | 国产，质量接近GPT-4 | ¥1/1M tokens 输入 |

> **什么是 token？**
> - 1个英文单词 ≈ 1.3个token
> - 1个中文字 ≈ 2个token
> - 1000个token ≈ 750个英文单词 ≈ 500个中文字
> 
> **价格举例：**
> 如果你有100个客服问题，每个问题平均100字，总共约2万字的输入：
> - GPT-4o：约 $0.05（约 ¥0.35）
> - GPT-4o-mini：约 $0.003（约 ¥0.02）
> - 通义千问：约 ¥0.006（约 ¥0.06）
> 
> **结论：** 用国产模型测试，成本可以忽略不计！

### 1.3 评估维度说明

平台从三个维度评估模型：

| 维度 | 权重（默认） | 说明 | 生活类比 |
|------|--------------|------|----------|
| **成本** | 30% | API调用费用，越低越好 | 餐厅价格，越便宜越好 |
| **速度** | 20% | 响应时间（秒），越快越好 | 上菜速度，越快越好 |
| **质量** | 50% | 输出质量（1-10分），越高越好 | 菜品口味，越好吃越好 |

> **为什么质量占50%？**
> 因为企业用AI是为了解决问题，质量不行，再便宜也没用。
> 就像餐厅菜再便宜，难吃也没人去。

### 1.4 LLM-as-Judge 是什么？

**技术解释：**
用强大的AI模型（比如GPT-4o）当"评委"，给各个模型的回答打分（1-10分）。

**为什么不用人工打分？**
- 人工打分：慢（一个回答要几分钟）、贵（要请专家）、不一致（不同人打分标准不一样）
- AI评委：快（一个回答几秒钟）、便宜（GPT-4o-mini打分，1000条约$0.5）、一致（标准统一）

**生活类比：**
> 就像"美食选秀节目"：
> - 传统方式：请10个美食家试吃，打分（慢、贵、口味不同）
> - LLM-as-Judge：请一个"美食大师"（GPT-4o）当评委，统一标准打分（快、便宜、标准一致）

**研究表明：**
GPT-4o当评委，打分结果跟人类专家的相关性 > 0.8（满分1.0），非常可靠！

---

## 2. 安装配置

### 2.1 系统要求

| 项目 | 要求 | 说明 |
|------|------|------|
| 操作系统 | Windows 10/11、macOS、Linux | 都能用 |
| Python | 3.10 或以上 | 推荐 3.11（速度快） |
| 内存 | 4GB 以上 | 平台本身不占多少内存 |
| 硬盘 | 1GB 以上 | 主要存报告文件 |
| 网络 | 能访问AI模型API | 需要调用OpenAI/Anthropic等API |

### 2.2 安装 Python（如果还没有）

**Windows 用户：**
1. 访问 https://www.python.org/downloads/
2. 下载最新版（比如 Python 3.12）
3. 安装时**务必勾选** "Add Python to PATH"（添加到环境变量）
4. 安装完成后，打开"命令提示符"（按 Win+R，输入 `cmd`，回车）
5. 输入 `python --version`，看到版本号说明安装成功

**macOS 用户：**
1. 打开"终端"（在"应用程序/实用工具"里）
2. 输入 `python3 --version`
3. 如果没安装，会提示你安装"命令行开发者工具"，点击"安装"即可

**Linux 用户：**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### 2.3 下载项目代码

**方式一：Git 克隆（推荐）**
```bash
git clone https://github.com/your-repo/zixuan.git
cd zixuan
```

**方式二：下载 ZIP**
1. 访问项目GitHub页面
2. 点击绿色的 "Code" 按钮 → "Download ZIP"
3. 解压到任意目录（比如 `D:\agent\zixuan\`）

### 2.4 安装依赖包

打开"命令提示符"或"终端"，进入项目目录，执行：

```bash
cd D:\agent\zixuan   # Windows 用户
# 或
cd /path/to/zixuan   # macOS/Linux 用户

# 安装依赖（就像"买菜"，把需要的包都买回来）
pip install -r requirements.txt
```

**安装过程说明：**
```
Collecting fastapi==0.115.0  # 下载 FastAPI 框架
  Downloading fastapi-0.115.0-py3-none-any.whl (88 kB)
Collecting uvicorn==0.30.6  # 下载 ASGI 服务器（用来运行 FastAPI）
  Downloading uvicorn-0.30.6-py3-none-any.whl (58 kB)
...
Installing collected packages: ...  # 安装所有包
Successfully installed ...           # 安装成功！
```

**如果安装很慢（国内用户）：**
```bash
# 使用清华镜像源（速度快10倍）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.5 配置 API Key

**什么是 API Key？**
就像"餐厅会员卡"，有了它才能调用AI模型的API（点菜）。

**配置步骤：**

1. **复制示例文件：**
   ```bash
   cp .env.example .env   # macOS/Linux
   # 或手动复制 .env.example，重命名为 .env
   ```

2. **编辑 `.env` 文件（用记事本或VS Code）：**
   ```env
   # 至少填一个API Key，想测哪个模型就填哪个
   OPENAI_API_KEY=sk-abc123...          # GPT模型需要
   ANTHROPIC_API_KEY=sk-ant-abc123...  # Claude模型需要
   DASHSCOPE_API_KEY=sk-abc123...      # 通义千问需要
   DEEPSEEK_API_KEY=sk-abc123...       # DeepSeek需要
   ```

3. **获取 API Key 的详细步骤：**

   **OpenAI API Key：**
   1. 访问 https://platform.openai.com/api-keys
   2. 登录（没有账号先注册）
   3. 点击 "Create new secret key"
   4. 复制生成的 Key（以 `sk-` 开头）
   5. **注意：** 新用户有 $5 免费额度（有效期3个月）

   **Anthropic API Key：**
   1. 访问 https://console.anthropic.com/settings/keys
   2. 登录（没有账号先注册）
   3. 点击 "Create Key"
   4. 复制生成的 Key（以 `sk-ant-` 开头）
   5. **注意：** Anthropic 暂无免费额度，需要先充值

   **阿里云百炼 API Key（推荐！便宜！）：**
   1. 访问 https://dashscope.aliyuncs.com/
   2. 登录（用支付宝/淘宝账号）
   3. 点击 "API Key管理" → "创建API Key"
   4. 复制生成的 Key（以 `sk-` 开头）
   5. **注意：** 新用户赠送 100万 tokens 免费额度！

   **DeepSeek API Key（超便宜！）：**
   1. 访问 https://platform.deepseek.com/
   2. 注册/登录
   3. 点击 "API Keys" → "Create new API key"
   4. 复制生成的 Key（以 `sk-` 开头）
   5. **注意：** 充值 $2 能用很久！

### 2.6 测试配置是否成功

执行以下命令（测试是否能调用API）：

```bash
python -c "import openai; client = openai.OpenAI(); print('OpenAI SDK 安装成功')"
```

如果不报错，说明配置成功！

---

## 3. 准备任务文件

### 3.1 什么是"任务文件"？

**定义：**
一个JSON格式的文件，里面包含你要测试的业务场景任务。

**生活类比：**
> 就像"宴席菜单"：
> - 每道菜 = 一个任务
> - 菜名 = 任务指令（比如"请把这段话总结成100字"）
> - 食材 = 输入文本（比如"要总结的那段话"）

### 3.2 任务文件格式（JSON）

```json
[
  {
    "id": "task_001",                 /* 任务ID（唯一标识，不能重复） */
    "task_type": "summarization",      /* 任务类型：qa（问答）、summarization（总结）、code_generation（代码生成）等 */
    "instruction": "请把以下这段话总结成100字以内：",  /* 任务指令（告诉模型要做什么） */
    "input_text": "人工智能（AI）是计算机科学的一个分支...（很长的一段话）",  /* 输入文本（可选） */
    "reference_output": "人工智能是计算机科学分支...（参考答案）",  /* 参考答案（可选，用来对比质量） */
    "expected_keywords": ["人工智能", "计算机科学", "分支"]  /* 期望关键词（可选，用来检查回答是否覆盖要点） */
  },
  {
    "id": "task_002",
    "task_type": "qa",
    "instruction": "用户问：'你们店支持7天无理由退货吗？' 请按照优质电商客服的标准回复。",
    "input_text": "",
    "reference_output": "亲，我们是支持7天无理由退货的哦！...",
    "expected_keywords": ["7天", "无理由", "退货", "支持"]
  }
]
```

### 3.3 任务类型说明

| 任务类型 | 说明 | 示例场景 |
|---------|------|----------|
| `qa` | 问答 | 客服自动回复、知识库问答 |
| `summarization` | 文本总结 | 长文档总结、会议记录摘要 |
| `code_generation` | 代码生成 | 自动写SQL、自动写Python脚本 |
| `translation` | 翻译 | 中文→英文、英文→中文 |
| `report_generation` | 报告生成 | 根据数据自动生成销售报告 |
| `classification` | 分类 | 情感分析、垃圾邮件识别 |

### 3.4 如何创建任务文件？

**方式一：用示例代码（推荐）**

项目自带了 `data/sample_tasks.json`（10个客服场景任务），可以直接用。

**方式二：手动编写**

1. 打开记事本或VS Code
2. 按照上面的JSON格式编写
3. 保存为 `my_tasks.json`（注意编码选UTF-8）

**方式三：用Excel生成（适合大量任务）**

1. 在Excel里填写任务（每行一个任务）
2. 用"另存为" → "CSV（逗号分隔）(*.csv)"
3. 用在线工具把CSV转成JSON（搜索"CSV to JSON"）

### 3.5 任务数量建议

| 用途 | 建议任务数 | 说明 |
|------|----------|------|
| 快速测试 | 5-10个 | 先跑通流程，看看平台好不好用 |
| 正式评估 | 50-100个 | 覆盖主要业务场景，评估结果更可靠 |
| 生产决策 | 200-500个 | 大规模测试，结果可用于CTO/CFO汇报 |

> **成本提醒：**
> 100个任务 × 5个模型 = 500次API调用
> - 如果用 GPT-4o-mini：约 $0.5
> - 如果用通义千问：约 ¥0.5
> 
> **建议：** 先用国产模型测试，调通后再用GPT-4o正式评估。

---

## 4. 启动平台

### 4.1 启动命令

在项目根目录执行：

```bash
python main.py
```

**看到以下输出说明启动成功：**

```
============================================================
🚀 智选 - AI模型选型平台
============================================================

📌 启动说明：
  1. 请确保已安装依赖：pip install -r requirements.txt
  2. 请确保 .env 文件已配置 API Key
  3. 启动后访问：http://localhost:8000

📌 配置说明：
  在项目根目录创建 .env 文件，写入：
  OPENAI_API_KEY=sk-xxxxxxxxxxxx
  ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
  DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
  DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

============================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.2 访问平台

打开浏览器（Chrome/Edge/Safari都行），访问：

```
http://localhost:8000
```

**如果打不开：**
- 检查是否看到"Uvicorn running on..."的提示
- 检查端口是否被占用（改成其他端口，比如 `python main.py --port 8080`）
- 检查防火墙是否拦截

### 4.3 停止平台

在命令提示符窗口按 `Ctrl + C`（就像"关餐厅门"）

---

## 5. 使用平台

### 5.1 首页介绍

打开 http://localhost:8000 后，你会看到：

```
┌─────────────────────────────────────────────┐
│  🧠 智选 - AI模型选型平台                 │
│    自动化评估 · 量化成本效益 · 数据驱动决策 │
└─────────────────────────────────────────────┘

【功能卡片】
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 🎯 量化评估  │ 🤖 LLM-as-  │ 📈 成本预测  │ 📄 决策报告  │
│             │    Judge     │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘

【开始使用按钮】
  [开始评估]  [了解工作原理]
```

### 5.2 上传任务文件

**步骤：**
1. 点击顶部导航的 "上传任务"
2. 拖拽你的JSON文件到上传区域（或点击选择文件）
3. 如果没准备文件，可以点击 "使用示例任务"

**页面布局：**
```
┌─────────────────────────────────────────────┐
│  📤 上传任务样本                           │
│    上传您的业务场景任务，或直接使用示例任务  │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐  │
│  │  📁                                 │  │
│  │  点击或拖拽文件到这里                │  │
│  │  支持 JSON 格式，包含 "tasks" 字段  │  │
│  └─────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│  【第二步：选择要评估的模型】               │
│  ☑ GPT-4o-mini  ☑ GPT-4o                │
│  ☑ Claude 3.5 Sonnet  ☑ 通义千问        │
│  [全选]  [全不选]                         │
├─────────────────────────────────────────────┤
│  【第三步：高级设置（可选）】               │
│  成本权重：====●=== 30%                   │
│  速度权重：=====●== 20%                   │
│  质量权重：=======● 50%                   │
├─────────────────────────────────────────────┤
│  [开始评估]  （按钮，点击后变灰色"处理中"）│
└─────────────────────────────────────────────┘
```

### 5.3 查看评估进度

点击"开始评估"后，页面会显示进度条：

```
┌─────────────────────────────────────────────┐
│  📊 评估进度                               │
├─────────────────────────────────────────────┤
│  ████████████████░░░░░░░░  60%            │
│  正在评估任务 6/10: task_006               │
└─────────────────────────────────────────────┘
```

**评估时间估算：**
- 10个任务 × 5个模型 = 50次API调用
- 每次调用约2-5秒（取决于模型速度和网络）
- 总时间约 5-10 分钟

> **提示：** 评估是在后台运行的，关闭浏览器不会影响评估进程。

### 5.4 查看评估报告

评估完成后，点击"查看报告"按钮，会跳转到结果页面：

```
┌─────────────────────────────────────────────┐
│  📊 评估报告                               │
│  报告ID: report_a1b2c3 | 生成时间: ...    │
├─────────────────────────────────────────────┤
│  【执行摘要】                               │
│  ┌─────────┬─────────┬─────────┬────────┐│
│  │ 模型     │ 综合得分 │ 质量得分 │ 总成本  ││
│  ├─────────┼─────────┼─────────┼────────┤│
│  │GPT-4o   │ 8.5     │ 9.2     │ $0.15  ││
│  │通义千问  │ 7.8     │ 7.5     │ $0.002 ││
│  └─────────┴─────────┴─────────┴────────┘│
├─────────────────────────────────────────────┤
│  【推荐结论】                               │
│  🏆 综合最优模型：GPT-4o                  │
│  💰 性价比最高模型：通义千问               │
├─────────────────────────────────────────────┤
│  【详细评估结果】                           │
│  [任务1] [任务2] [任务3] ...              │
│  （点击任务标签查看详情）                    │
├─────────────────────────────────────────────┤
│  【下载完整报告】                           │
│  [下载 Markdown] [下载 HTML] [下载 PDF]    │
└─────────────────────────────────────────────┘
```

---

## 6. 解读评估报告

### 6.1 综合得分怎么算的？

**公式：**
```
综合得分 = 成本得分 × 30% + 速度得分 × 20% + 质量得分 × 50%
```

**详细解释：**

| 维度 | 得分范围 | 计算方式 | 示例 |
|------|---------|---------|------|
| 成本得分 | 0-10分 | 成本越低分越高（用指数函数归一化） | 成本$0.001 → 9.5分<br>成本$0.1 → 3.7分 |
| 速度得分 | 0-10分 | <1秒=10分，>10秒=3分（线性递减） | 0.5秒 → 10分<br>5秒 → 7分 |
| 质量得分 | 1-10分 | LLM评委打分（1-10分） | 9.2分（优秀） |

**示例计算：**
```
模型A：成本$0.01（得分8.2），速度2秒（得分8.5），质量8.5分
综合得分 = 8.2×0.3 + 8.5×0.2 + 8.5×0.5 = 8.46分

模型B：成本$0.001（得分9.5），速度1秒（得分10），质量7.0分
综合得分 = 9.5×0.3 + 10×0.2 + 7.0×0.5 = 8.55分

结论：模型B性价比更高（虽然质量稍差，但成本低很多）
```

### 6.2 质量评分标准

| 分数 | 等级 | 说明 | 企业应用建议 |
|------|------|------|-------------|
| 9-10分 | 优秀 | 回答准确、完整、清晰，可直接用于生产 | ✅ 强烈推荐 |
| 7-8分 | 良好 | 回答基本准确，偶尔有小错误 | ✅ 可以使用，建议人工审核 |
| 5-6分 | 及格 | 回答部分准确，需要较多人工修改 | ⚠️ 谨慎使用，必须人工审核 |
| 0-4分 | 不及格 | 回答错误多，或完全不相关 | ❌ 不推荐使用 |

### 6.3 成本预测表怎么看？

**表格示例：**

| 月调用量 | GPT-4o | GPT-4o-mini | 通义千问 |
|---------|---------|--------------|----------|
| 1,000次 | $0.15 | $0.009 | ¥0.06 |
| 10,000次 | $1.5 | $0.09 | ¥0.6 |
| 100,000次 | $15 | $0.9 | ¥6 |

**如何决策？**
> 如果你的业务月调用量是10万次：
> - 用 GPT-4o：每月 $15（约¥105）
> - 用 GPT-4o-mini：每月 $0.9（约¥6.3）
> - 用通义千问：每月 ¥6
> 
> **如果质量差距不大（比如8.5分 vs 8.0分），建议用便宜的模型，一年能省几千块！**

### 6.4 报告里的"评分理由"是什么？

**定义：**
LLM评委在打分后，会生成一段文字说明"为什么打这个分"。

**示例：**
```
模型：GPT-4o
任务：用户问"你们店支持7天无理由退货吗？"
评分：9分
理由：回答准确（明确说"支持"），友好（用了"亲"等称呼），
      引导行动（"需要的话我可以帮您发起退货申请"），
      符合优质客服标准。扣1分是因为没提到"不影响二次销售"等细节。
```

**用途：**
- 帮你理解为什么这个模型得分高/低
- 给人工审核提供参考（哪些地方需要改进）
- 用于向CTO/CFO汇报（"为什么推荐这个模型"）

---

## 7. 逐文件代码解析

> **本章目标：**
> 让你读懂平台的每一行代码，知道"为什么会这样写"。
> 
> **阅读建议：**
> - 如果你是完全不懂代码的小白：跳过本章，直接用平台就行
> - 如果你是会一点代码的开发者：建议通读，能帮你深入理解平台原理
> - 如果你是要修改平台的企业开发者：必须读！每一行都很重要

---

### 7.1 config.py —— 配置文件

**文件路径：** `D:\agent\zixuan\config.py`

**作用：**
就像餐厅的"设置菜单"，里面定义了：
- 支持哪些模型（就像菜单上有哪些菜）
- 每个模型的价格（就像菜品价格）
- API Key 存在哪里（就像"会员卡"放在哪个抽屉）

**逐行解析：**

```python
"""
配置文件 - 放所有的配置项
就像餐厅的"设置菜单"，哪些模型可以用、价格是多少，都写在这里
"""
```
> **生活类比：**
> 就像餐厅开业前，老板要写一份"菜单"：
> - 有什么菜（支持哪些模型）
> - 每道菜多少钱（模型的价格）
> - 厨房在哪里（API地址）
> 
> **为什么要单独写个配置文件？**
> 因为模型和价格会经常变（就像菜价会涨会跌），
> 如果把这些信息写在"做菜的程序"里，每次改都要翻代码，很麻烦。
> 单独写个配置文件，改起来方便。

```python
import os
from dotenv import load_dotenv

# 加载 .env 文件里的API Key（这样不用把密钥写死在代码里）
load_dotenv()
```
> **`import os` 是干什么的？**
> `os` 是Python的"系统操作库"，可以读取系统的环境变量。
> 就像"管家"，能帮你从"抽屉"（环境变量）里拿东西（API Key）。
> 
> **`from dotenv import load_dotenv` 是干什么的？**
> `python-dotenv` 是一个第三方库，能读取项目根目录的 `.env` 文件。
> 就像"秘书"，帮你把 `.env` 文件里的配置读出来，放到"抽屉"里。
> 
> **为什么要这么做？**
> 因为 API Key 是机密信息（就像银行卡密码），不能写在代码里。
> 如果代码泄露（比如传到了GitHub），黑客就能拿到你的API Key，用你的钱！
> 所以要把API Key放在 `.env` 文件里，并且把 `.env` 加到 `.gitignore`（不让Git管理）。
> 
> **`.env` 文件示例：**
> ```
> OPENAI_API_KEY=sk-abc123...
> ```
> 
> **代码里怎么用？**
> ```python
> api_key = os.getenv("OPENAI_API_KEY")  # 从"抽屉"里拿出 API Key
> ```

```python
# ==================== 支持的模型列表 ====================
# 就像菜单一样，告诉系统"我们能点哪些模型"
# 每个模型有：名字、调用方式、价格（每1000个token多少钱）

AVAILABLE_MODELS = {
```
> **`AVAILABLE_MODELS` 是什么？**
> 这是一个"字典"（dictionary），就像"电话本"：
> - 键（key）：模型名称（比如 `"gpt-4o-mini"`）
> - 值（value）：模型的详细配置（是个字典）
> 
> **为什么要定义这个？**
> 因为平台需要知道"能调用哪些模型"，以及"调用它们要花多少钱"。
> 就像餐厅需要知道"菜单上有哪些菜"，以及"每道菜多少钱"。

```python
    # OpenAI 的模型
    "gpt-4o-mini": {
        "provider": "openai",                    # 服务商：OpenAI
        "model_id": "gpt-4o-mini",             # 模型ID（调用API时用）
        "price_per_1k_input": 0.00015,         # 输入价格：$0.00015/1k tokens
        "price_per_1k_output": 0.0006,        # 输出价格：$0.0006/1k tokens
        "speed": "fast",                        # 速度快慢
        "context_window": 128000,               # 上下文窗口（能记住多少字）
    },
```
> **`"provider": "openai"` 是什么意思？**
> 告诉系统"这个模型是OpenAI家的"，调用时要用OpenAI的API格式。
> 就像"这道菜是川菜"，要做的话得按川菜的做法。
> 
> **为什么输入和输出价格不一样？**
> 因为AI模型"说"（输出）比"听"（输入）更耗算力。
> 就像餐厅里，"做菜"（输出）比"看菜单"（输入）更费时间。
> 
> **`"context_window": 128000` 是什么意思？**
> 上下文窗口就像模型的"短期记忆"：
> - 你能跟它聊多少字（输入+输出），超过就"忘事"了
> - 128000 tokens ≈ 10万字（一本中篇小说的量）
> 
> **为什么要关心这个？**
> 如果你的任务需要输入很长的文档（比如10万字），
> 就要选上下文窗口大的模型（比如Claude 3.5 Sonnet，支持200000 tokens）。

```python
    # 国产模型（兼容OpenAI格式）
    "qwen-turbo": {
        "provider": "openai_compatible",        # 用OpenAI的方式调用
        "model_id": "qwen-turbo",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云底座
        "price_per_1k_input": 0.0001,         # 国产模型便宜很多
        "price_per_1k_output": 0.0001,
        "speed": "fast",
        "context_window": 131072,
    },
```
> **`"provider": "openai_compatible"` 是什么意思？**
> 阿里云、DeepSeek等国产模型，为了吸引开发者，
> 故意把API格式做得跟OpenAI一模一样。
> 这样开发者只需要改个"网址"（api_base），就能用原来的代码调用国产模型。
> 
> 就像"山寨充电器"，虽然牌子不一样，但接口跟原装的一样，能通用。
> 
> **`"api_base"` 是什么？**
> 这是国产模型的API地址（就像"餐厅在哪条街"）。
> OpenAI的API地址是 `https://api.openai.com/v1`，
> 阿里云的API地址是 `https://dashscope.aliyuncs.com/compatible-mode/v1`。
> 
> **为什么国产模型便宜？**
> 因为国产模型的算力成本低（用国产GPU），
> 而且政府在补贴（就像"新能源汽车补贴"）。

```python
# ==================== API Key 配置 ====================
# 从环境变量读取（安全！不会泄露密钥）
# 使用方式：在项目根目录创建 .env 文件，写入：
# OPENAI_API_KEY=sk-xxxxxxxxxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
# DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # 第二个参数是"默认值"（如果没找到，返回空字符串）
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")   # 阿里云百炼
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
```
> **`os.getenv("OPENAI_API_KEY", "")` 是干什么的？**
> 从环境变量里读取 `OPENAI_API_KEY`。
> 如果没找到（比如用户没填），返回空字符串 `""`。
> 
> **为什么要设默认值？**
> 因为如果用户没填API Key，我们不希望程序"崩溃"（报错），
> 而是"温柔地"设个空值，后续调用时再提示"请配置API Key"。
> 
> 就像"如果客户没带钱，先让他记账，而不是直接赶人"。

```python
# ==================== 评估配置 ====================
# LLM-as-Judge 用来评估质量（用强大的模型当"评委"）
JUDGE_MODEL = "gpt-4o-mini"               # 评委模型（便宜又够用）
QUALITY_SCORE_THRESHOLDS = {                # 质量评分阈值
    "excellent": 9,                         # 9-10分：优秀
    "good": 7,                              # 7-8分：良好
    "acceptable": 5,                         # 5-6分：及格
    "poor": 0,                              # 0-4分：不及格
}

# ==================== 报告配置 ====================
REPORT_OUTPUT_DIR = "reports"                # 报告保存位置
TEMPLATE_DIR = "templates"                  # 报告模板位置

# ==================== 默认评估维度权重 ====================
# 企业可以根据自己的需求调整这些权重
DEFAULT_WEIGHTS = {
    "cost": 0.3,           # 成本占30%权重
    "speed": 0.2,          # 速度占20%权重
    "quality": 0.5,        # 质量占50%权重（质量最重要）
}
```
> **`JUDGE_MODEL = "gpt-4o-mini"` 是什么意思？**
> 指定用哪个模型当"评委"。
> 默认用 `gpt-4o-mini`（便宜，打分质量也不错）。
> 
> **能不能换成其他模型？**
> 能！比如换成 `gpt-4o`（更准，但贵3倍），
> 或者换成 `claude-3-haiku`（便宜，但打分质量稍差）。
> 
> **`DEFAULT_WEIGHTS` 是什么？**
> 这是评估维度的"重要性占比"：
> - 成本占 30%（不是越便宜越好，要综合考虑）
> - 速度占 20%（响应快用户体验好，但不是最重要）
> - 质量占 50%（这是核心！质量不行，再便宜也没用）
> 
> **企业能改权重吗？**
> 能！比如你的业务"对成本极其敏感"（比如创业公司），
> 可以把成本权重调高到 50%，质量降到 30%。

---

### 7.2 models.py —— 数据模型定义

**文件路径：** `D:\agent\zixuan\models.py`

**作用：**
定义平台里用到的所有"数据结构"（就像餐厅的"点菜单格式"）。

**为什么要定义数据模型？**
> 因为Python是"动态语言"（变量类型不固定），
> 如果不事先定义数据结构，代码里容易出现"这个字段叫什么来着？"的问题。
> 
> 用 Pydantic 定义数据模型后：
> 1. 代码有"自动补全"（IDE知道有哪些字段）
> 2. 有"类型检查"（如果字段类型错了，会报错）
> 3. 能自动生成API文档（FastAPI的功能）
> 
> 就像餐厅规定"点菜单必须包含：菜名、数量、备注"，
> 服务员就不会漏填信息。

**逐行解析：**

```python
"""
数据模型定义 - 用 Pydantic 定义数据结构
就像餐厅的"点菜单格式"，规定什么样的数据才是合法的
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
```
> **`from pydantic import BaseModel, Field` 是干什么的？**
> Pydantic 是Python的"数据验证库"。
> - `BaseModel`：所有数据模型的"基类"（就像"生物"是所有动物的基类）
> - `Field`：用来给字段加"说明"和"默认值"
> 
> **`from typing import List, Optional, Dict, Any` 是干什么的？**
> typing 是Python的"类型提示库"。
> - `List`：列表（比如 `[1, 2, 3]`）
> - `Optional`：可选（可以是"有值"，也可以是 `None`）
> - `Dict`：字典（比如 `{"name": "GPT-4o"}`）
> - `Any`：任意类型（可以是字符串、数字、列表...）
> 
> **为什么要类型提示？**
> 为了让代码"可读性更好"，也方便IDE做"类型检查"。
> 就像餐厅的"点菜单"上写明"数量：数字"，服务员就不会填"一份"这种模糊的答案。

```python
# ==================== 任务类型枚举 ====================
class TaskType(str, Enum):
    """任务类型 - 企业常见的AI任务"""
    QA = "qa"                        # 问答（客服场景）
    SUMMARIZATION = "summarization"  # 总结/摘要
    CODE_GENERATION = "code_generation"  # 代码生成
    TRANSLATION = "translation"       # 翻译
    REPORT_GENERATION = "report_generation"  # 报告生成
    CLASSIFICATION = "classification" # 分类
```
> **`class TaskType(str, Enum):` 是干什么的？**
> 定义一个"枚举类"（Enum），就像"下拉菜单"：
> - 只能选固定的几个值（不能乱填）
> - 比如 `task_type` 只能是 `qa`、`summarization` 等，不能是 `abc123`
> 
> **为什么要继承 `str`？**
> 因为枚举值要当成"字符串"存到数据库/JSON里。
> 如果不继承 `str`，存进去的会是 `TaskType.QA`（带类型信息），而不是 `"qa"`。
> 
> **生活类比：**
> 就像餐厅的"口味选择"：只能是"微辣"、"中辣"、"特辣"，不能是"辣度5.3"。

```python
# ==================== 任务数据模型 ====================
class TaskSample(BaseModel):
    """单个任务样本 - 就像考试的一道题"""
    id: str = Field(..., description="题目ID，比如 'task_001'")
    task_type: TaskType = Field(..., description="任务类型")
    instruction: str = Field(..., description="任务指令，比如'请把下面这段话总结成100字'")
    input_text: str = Field("", description="输入文本，比如要总结的那段话")
    reference_output: Optional[str] = Field(None, description="参考答案（可选），用来对比质量")
    expected_keywords: List[str] = Field(default=[], description="期望出现的关键词，比如['总结','核心']")
```
> **`class TaskSample(BaseModel):` 是干什么的？**
> 定义一个"任务样本"的数据结构。
> 每个任务样本是一道"考试题"，包含：
> - `id`：题目ID（唯一标识）
> - `instruction`：题目要求（比如"总结这段话"）
> - `input_text`：输入内容（比如"要总结的那段话"）
> 
> **`Field(..., description="...")` 是什么意思？**
> - `...`（三个点）表示"必填字段"（不能为空）
> - `description` 是字段的说明（会显示在API文档里）
> 
> **`Optional[str] = Field(None, ...)` 是什么意思？**
> - `Optional[str]` 表示"可以是字符串，也可以是 `None`"
> - `default=None` 表示"默认值是 `None`"（用户不填就是 `None`）
> 
> **生活类比：**
> 就像"点菜单"上：
> - 菜名（必填，不能空着）
> - 备注（可选，可以不填）

```python
    class Config:
        use_enum_values = True   # 让枚举值以字符串形式存储
```
> **`class Config:` 是干什么的？**
> 这是 Pydantic 模型的"配置类"。
> 
> **`use_enum_values = True` 是什么意思？**
> 让枚举字段存成"值"（字符串），而不是"枚举对象"。
> 比如 `task_type` 存成 `"qa"`，而不是 `TaskType.QA`。
> 
> **为什么要这样？**
> 因为存到JSON/数据库时，"字符串"更通用（其他程序也能读）。

```python
class TaskBatch(BaseModel):
    """一批任务 - 就像一套试卷"""
    batch_id: str = Field(..., description="批次ID")
    name: str = Field(..., description="批次名称，比如'客服问答测试集'")
    description: Optional[str] = Field("", description="批次描述")
    tasks: List[TaskSample] = Field(..., description="任务列表")
    created_at: Optional[str] = Field(None, description="创建时间")
```
> **`tasks: List[TaskSample]` 是什么意思？**
> 表示 `tasks` 字段是一个"列表"，里面的每个元素都是 `TaskSample` 类型。
> 
> **为什么要这样定义？**
> 因为一批任务包含多个"题目"（TaskSample），
> 用列表能把这些题目"打包在一起"。
> 
> **生活类比：**
> 就像"一套试卷"包含"多道题"，
> `TaskBatch` 是试卷，`TaskSample` 是题目。

---

### 7.3 api_client.py —— API调用封装

**文件路径：** `D:\agent\zixuan\api_client.py`

**作用：**
封装所有大模型API调用（就像餐厅的"传菜员"）。

**为什么要封装？**
> 因为不同模型（OpenAI、Anthropic、国产模型）的API格式都不一样：
> - OpenAI：`client.chat.completions.create(...)`
> - Anthropic：`client.messages.create(...)`
> - 国产模型：跟OpenAI格式一样，但要改 `base_url`
> 
> 如果每次调用都写一堆 `if...else`，代码会很难看。
> 所以封装成一个统一的接口：`call_model(instruction, input_text)`，
> 不管什么模型，都用这个方法调用。
> 
> 就像"万能充电器"，不管什么手机（模型），都能充电（调用API）。

**逐行解析：**

```python
"""
API客户端 - 封装所有大模型API调用
就像一个"翻译官"，不管什么模型，都用统一的接口调用
企业只需要说"我要用GPT-4o"，不用管底层怎么调API
"""

import time
import json
from typing import List, Dict, Any, Optional
import openai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
```
> **`import time` 是干什么的？**
> time 是Python的"时间库"，用来：
> - 计时（看看API调用花了多少秒）
> - 等待（如果失败了，等几秒再重试）
> 
> **`from tenacity import retry, stop_after_attempt, wait_exponential` 是干什么的？**
> tenacity 是Python的"重试库"。
> - `@retry`：给函数加"重试功能"（就像"这道题不会，再做一次"）
> - `stop_after_attempt(3)`：最多重试3次（别无限重试，浪费时间）
> - `wait_exponential`：每次重试前等待的时间"指数增长"（1秒、2秒、4秒...）
> 
> **为什么要重试？**
> 因为API调用偶尔会失败：
> - 网络抖动（就像"电话断了"）
> - API限流（就像"餐厅客满，请稍后再来"）
> 
> 如果不重试，一次失败就"放弃"了，很浪费。
> 所以加个重试机制，提高成功率。

```python
class ModelAPIClient:
    """
    模型API客户端 - 统一调用接口
    
    为什么需要这个？
    - OpenAI、Anthropic、国产模型的API格式都不一样
    - 这个客户端把它们"统一"成一个接口
    - 就像万能充电器，不管什么手机都能充
    """
```
> **`class ModelAPIClient:` 是干什么的？**
> 定义一个"类"（Class），就像"图纸"：
> - 可以创建多个"实例"（比如 `client1 = ModelAPIClient()`）
> - 每个实例都有相同的"方法"（比如 `call_model()`）
> 
> **为什么要写成"类"？**
> 因为：
> 1. 可以保存"状态"（比如 `self.openai_client`，这样不用每次都重新创建）
> 2. 可以封装"方法"（把相关的函数组织在一起）
> 
> 就像"餐厅"是个类，可以开多家分店（实例），每家分店都有相同的功能（点菜、做菜、结账）。

```python
    def __init__(self):
        """初始化各个服务商的客户端"""
        
        # OpenAI 客户端（也兼容国产模型）
        self.openai_client = openai.OpenAI(
            api_key=OPENAI_API_KEY if OPENAI_API_KEY else "dummy",
        ) if OPENAI_API_KEY else None
```
> **`def __init__(self):` 是干什么的？**
> 这是"构造函数"（Constructor），在创建实例时自动调用。
> 就像"餐厅开业前，要先准备厨房、招聘服务员"。
> 
> **`self.openai_client = openai.OpenAI(...)` 是什么意思？**
> 创建一个OpenAI客户端实例，后续调用API时直接用这个实例。
> 就像"招聘一个专门的OpenAI服务员"，以后点菜直接找他。
> 
> **`if OPENAI_API_KEY else None` 是什么意思？**
> 如果配置了API Key，就创建客户端；否则设为 `None`（空）。
> 就像"如果有OpenAI的会员卡，就招聘专门的OpenAI服务员；否则就不招"。

```python
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
    def call_model(
        self,
        model_config: ModelConfig,
        instruction: str,
        input_text: str = "",
        max_tokens: int = 1000,
    ) -> ModelResponse:
        """
        统一调用接口 - 不管什么模型，都用这个方法
        
        参数：
        - model_config: 模型配置（从config.py读取）
        - instruction: 任务指令（比如"总结下面这段话"）
        - input_text: 输入文本（比如要总结的那段话）
        - max_tokens: 最多生成多少token
        
        返回：
        - ModelResponse 对象（包含回复、耗时、花费等）
        
        为什么要用 @retry？
        - API偶尔会失败（网络抖动、限流等）
        - 自动重试3次，提高成功率
        """
```
> **`@retry(stop=stop_after_attempt(3), ...)` 是干什么的？**
> 这是"装饰器"（Decorator），给函数加功能（就像"给手机加个保护壳"）。
> 这里加的功能是"如果调用失败，自动重试3次"。
> 
> **为什么要重试？**
> 因为API调用是"网络通信"，偶尔会失败：
> - 网络抖动（就像"打电话时信号不好"）
> - API限流（就像"餐厅客满，请稍后再来"）
> 
> 如果不重试，一次失败就"放弃"了，很浪费。
> 所以加个重试机制，提高成功率。
> 
> **`wait_exponential(multiplier=1, min=4, max=60)` 是什么意思？**
> 每次重试前等待的时间"指数增长"：
> - 第1次失败：等 4 秒再重试
> - 第2次失败：等 8 秒再重试
> - 第3次失败：等 16 秒再重试
> - 最多等 60 秒
> 
> **为什么要"指数增长"？**
> 因为如果API是"限流"导致的失败，
> 等的时间越长，API恢复的可能性越大。
> 就像"餐厅客满"，你等10分钟再去，比"马上再去"更容易有位置。

```python
        # 根据服务商选择不同的调用方式
        if model_config.provider == "openai":
            return self._call_openai(model_config, full_prompt, max_tokens, start_time)
        
        elif model_config.provider == "anthropic":
            return self._call_anthropic(model_config, full_prompt, max_tokens, start_time)
        
        elif model_config.provider == "openai_compatible":
            return self._call_openai_compatible(model_config, full_prompt, max_tokens, start_time)
```
> **`if model_config.provider == "openai":` 是干什么的？**
> 根据"服务商"选择不同的调用方式。
> 就像"点菜"时，川菜找川菜厨师，粤菜找粤菜厨师。
> 
> **为什么要分开调用？**
> 因为不同服务商的API格式不一样：
> - OpenAI：`client.chat.completions.create(...)`
> - Anthropic：`client.messages.create(...)`
> - 国产模型：`client.chat.completions.create(...)`（但要把 `base_url` 改成国产厂商的地址）
> 
> 如果写在一起，代码会很长很乱。
> 所以拆成三个"私有方法"（以 `_` 开头的方法），各管各的。

```python
    def _call_openai(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_tokens: int,
        start_time: float,
    ) -> ModelResponse:
        """调用 OpenAI API（GPT-4o、GPT-4o-mini 等）"""
        
        if not self.openai_client:
            raise ValueError("OpenAI API Key 未配置")
        
        # 调用 Chat Completions API
        response = self.openai_client.chat.completions.create(
            model=model_config.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,   # 控制创造性，0.7是比较平衡的值
        )
```
> **`self.openai_client.chat.completions.create(...)` 是干什么的？**
> 调用OpenAI的"聊天补全API"（Chat Completions API）。
> 这是OpenAI最常用的API，用来"让模型回答问题"。
> 
> **参数说明：**
> - `model`：模型名称（比如 `"gpt-4o-mini"`）
> - `messages`：对话历史（这里只传了一条消息，就是用户的提问）
> - `max_tokens`：最多生成多少token（防止生成太长，浪费钱）
> - `temperature`：控制"创造性"（0=很死板，1=很创意，0.7=平衡）
> 
> **`temperature=0.7` 是什么意思？**
> 就像"厨师的创意"：
> - `temperature=0`：每次做菜都一模一样（适合客服、翻译等需要"稳定"的场景）
> - `temperature=1`：每次做菜都不一样（适合写小说、头脑风暴等需要"创意"的场景）
> - `temperature=0.7`：有点创意，但不过分（最常用）
> 
> **返回的 `response` 是什么结构？**
> ```python
> {
>     "choices": [
>         {
>             "message": {
>                 "content": "模型生成的回复"
>             }
>         }
>     ],
>     "usage": {
>         "prompt_tokens": 100,      # 输入用了多少token
>         "completion_tokens": 50,  # 输出生成了多少token
>     }
> }
> ```

```python
        # 提取回复内容
        output_text = response.choices[0].message.content
        
        # 计算花费
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens / 1000 * model_config.price_per_1k_input +
                output_tokens / 1000 * model_config.price_per_1k_output)
```
> **`output_text = response.choices[0].message.content` 是干什么的？**
> 从API返回的结果里，提取"模型生成的回复"。
> 
> **为什么要 `.choices[0]`？**
> 因为OpenAI API支持"一次生成多个回复"（比如 `n=3`，让模型生成3个不同的回答）。
> 但我们这里只生成1个回复，所以取 `choices[0]`（第一个回复）。
> 
> **`cost = (input_tokens / 1000 * price_per_1k_input + ...)` 是干什么的？**
> 计算这次API调用花了多少钱。
> 
> **计算公式：**
> ```
> 总成本 = (输入token数 ÷ 1000 × 每1000输入token的价格) +
>          (输出token数 ÷ 1000 × 每1000输出token的价格)
> ```
> 
> **示例：**
> 输入1000个token，输出500个token，用GPT-4o-mini：
> - 输入成本：`1000 ÷ 1000 × $0.00015 = $0.00015`
> - 输出成本：`500 ÷ 1000 × $0.0006 = $0.0003`
> - 总成本：`$0.00015 + $0.0003 = $0.00045`（约 ¥0.003）
> 
> **为什么要记录成本？**
> 因为企业关心"用这个模型要花多少钱"，
> 记录每次调用的成本，后续能生成"成本预测报告"（比如"月调用10万次要花多少"）。

---

### 7.4 evaluator.py —— 评估器

**文件路径：** `D:\agent\zixuan\evaluator.py`

**作用：**
评估模型输出质量（就像考试的"阅卷老师"）。

**核心功能：**
1. 调用各个模型，拿到回复
2. 用LLM-as-Judge评估质量（让强大模型当评委）
3. 计算综合得分（成本、速度、质量加权）

**逐行解析：**

```python
"""
评估器 - 负责评估模型输出质量
就像考试的"阅卷老师"，给每个模型的回答打分

包含三个维度：
1. 成本评估 - 花了多少钱
2. 速度评估 - 响应有多快
3. 质量评估 - 回答得好不好（用 LLM-as-Judge，让强大模型当评委）
"""
```
> **为什么要分成三个维度评估？**
> 因为企业选型时，不能只看"质量"（就像选餐厅不能只看"口味"）：
> - 成本：太贵了用不起（就像餐厅太贵，吃不起）
> - 速度：太慢了影响用户体验（就像上菜太慢，客人等不及）
> - 质量：太差了解决不了问题（就像菜太难吃，白吃了）
> 
> 所以要"综合考虑"，给每个维度打分，然后算"综合得分"。

```python
class ModelEvaluator:
    """
    模型评估器
    
    为什么需要 "LLM-as-Judge"？
    - 传统评估：用 BLEU、ROUGE 等指标，但这些指标跟人类判断相关性不高
    - LLM-as-Judge：让 GPT-4o 当评委，给模型回答打分（1-10分）
    - 研究表明：GPT-4o 的评分跟人类评分相关性很高（>0.8）
    - 成本：用 gpt-4o-mini 当评委，每1000条评分约 $0.5，很便宜
    """
```
> **什么是 BLEU、ROUGE？**
> 这是传统的"自动评估指标"：
> - BLEU：用来评估"翻译质量"（对比机器翻译和人工翻译的相似度）
> - ROUGE：用来评估"总结质量"（对比机器总结和人工总结的相似度）
> 
> **为什么不用 BLEU、ROUGE？**
> 因为它们只看"字面相似度"，不看"语义"：
> - 比如参考答案是"今天天气很好"，
> - 模型回答是"今日天气不错"（意思一样，但字面不一样），
> - BLEU会给低分（因为字面不一样），但人类会觉得"回答得很好"。
> 
> **LLM-as-Judge 的优势：**
> 因为GPT-4o能理解语义，所以打分跟人类更相关。
> 就像"美食评委"能尝出"这道菜好吃"（语义理解），
> 而不是只看"这道菜的食材跟标准答案一样吗"（字面相似度）。

```python
    def evaluate_task(
        self,
        task_sample,
        model_responses: Dict[str, ModelResponse],
        weights: Dict[str, float] = None,
    ) -> TaskEvaluationResult:
        """
        评估单个任务的所有模型回复
        
        参数：
        - task_sample: 任务样本（题目）
        - model_responses: 各个模型的回复 {模型名: 回复内容}
        - weights: 评估维度权重（成本、速度、质量的占比）
        
        返回：
        - TaskEvaluationResult: 包含所有的评估结果
        """
```
> **这个函数的作用是什么？**
> 评估"一道题"（一个任务）的所有模型回复。
> 就像"阅卷老师"改"一道题"的"多份答卷"（每个模型都做了一遍这道题）。
> 
> **为什么要传入 `model_responses`？**
> 因为这个函数只负责"评估"，不负责"调用模型"。
> 调用模型是 `api_client.py` 的工作。
> 
> **为什么要 `weights` 参数？**
> 因为不同企业对"成本、速度、质量"的看重程度不一样：
> - 创业公司：更看重成本（钱不多）
> - 大厂：更看重质量（用户体验最重要）
> 
> 所以把权重做成"参数"，让企业自己调整。

```python
        # ========== 第二步：质量评估（LLM-as-Judge）====================
        quality_scores = {}
        for model_name, response in model_responses.items():
            if not response.success:
                # 如果模型调用失败，给0分
                quality_scores[model_name] = QualityScore(
                    model_name=model_name,
                    task_id=task_sample.id,
                    overall_score=0.0,
                    accuracy=0.0,
                    relevance=0.0,
                    completeness=0.0,
                    readability=0.0,
                    reasoning="模型调用失败，无法评估",
                )
```
> **`if not response.success:` 是干什么的？**
> 检查模型调用是否成功。
> 如果失败（比如API Key错了、网络超时），就不用让评委打分了，直接给0分。
> 
> **为什么要给0分？**
> 因为"调用失败"比"回答得差"更严重：
> - 回答得差：至少还有输出，能人工修改
> - 调用失败：直接报错，用户体验极差
> 
> 就像"考试时"：
> - 回答得差：得0-4分（至少还写了）
> - 没交卷：得0分（直接放弃）

```python
            else:
                # 调用评委模型打分
                score = self._judge_quality(task_sample, response.output_text)
                quality_scores[model_name] = score
```
> **`score = self._judge_quality(...)` 是干什么的？**
> 调用"评委模型"（比如GPT-4o-mini），让它给模型的回答打分。
> 
> **`_judge_quality` 函数里面做了什么？**
> 1. 构造一个"评委提示词"（告诉评委"怎么打分"）
> 2. 调用评委模型的API
> 3. 解析评委的回复（期望是JSON格式，包含 `accuracy`、`relevance` 等字段）
> 4. 计算总分（四个维度的平均分）
> 
> **评委提示词示例：**
> ```
> 你是一位专业的AI模型评估专家。请对以下AI模型的回答进行评分。
> 
> 【任务指令】
> 用户问：'你们店支持7天无理由退货吗？'
> 
> 【模型回答】
> 亲，我们是支持7天无理由退货的哦！...
> 
> 【评分标准】
> 请从以下四个维度打分（每维度 1-10 分）：
> 1. 准确性（Accuracy）：回答是否准确、有无事实错误？
> 2. 相关性（Relevance）：是否直接回答了问题？
> 3. 完整性（Completeness）：是否覆盖了所有要点？
> 4. 可读性（Readability）：表达是否清晰、通顺、易懂？
> 
> 【输出格式】
> 请严格按照以下JSON格式输出（不要输出其他内容）：
> {
>     "accuracy": 8,
>     "relevance": 9,
>     "completeness": 7,
>     "readability": 8,
>     "reasoning": "回答准确，直接解决了用户问题，但缺少了XXX部分..."
> }
> ```
> 
> **为什么要指定"输出格式"？**
> 因为我们后续要用代码解析评委的回复，
> 如果评委回复的是"自然语言"（比如"我觉得这个回答得8分，因为..."），
> 代码很难解析（不知道哪部分是分数）。
> 
> 所以要求评委输出"JSON格式"（就像"填表格"），
> 代码就能很容易地提取分数（`scores["accuracy"]`）。

```python
        # ========== 第三步：计算综合得分 ==========
        # 综合得分 = 成本得分×30% + 速度得分×20% + 质量得分×50%
        # （权重可以调整）
        
        comprehensive_scores = {}
        for model_name in model_responses.keys():
            cost_score = self._calculate_cost_score(model_responses[model_name])
            speed_score = self._calculate_speed_score(model_responses[model_name])
            quality_score = quality_scores[model_name].overall_score
            
            # 加权平均（所有分数都归一化到 0-10 分制）
            final_score = (
                cost_score * weights["cost"] * 10 +     # 成本越低分越高，需要反转
                speed_score * weights["speed"] * 10 +
                quality_score * weights["quality"]
            )
            comprehensive_scores[model_name] = round(final_score, 2)
```
> **`cost_score = self._calculate_cost_score(...)` 是干什么的？**
> 计算"成本得分"（0-10分）。
> 
> **为什么要"归一化"到0-10分？**
> 因为成本、速度、质量的"原始值"不在一个量级：
> - 成本：$0.001 到 $0.1（小数点很多位）
> - 速度：0.5秒 到 10秒（数值范围不一样）
> - 质量：1-10分（已经是0-10分了）
> 
> 如果直接加权，会出现"质量分1-10，成本分0.001-0.1，质量分的影响被稀释了"。
> 
> 所以要把成本、速度都"归一化"到0-10分，这样加权才公平。
> 
> **成本得分怎么算？**
> 用"指数函数"：`score = exp(-cost * 100)`
> - 成本 $0.001：`exp(-0.001 * 100) = exp(-0.1) = 0.905`（9分）
> - 成本 $0.01：`exp(-0.01 * 100) = exp(-1) = 0.368`（3.7分）
> - 成本 $0.1：`exp(-0.1 * 100) = exp(-10) = 0.000045`（0分）
> 
> **为什么要这样设计？**
> 因为成本是"越低越好"，
> 如果直接用"1/cost"算分，会出现"成本$0.001得1000分，成本$0.01得100分"，
> 差距太大（1000倍），会导致"成本权重"实际影响过大。
> 
> 用指数函数，能让"成本分的分布更平滑"（不会出现极端值）。

---

### 7.5 report_generator.py —— 报告生成器

**作用：**
把评估结果转成可阅读的报告（就像餐厅的"结账小票"）。

**支持三种格式：**
1. Markdown（简单易读，能转PDF）
2. HTML（漂亮，能直接在浏览器里看）
3. PDF（正式，能打印）

**逐行解析（节选核心部分）：**

```python
"""
报告生成器 - 把评估结果转成可阅读的报告

支持两种格式：
1. Markdown 报告（简单易读）
2. HTML 报告（漂亮，可转PDF）
3. PDF 报告（用 ReportLab 生成）

就像餐厅的"结账小票"，把整个评估过程的结果打印出来
"""
```
> **为什么要生成报告？**
> 因为评估的结果（数字、图表）存在代码里，老板看不懂。
> 需要生成一份"人类可读"的报告（就像"结账小票"），
> 老板一看就明白"哪个模型最好，要花多少钱"。
> 
> **三种格式的区别：**
> - Markdown：纯文本格式，能转成任何格式（HTML、PDF、Word）
> - HTML：网页格式，能嵌入图表（用matplotlib生成）
> - PDF：打印格式，适合"正式汇报"（给CTO/CFO看）

```python
    def generate_markdown_report(self, report: BenchmarkReport) -> str:
        """
        生成 Markdown 格式报告
        
        Markdown 就像"简化版HTML"
        - 用 # 表示标题
        - 用 **文字** 表示加粗
        - 用 | 分隔表示表格
        很多平台都能直接渲染（GitHub、语雀、飞书等）
        """
```
> **什么是 Markdown？**
> 一种"轻量级标记语言"（就像"简化版HTML"）。
> 
> **示例：**
> ```markdown
> # 标题1
> ## 标题2
> 
> **加粗文字**
> 
> | 列1 | 列2 |
> |------|------|
> | 内容 | 内容 |
> ```
> 
> **为什么要生成Markdown？**
> 因为Markdown"通用性强"：
> - 能直接贴在GitHub README里
> - 能导入语雀、飞书文档
> - 能用Pandoc转成HTML、PDF、Word
> 
> 就像"万能插头"，去哪个国家都能用。

```python
        # ========== 标题 ==========
        md_lines.append(f"# {report.report_title}\n")
        md_lines.append(f"**报告ID**: {report.report_id}  ")
        md_lines.append(f"**生成时间**: {report.created_at}  ")
        md_lines.append(f"**评估批次**: {report.batch_name}  ")
        md_lines.append(f"**测试任务数**: {report.total_tasks}  ")
        md_lines.append(f"**测试模型**: {', '.join(report.models_tested)}  ")
        md_lines.append("\n---\n")
```
> **`md_lines.append(...)` 是干什么的？**
> 把一行Markdown文本加到列表里。
> 最后用 `"\n".join(md_lines)` 把所有行拼接成完整的Markdown文档。
> 
> **为什么要存在列表里，而不是直接写到文件？**
> 因为：
> 1. 列表能"动态添加"（边评估边往里加内容）
> 2. 最后一次性写入文件（比"每次都打开文件写一行"快）
> 
> 就像"写文章"：
> - 先打草稿（写在列表里）
> - 最后抄正（一次性写入文件）

```python
        # ========== 执行摘要 ==========
        md_lines.append("## 📊 执行摘要\n")
        
        if report.summary_stats:
            md_lines.append("| 模型 | 综合得分 | 质量得分 | 总成本 | 平均响应时间 |")
            md_lines.append("|------|---------|---------|--------|------------|")
            
            for model_name, stats in report.summary_stats.items():
                md_lines.append(
                    f"| {model_name} "
                    f"| {stats.get('avg_comprehensive_score', 0)} "
                    f"| {stats.get('avg_quality_score', 0)} "
                    f"| ${stats.get('total_cost', 0):.4f} "
                    f"| {stats.get('avg_latency', 0):.2f}s |"
                )
```
> **这段代码在干什么？**
> 生成"执行摘要"部分的Markdown表格。
> 
> **表格格式：**
> ```markdown
> | 模型 | 综合得分 | 质量得分 | 总成本 | 平均响应时间 |
> |------|---------|---------|--------|------------|
> | GPT-4o | 8.5 | 9.2 | $0.15 | 2.3s |
> | 通义千问 | 7.8 | 7.5 | $0.002 | 1.1s |
> ```
> 
> **`f"| {model_name} "` 是什么？**
> Python的"格式化字符串"（f-string），
> 能把变量的值"嵌入"到字符串里。
> 
> 就像"填空"：
> - 原题：`"| {model_name} |"`
> - 填空后：`"| GPT-4o |"`

---

### 7.6 main.py —— 主程序入口

**作用：**
FastAPI Web应用（就像餐厅的"前台"）。

**核心功能：**
1. 提供网页界面（首页、上传页面、结果页面）
2. 提供API接口（上传任务、启动评估、查询进度、下载报告）
3. 编排评估流程（调用api_client、evaluator、report_generator）

**逐行解析（节选核心部分）：**

```python
"""
主程序入口 - FastAPI Web 应用
就像餐厅的"前台"，负责接待客户、派单、结账

功能：
1. 上传任务样本（网页表单）
2. 选择要测试的模型
3. 启动评估（后台运行）
4. 查看/下载报告
"""
```
> **什么是 FastAPI？**
> 一个Python的"Web框架"（就像"餐厅的前台系统"）。
> 
> **为什么要做网页界面？**
> 因为不是所有人都会用"命令行"（就像不是所有人都会"做饭"），
> 但几乎所有人都会用"网页"（就像几乎所有人都会"点外卖"）。
> 
> 所以做一个网页界面，让企业用户能"点几下鼠标"就完成评估。

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
```
> **这些导入是干什么的？**
> - `FastAPI`：Web框架的核心类
> - `UploadFile, File`：处理文件上传（就像"接收客户的点菜单"）
> - `Form`：处理表单数据（就像"接收客户填的表格"）
> - `HTTPException`：抛出HTTP错误（比如"404 Not Found"）
> - `BackgroundTasks`：后台任务（就像"客户点单后，厨房在后台做菜，前台继续接待其他客户"）
> - `HTMLResponse`：返回HTML网页
> - `FileResponse`：返回文件（用于下载报告）
> - `StaticFiles`：托管静态文件（CSS、JS、图片）
> - `Jinja2Templates`：模板引擎（就像"邮件合并"，把数据填入HTML模板）

```python
# ==================== 初始化 FastAPI 应用 ====================
app = FastAPI(
    title="智选 - AI模型选型平台",
    description="企业大模型成本效益分析与自动化选型平台",
    version="1.0.0",
)

# 挂载静态文件目录（CSS、JS、图片等）
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 模板引擎（用来渲染HTML页面）
templates = Jinja2Templates(directory="templates")
```
> **`app = FastAPI(...)` 是干什么的？**
> 创建一个FastAPI应用实例。
> 就像"开一家餐厅"，要先"注册营业执照"（创建应用）。
> 
> **`app.mount("/static", ...)` 是干什么的？**
> 把 `static/` 目录"挂载"到 `/static` 路径。
> 这样网页里就能引用 `/static/style.css`（就像"把厨房安排在餐厅后面"）。
> 
> **`Jinja2Templates(directory="templates")` 是干什么的？**
> 创建一个"模板引擎"，用来渲染HTML页面。
> 就像"邮件合并"：
> - 你写一个HTML模板（带占位符，比如 `{{ report.title }}`）
> - 传入实际数据（比如 `report.title = "AI模型选型报告"`）
> - 模板引擎自动把占位符替换成实际数据，生成最终的HTML

```python
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    首页 - 展示平台功能入口
    
    就像餐厅的"菜单首页"，告诉客户能点什么菜
    """
    return templates.TemplateEnv.get_template("index.html").render(
        request=request,
        available_models=list(AVAILABLE_MODELS.keys()),
    )
```
> **`@app.get("/")` 是干什么的？**
> 定义一个"路由"（Route）。
> 就像"餐厅的门口"，客户访问 `http://localhost:8000/` 时，
> 会执行 `index()` 函数，返回首页HTML。
> 
> **`async def index(...)` 是什么意思？**
> 定义一个"异步函数"（async function）。
> 就像"前台接待"可以同时处理"多个客户的咨询"（不用等一个客户说完再接待下一个）。
> 
> **为什么要"异步"？**
> 因为Web服务器要同时处理"多个用户的请求"，
> 如果用"同步"（一个一个处理），后面的用户要"排队"，体验很差。
> 
> 用"异步"，就像"餐厅有多个服务员"，能同时接待多桌客人。

```python
@app.post("/api/start-evaluation")
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    启动评估任务（后台运行）
    
    就像客户"下单"，后台开始做菜
    """
    # 验证 batch_id
    if request.batch_id not in task_batches:
        raise HTTPException(status_code=404, detail="任务批次不存在")
    
    # 创建报告ID
    report_id = "report_" + str(uuid.uuid4())[:8]
    
    # 添加后台任务
    background_tasks.add_task(
        run_evaluation,
        report_id=report_id,
        batch=request.batch_id,
        model_names=request.model_names,
    )
    
    return {
        "status": "accepted",
        "report_id": report_id,
        "message": "评估任务已启动，请稍后查询进度",
    }
```
> **`@app.post("/api/start-evaluation")` 是什么意思？**
> 定义一个"POST请求"的路由。
> 就像"餐厅的后厨入口"，客户不能直接进，只能通过"前台下单"（API调用）。
> 
> **`background_tasks.add_task(...)` 是干什么的？**
> 把评估任务加到"后台任务队列"。
> 就像"客户点单后，前台把订单交给后厨（后台），前台继续接待其他客户"。
> 
> **为什么要"后台运行"？**
> 因为评估任务很耗时（5-10分钟），
> 如果让用户"一直等着页面转圈"，体验很差。
> 
> 所以设计成：
> 1. 用户点击"开始评估"
> 2. 后台开始跑评估（用户在"进度页面"看进度）
> 3. 评估完成后，用户收到通知（或自己刷新页面看结果）
> 
> 就像"点外卖"：
> - 你下单后，不用一直盯着厨师做菜
> - 你可以去干别的（比如看电视）
> - 菜做好了，骑手会送过来（或你收到短信通知）

---

## 8. 常见问题FAQ

### 8.1 安装配置问题

**Q：pip install 很慢怎么办？**
A：使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q：.env 文件在哪？**
A：在项目根目录（跟 `main.py` 同级）。如果没看到，打开"文件资源管理器"，勾选"隐藏的项目"（Windows）。

**Q：API Key 填错了会怎样？**
A：平台会报错 "Authentication error" 或 "Invalid API Key"，请检查是否复制完整。

### 8.2 使用问题

**Q：评估要多久？**
A：取决于任务数和模型数。10个任务 × 5个模型 = 50次API调用，约5-10分钟。

**Q：能中断评估吗？**
A：可以，按 `Ctrl + C` 停止平台。但已经完成的评估无法恢复，需要重新启动。

**Q：评估报告在哪？**
A：在 `reports/` 目录下，有 `.md`、`.html`、`.pdf` 三种格式。

### 8.3 费用问题

**Q：评估会花多少钱？**
A：取决于模型选择和任务数。建议先用国产模型（通义千问/DeepSeek）测试，成本可忽略不计。

**Q：如何控制成本？**
A：
1. 先用少量任务（5-10个）测试流程
2. 用国产模型做初步评估
3. 确定好模型后，再用GPT-4o做最终验证

---

## 附录：文件清单

```
D:\agent\zixuan\
├── requirements.txt            # 依赖清单
├── config.py                  # 配置文件（模型列表、API Key、权重）
├── models.py                  # 数据模型定义（任务、回复、评估结果）
├── api_client.py              # API调用封装（统一调用接口）
├── evaluator.py               # 评估器（LLM-as-Judge、综合得分计算）
├── report_generator.py       # 报告生成器（Markdown/HTML/PDF）
├── main.py                   # 主程序（FastAPI Web应用）
├── .env.example              # 环境变量示例（用户要复制成 .env）
├── data\
│   └── sample_tasks.json    # 示例任务（10个客服场景）
├── templates\
│   ├── index.html           # 首页
│   ├── upload.html          # 上传任务页面
│   ├── results.html         # 评估结果页面
│   └── report_template.html # 报告HTML模板
├── static\
│   ├── style.css            # 样式文件
│   └── main.js             # 前端交互逻辑
└── reports\                  # 生成的报告（自动创建）
    ├── report_xxx.md
    ├── report_xxx.html
    └── report_xxx.pdf
```

---

## 结语

恭喜你读完了这份超详细的使用说明书！

**如果你是完全不懂代码的小白：**
- 你已经知道平台能干什么、怎么用、评估报告怎么解读
- 可以直接使用平台，遇到问题看"常见问题FAQ"

**如果你是会一点代码的开发者：**
- 你已经深入理解平台的工作原理
- 可以根据自己的需求修改配置（比如加新的模型、调整评估权重）

**如果你是要修改平台的企业开发者：**
- 你已经读懂了每一行代码
- 可以根据自己的业务需求，修改或扩展平台功能

---

**最后的话：**
> 这个平台的初衷，是让企业"不盲目选型"——用数据说话，而不是凭感觉。
> 
> 希望这份说明书能帮到你。如果有问题，欢迎提Issue或PR！

---

**文档版本：** v1.0  
**最后更新：** 2026-05-26  
**作者：** 智选团队  
**联系方式：** [GitHub Issues](https://github.com/your-repo/zixuan/issues)
