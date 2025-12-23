# 项目传承：Lit-Miner v2.0.1

本文档封装了 "Lit-Miner" 项目的核心知识、架构和技术决策。在新项目启动时，请将此文件提供给您的AI助手，作为项目初始化的上下文依据。

---

## 1. 项目身份
**名称**: Lit-Miner (Legacy / 经典版)
**核心功能**: AI驱动的医学文献挖掘与系统综述生成
**核心价值**: 自动化 PubMed 搜索工作流，通过智能评分（基于影响因子和时效性）筛选高质量论文，并生成基于 RAG 的综合综述。

## 2. 技术栈与依赖

### 核心后端
- **语言**: Python 3.8+
- **API (搜索)**: `Bio.Entrez` (PubMed)
- **API (大模型)**: DeepSeek API (OpenAI兼容)
- **向量数据库**: ChromaDB (本地持久化)
- **Embeddings**: `sentence-transformers` (HuggingFace)

### 前端
- **框架**: Streamlit
- **可视化**: 原生 Streamlit 图表

### 数据处理
- **PDF 处理**: `LayoutParser` (深度学习布局分析), `PyMuPDF` (文本提取)
- **图片提取**: `pdf2image`, `OpenCV`

---

## 3. 架构总览

### 数据流
1.  **搜索与挖掘 (Search & Mine)**:
    用户查询 -> 查询扩展 (AI) -> PubMed 搜索 -> 元数据过滤 -> 智能评分 -> 选出 Top N 论文。
2.  **摄取与存储 (Ingest & Store)**:
    Top 论文 -> 摘要/全文 -> 切片 (Chunking) -> 向量嵌入 -> ChromaDB。
3.  **生成与写作 (Generate / Write)**:
    主题选择 -> 检索 (RAG) -> 上下文组装 -> LLM 生成 -> Markdown 报告。
4.  **处理与阅读 (Process / Read)**:
    PDF 上传 -> 布局分析 -> 文本/图片分离 -> 结构化 Markdown。

### 目录结构模板
```text
project_root/
├── core/                   # 业务逻辑
│   ├── miners/             # 搜索与抓取逻辑 (PubMed)
│   ├── writers/            # LLM 生成逻辑
│   └── processors/         # PDF/文件解析逻辑
├── interface/              # 前端界面 (原 streamlit_app)
├── data/                   # 本地存储 (Git忽略)
│   ├── vector_dbs/
│   └── raw_files/
└── config/                 # 配置与常量
```

---

## 4. 关键指标与算法 (“秘制酱料”)

### A. "Smart Miner" 智能评分系统
不仅仅依赖 PubMed 的相关性排序，而是基于以下维度重排序：
1.  **期刊影响因子**: 对顶级期刊（如 *Nature*, *Periodontology 2000*）硬编码加权。
2.  **时效性**: 最近 1-3 年的论文得分更高。
3.  **类型加成**: "Systematic Reviews"（系统综述）和 "Meta-Analysis"（元分析）有额外加分。
4.  **负面过滤**: 自动排除 "Retracted"（撤稿）论文，降低预印本 (bioRxiv) 权重。

### B. 查询扩展策略 (AI驱动)
解决“关键词不匹配”问题：
-   输入: "Alzheimer"
-   AI 输出: `("Alzheimer's disease"[MeSH Terms] OR "Alzheimer disease"[Title/Abstract] OR "AD"[Title/Abstract])`
-   *经验*: 如果 AI API 失败，必须有一个静态字典作为后备 (Fallback)。

### C. RAG (检索增强生成) 策略
-   不要将整个 PDF 塞入 LLM 上下文窗口。
-   使用 **递归检索 (Recursive Retrieval)**:
    1.  基于摘要生成大纲。
    2.  对于每个章节，从向量库中检索特定的块 (Chunks)。
    3.  逐节合成内容。

---

## 5. 技术决策与经验教训

### 可靠性
-   **影响因子**: 如果包含专有数据，将 `impact_factors.py` 保持独立并加入 `.gitignore`。
-   **API 限制**: 为 PubMed 实现强健的缓存机制（重复查询 1ms 返回），以节省时间和配额。
-   **PDF 处理**: PDF 解析既慢又容易出错。仅在必要时使用 `LayoutParser`；如果结构不重要，优先使用简单的文本提取以提高速度。

### 隐私
-   **Gitignore**: 严格忽略 `data/`, `.env`, `*.log`, 和 `vector_dbs/`。
-   **密钥**: 所有 API Key 必须严格保存在 `.env` 中。

### 对新项目的改进建议
-   **架构**: 如果项目变大，脱离 Streamlit 单体应用架构。考虑 FastAPI 后端 + React/Next.js 前端。
-   **数据库**: ChromaDB 适合本地，但考虑 PGVector 以提升扩展性。
-   **类型系统**: 从第一天起就强制使用严格的 Python 类型提示 (Legacy 项目在这方面有所欠缺)。

---

## 6. 迁移提示词 (Migration Prompt)
**复制并在新项目中粘贴给你的 AI 助手:**

> "我正在启动一个名为 [新项目名称] 的新项目。它是 'Lit-Miner' 的精神续作。我附上了 `PROJECT_INHERITANCE.md`，其中包含了前一个项目的核心基因。
>
> 请根据文档中的 '目录结构模板' 初始化新项目结构。采用 'Smart Miner' 评分逻辑和 'RAG 策略' 进行内容生成。
>
> 但是，我想在 [特定领域，例如 UI 或数据库] 方面进行改进。请现在开始设置初始文件结构。"
