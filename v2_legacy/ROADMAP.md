# Lit-Miner 开发路线图 (v2.1 - v3.0)

**最后更新**: 2025-12-25  
**当前版本**: v2.0.1  
**下一版本**: v2.1 (计划中)

---

## 🎯 总体目标

将 Lit-Miner 从**文献检索工具**升级为**临床学术助手**，覆盖：
1. 文献检索与综述（已完成）
2. 学术汇报支持（新增）
3. 临床决策辅助（新增）

---

## 📅 版本规划

### v2.0.1 (当前版本) ✅
**发布时间**: 2025-12-20  
**核心功能**:
- ✅ AI 查询扩展
- ✅ 60+ 期刊多领域支持
- ✅ 撤稿论文检测
- ✅ 预印本标记
- ✅ 影响因子集成

---

### v2.1 (Phase 1: Review Memory) 🔥
**预计时间**: 1-2 天  
**优先级**: P0（立即开始）

#### 核心功能
**1. 查询历史记录**
- 存储用户所有查询记录
- 数据结构：
  ```json
  {
    "query_id": "uuid",
    "timestamp": "2025-12-25 10:00",
    "query_text": "牙周炎与糖尿病",
    "expanded_query": "...",
    "papers_found": 45,
    "review_generated": true,
    "tags": ["牙周炎", "糖尿病"]
  }
  ```

**2. 历史查询展示**
- 在 Review 页面添加侧边栏
- 显示最近 20 条查询
- 支持点击重新运行

**3. 主题标签系统**
- 自动提取查询关键词
- 支持手动添加标签
- 按标签筛选历史

#### 技术实现
```
core/
  └── memory/
      ├── query_history.py    # 历史记录管理
      └── tag_extractor.py    # 标签提取

data/
  └── query_history.json      # 历史数据存储
```

#### 验收标准
- [ ] 每次查询自动保存
- [ ] 历史记录可查看、重运行
- [ ] 标签自动提取准确率 > 80%

---

### v2.2 (Phase 2: Report Generator) 🔥
**预计时间**: 3-5 天  
**优先级**: P1（优先实施）

#### 核心功能
**1. 单篇文献 PPT 生成**
- 上传 PDF → 自动生成 PPT
- 固定模板（7 页）：
  1. 标题页（论文标题、作者、期刊）
  2. 研究背景（问题、假设）
  3. 研究方法（设计、样本、干预）
  4. 研究方法（统计分析）
  5. 研究结果（主要发现）
  6. 研究结果（次要发现）
  7. 结论与临床意义

**2. 内容自动提取**
- 使用 DeepSeek API 提取：
  - 研究问题
  - 方法学设计
  - 主要结果
  - 结论
  - 临床意义

**3. 模板系统**
- 医学汇报标准模板
- 支持自定义配色
- 支持添加机构 Logo

#### 技术实现
```
core/
  └── generators/
      ├── ppt_generator.py    # PPT 生成核心
      ├── content_extractor.py # 内容提取
      └── templates/
          └── medical_report.pptx  # 模板文件

依赖:
  - python-pptx==0.6.21
```

#### 验收标准
- [ ] 单篇 PDF → PPT 生成成功率 > 90%
- [ ] 内容提取准确性（人工评估）
- [ ] PPT 排版美观（符合学术规范）

---

### v2.3 (Phase 2+: Report Advanced) 🚀
**预计时间**: 2-3 天  
**优先级**: P1（可选增强）

#### 增强功能
**1. 图表提取**
- 从 PDF 提取关键图表
- 自动插入 PPT 对应位置

**2. 多文献整合**
- 合并 2-5 篇文献到一个 PPT
- 对比研究设计和结果

**3. 自定义模板**
- 用户上传自己的 PPT 模板
- 支持多种汇报场景（组会、学术会议）

---

### v2.4 (Phase 3: Chatbot MVP) ⚠️
**预计时间**: 5-7 天  
**优先级**: P2（谨慎实施）

#### 核心功能
**1. 临床指南问答**
- 基于 RAG（检索增强生成）
- 支持自然语言提问
- 返回答案 + 指南引用

**2. 指南知识库**
- 初始版本包含：
  - 欧洲牙周病学会（EFP）指南 2-3 份
  - 美国牙周病学会（AAP）指南 2-3 份
  - 中华口腔医学会指南 1-2 份

**3. 免责声明系统**
- 每次回答附带免责声明
- 明确标注"仅供学术参考"
- 不构成医疗建议

#### 技术实现
```
core/
  └── chatbot/
      ├── rag_engine.py       # RAG 核心
      ├── vector_store.py     # 向量数据库
      └── guideline_loader.py # 指南加载

data/
  └── guidelines/
      ├── efp_2020.pdf
      ├── aap_2018.pdf
      └── vector_db/          # 向量数据库

依赖:
  - chromadb==0.4.22
  - langchain==0.1.0
```

#### 验收标准
- [ ] 问答准确率 > 85%（人工评估）
- [ ] 每个答案都有引用来源
- [ ] 免责声明显示正常

---

## 🗂️ 文件结构变化

### 当前结构 (v2.0.1)
```
Lit-Miner/v2_legacy/
├── core/
│   ├── miners/
│   ├── processors/
│   └── writers/
├── streamlit_app/
│   └── pages/
│       ├── 1_🔍_Search.py
│       ├── 2_✍️_Write.py
│       ├── 3_📖_Read.py
│       └── 4_🔧_Tools.py
└── data/
```

### 目标结构 (v2.4)
```
Lit-Miner/v2_legacy/
├── core/
│   ├── miners/
│   ├── processors/
│   ├── writers/
│   ├── memory/          # 新增：历史记录
│   ├── generators/      # 新增：PPT 生成
│   └── chatbot/         # 新增：问答系统
├── streamlit_app/
│   └── pages/
│       ├── 1_🔍_Search.py
│       ├── 2_✍️_Write.py  (增强：历史记录)
│       ├── 3_📖_Read.py
│       ├── 4_🔧_Tools.py
│       └── 5_📊_Report.py  # 新增
│       └── 6_💬_Chatbot.py # 新增
└── data/
    ├── query_history.json
    ├── guidelines/
    └── vector_db/
```

---

## 📊 开发进度追踪

| 版本 | 功能 | 状态 | 预计完成 |
|------|------|------|----------|
| v2.0.1 | 基础功能 | ✅ 完成 | 2025-12-20 |
| v2.1 | Review Memory | ✅ 完成 | 2025-12-25 |
| v2.2 | Report Generator | ✅ 完成 | 2025-12-25 |
| v2.3 | Report Advanced | 📋 待开始 | 2026-01-05 |
| v2.4 | Chatbot MVP | 📋 待开始 | 2026-01-15 |

---

## ⚠️ 风险与挑战

### Review Memory
- **风险**: 低
- **挑战**: 数据结构设计、性能优化

### Report Generator
- **风险**: 中
- **挑战**: PPT 排版美观、图表提取质量

### Chatbot
- **风险**: 高
- **挑战**: 
  - 法律风险（医疗建议）
  - 指南版权问题
  - 准确性要求极高

---

## 📝 待办事项

### 立即行动
- [ ] 创建 `core/memory/` 目录
- [ ] 设计查询历史数据结构
- [ ] 实现基础存储功能

### 短期计划
- [ ] 调研 `python-pptx` 库
- [ ] 设计 PPT 模板
- [ ] 收集临床指南文档

### 长期规划
- [ ] 用户系统（多用户支持）
- [ ] 云端同步
- [ ] 移动端适配

---

**文档位置**: `/Users/gao/Desktop/Lit-Miner/v2_legacy/ROADMAP.md`  
**相关文档**: `IMPLEMENTATION_STATUS.md`, `TECH_DECISIONS.md`
