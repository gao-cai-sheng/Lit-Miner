# Lit-Miner

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-green)

AI-Powered Literature Mining & Review Generation

一个智能文献研究助手，结合PubMed智能搜索、AI综述生成和本地PDF处理功能。

> **🎉 最新更新 v2.0** (2025-12-19)
> - 🤖 **AI查询扩展**: 零配置支持任意医学领域（神经科学、心血管、肿瘤等）
> - 🌍 **50+顶级期刊**: Nature、Science、NEJM、Lancet等多领域支持
> - 📊 **检索深度提升**: 默认200篇（10倍提升），最高500篇
> - 💎 **PRO功能预览**: 分层订阅UI已集成
>
> [查看完整更新日志 →](CHANGELOG.md)

---

## 📚 功能特性

- **🔍 Search** - 智能文献检索
  - 中英文查询扩展
  - 基于影响因子、时效性的智能评分
  - ChromaDB向量存储用于RAG检索

- **✍️ Write** - AI综述生成
  - 基于检索文献自动生成主题
  - DeepSeek大模型驱动
  - RAG增强准确性
  - Markdown格式导出

- **📖 Read** - 本地PDF智能拆解
  - 上传PDF文件
  - LayoutParser AI模型自动识别
  - 文本提取为Markdown
  - 图片和表格自动分离保存

- **🔧 Tools** - PMID查询工具
  - PMID → DOI转换
  - 论文元数据快速查询
  - 一键访问PubMed/DOI/Sci-Hub链接

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- macOS/Linux/Windows

### 2. 安装步骤

```bash
# 克隆或解压项目
cd Lit-Miner

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（项目根目录）:

```env
# DeepSeek API Key (用于AI写作)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# PubMed联系邮箱 (用于API访问)
PUBMED_EMAIL=your_email@example.com
```

**获取API Key**:
- DeepSeek: https://platform.deepseek.com/
- PubMed: 使用任意有效邮箱

### 4. 运行应用

```bash
cd streamlit_app
streamlit run Home.py
```

浏览器会自动打开 `http://localhost:8501`

---

## 📖 使用指南

### Search - 文献检索

1. 进入 **Search** 页面
2. 输入检索词（支持中英文，如"牙周炎"或"socket preservation"）
3. 点击"开始挖掘"
4. 系统会自动:
   - 扩展查询词
   - 从PubMed检索文献
   - 智能评分排序
   - 存储到ChromaDB向量库

### Write - AI综述生成

1. 进入 **Write** 页面
2. 选择已有的检索查询（或新建）
3. 输入或自动生成综述主题
4. 点击"生成综述"
5. 等待AI生成（约30-60秒）
6. 下载Markdown文件

### Read - PDF处理

1. 进入 **Read** 页面
2. 上传PDF文件
3. 点击"开始AI拆解"
4. 系统会自动:
   - 提取文本为Markdown
   - 识别并分离图片
   - 识别并分离表格
5. 下载处理结果

### Tools - PMID查询

1. 进入 **Tools** 页面
2. 输入PMID（如36054302）
3. 点击"查询"
4. 获取DOI、标题、摘要和快速链接

---

## 🔧 AI模型说明

### LayoutParser模型

Read功能使用LayoutParser进行PDF内容识别。首次使用时会自动下载模型文件（约817MB）。

模型会保存在：`~/.layoutparser/model_final.pth`

如需手动下载：
```bash
# 由layoutparser自动处理，首次运行Read功能时会下载
```

---

## 📁 项目结构

```
Lit-Miner/
├── core/                    # 核心功能模块
│   ├── miners/             # 文献挖掘
│   ├── writers/            # AI写作
│   └── processors/         # PDF处理
├── streamlit_app/          # Web应用
│   ├── pages/              # 各个页面
│   │   ├── 1_🔍_Search.py
│   │   ├── 2_✍️_Write.py
│   │   ├── 3_📖_Read.py
│   │   └── 4_🔧_Tools.py
│   └── utils/              # 工具函数
├── data/                   # 运行时数据(自动生成)
│   ├── vector_dbs/        # 向量数据库
│   ├── raw_pdfs/          # PDF文件
│   └── processed/         # 处理结果
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
└── .env                   # 环境变量(需手动创建)
```

---

## ⚙️ 配置说明

### config.py

主要配置项：

```python
PROJECT_ROOT = ...          # 项目根目录
VECTOR_DB_DIR = ...        # 向量数据库目录
PDF_DIR = ...              # PDF存储目录
PUBMED_EMAIL = ...         # 从.env读取
DEEPSEEK_API_KEY = ...     # 从.env读取
```

### 期刊评分规则

可在 `config.py` 中自定义顶级期刊列表和评分权重：

```python
TOP_JOURNALS = {
    "Periodontology 2000": 10,
    "Journal of clinical periodontology": 8,
    ...
}
```

---

## 🐛 常见问题

### Q: 启动后提示缺少API key
A: 确保创建了 `.env` 文件并配置了 `DEEPSEEK_API_KEY` 和 `PUBMED_EMAIL`

### Q: Read功能提示缺少依赖
A: 确保安装了所有依赖: `pip install -r requirements.txt`

### Q: PDF处理很慢
A: 正常现象。LayoutParser AI模型处理需要30-60秒，取决于PDF大小和页数

### Q: Search找不到文献
A: 检查网络连接，确保能访问PubMed API

### Q: 如何更新依赖？
A: 
```bash
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## 📝 开发说明

### 技术栈

- **Frontend**: Streamlit
- **文献API**: Bio.Entrez (PubMed)
- **向量数据库**: ChromaDB
- **语义模型**: sentence-transformers
- **AI写作**: DeepSeek API
- **PDF处理**: PyMuPDF, LayoutParser
- **图像处理**: OpenCV, pdf2image

### 添加新功能

1. 在 `core/` 目录添加核心逻辑
2. 在 `streamlit_app/pages/` 添加新页面
3. 在 `streamlit_app/utils/` 添加辅助函数
4. 更新导航和文档

---

## 📄 许可证

MIT License

---

## 👥 贡献

欢迎提交Issue和Pull Request!

---

## 📧 联系方式

如有问题或建议，请通过Issue联系。

---

**Built with ❤️ | Powered by DeepSeek & PubMed**
