# Lit-Miner 快速测试指南

## ✅ 当前状态
- Streamlit 运行中: http://localhost:8501
- 已有数据库: 
  - `socket_preservation` (11篇论文) ✅
  - `10_Maintenance_in_Periodontal_Therapy` ✅
- API Key: 已配置 ✅

---

## 🔴 问题: "test" 查询失败
**原因**: "test" 作为查询词太通用,PubMed 可能没有返回医学相关结果

**解决**: 使用专业医学术语

---

## 📝 测试步骤

### 测试 1: 验证 Write 功能(使用现有数据)

1. **打开 Write 页面**: http://localhost:8501/Write
2. **选择查询**: 
   - 勾选 "Use current session query" 或
   - 从下拉菜单选择 "socket preservation"
3. **设置**:
   - Topic: 留空(自动生成)
   - Papers: 20
4. **点击**: "Generate Review"
5. **等待**: 30-60秒
6. **验证**: 查看生成的综述

---

### 测试 2: 中文查询 + 查询扩展

1. **打开 Search 页面**: http://localhost:8501/Search
2. **在侧边栏设置邮箱**: 
   ```
   gaoyifu777@gmail.com
   ```
3. **输入中文查询**:
   ```
   牙周炎
   ```
4. **设置 Limit**: 20
5. **点击 Search**

**预期行为**:
- ✅ 查询自动扩展: `牙周炎` → `("periodontitis" OR "chronic periodontitis" OR "aggressive periodontitis")`
- ✅ 在日志中看到扩展后的查询
- ✅ 找到 10-20 篇论文
- ✅ 论文按类别分类

---

### 测试 3: 更多中文查询

继续测试其他中文术语:

| 中文 | 预期英文扩展 |
|------|------------|
| 牙周炎 | periodontitis, chronic periodontitis, aggressive periodontitis |
| 牙龈退缩 | gingival recession, GTR |
| 牙周维护 | periodontal maintenance, supportive periodontal therapy |
| 牙周袋 | periodontal pocket |

---

## 🐛 调试

### 如果 Write 页面显示 "No papers found"

**检查**:
```bash
# 查看数据库目录
ls -la data/vector_dbs/

# 检查特定数据库的记录数
sqlite3 data/vector_dbs/socket_preservation/chroma.sqlite3 "SELECT COUNT(*) FROM embeddings;"
```

**可能原因**:
1. 查询名称不匹配(空格/下划线问题)
2. 数据库为空
3. ChromaDB 查询错误

---

## 📊 查看终端日志

检查 Streamlit 终端输出以查看:
- 查询扩展过程
- PubMed 搜索结果
- 评分和分类逻辑
- 错误信息

---

## ✅ 成功验证标准

- [ ] socket_preservation Write 功能正常
- [ ] 中文查询 "牙周炎" 正确扩展
- [ ] 至少找到 10+ 篇论文
- [ ] 论文正确分类(high_impact/recent/data_rich)
- [ ] AI Review 生成成功
- [ ] Review 质量可接受

