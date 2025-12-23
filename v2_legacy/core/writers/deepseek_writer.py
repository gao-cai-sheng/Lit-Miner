"""
DeepSeek Writer - AI-powered Literature Review Generator
Uses DeepSeek API to generate comprehensive reviews from RAG-retrieved papers
"""

import requests
from typing import Dict, Any, Optional

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL


class DeepSeekWriter:
    """
    AI-powered literature review writer using DeepSeek Chat API
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Args:
            api_key: DeepSeek API key (uses config if not provided)
            base_url: API base URL (uses config if not provided)
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.model_name = "deepseek-chat"
        
        if not self.api_key:
            raise RuntimeError("DeepSeek API key not configured. Set DEEPSEEK_API_KEY in .env")
    
    def generate_review(
        self,
        topic: str,
        evidence: Dict[str, Any],
        raw_query: str = "",
        search_term: str = ""
    ) -> str:
        """
        Generate literature review from RAG evidence.
        
        Args:
            topic: Review topic/title
            evidence: RAG query results with ids, metadatas, documents
            raw_query: Original user query (for context)
            search_term: Expanded search term used
            
        Returns:
            Generated review in Markdown format
        """
        # Build context from evidence
        context = self._build_context(evidence)
        if not context:
            return "❌ No papers found for review generation"
        
        # Build prompt
        prompt = self._build_prompt(topic, context, raw_query, search_term, evidence)
        
        # Call API
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=120
            )
            resp.raise_for_status()
            
            result = resp.json()
            text = result["choices"][0]["message"]["content"]
            return text
            
        except Exception as e:
            return f"❌ Review generation failed: {e}"
    
    def _build_context(self, evidence: Dict[str, Any]) -> str:
        """Build context string from evidence"""
        context = ""
        
        if not evidence or not evidence.get("ids") or len(evidence["ids"][0]) == 0:
            return context
        
        for i in range(len(evidence["ids"][0])):
            meta = evidence["metadatas"][0][i]
            context += f"【文献{i + 1}】(PMID:{evidence['ids'][0][i]})\n"
            context += f"标题: {meta.get('title', '')}\n"
            context += f"来源: {meta.get('journal', '')} ({meta.get('year', '')})\n"
            context += f"摘要: {evidence['documents'][0][i][:800]}\n\n"
        
        return context
    
    def _build_prompt(
        self,
        topic: str,
        context: str,
        raw_query: str,
        search_term: str,
        evidence: Dict[str, Any]
    ) -> str:
        """Build prompt for DeepSeek"""
        num_docs = len(evidence["ids"][0])
        display_topic = topic or raw_query or "牙周/口腔医学相关主题"
        
        prompt = f"""你是一位顶级的牙周病学和口腔医学专家。请基于以下【检索到的最相关文献】写一篇专业综述,并在合适位置生成配图的AI绘图提示词。

【用户检索问题】：
{raw_query if raw_query else "（未提供）"}

【检索使用的英文term】：
{search_term if search_term else "（未记录）"}

【本次写作主题】：
{display_topic}

【核心文献摘要】（共{num_docs}篇）：
{context}

【写作要求】：
1. **引言与概念阐述**：
   - 简要说明该主题的临床重要性
   - 定义关键概念和术语,解释操作发生的位置、解决的问题
   - **配图提示**: 在需要用图解释概念的位置,生成配图的AI绘图prompt,格式为:
     【prompt】详细的英文或中文绘图提示词【/prompt】
   - 示例: 【prompt】Medical illustration of dental socket preservation procedure, cross-sectional view showing alveolar bone, extraction socket, and bone graft material placement, anatomical accuracy, professional medical textbook style【/prompt】

2. **Primary Outcome系统对比**：
   - 从每篇文献识别primary outcome（PPD、CAL、MBL、种植存活率等）
   - 按结局类别对比不同研究,给出关键数值
   - **配图提示**: 在需要数据可视化的位置,生成图表prompt:
     【prompt】Bar chart comparing PPD reduction across 5 studies, X-axis showing study numbers, Y-axis showing PPD change in mm, clear labels, scientific publication style【/prompt】

3. **统计学显著性结果分析**：
   - 明确指出哪些研究达到统计学显著(p<0.05)
   - 区分"统计学显著"与"临床显著"
   - 可添加森林图或对比图的prompt

4. **不同方案/材料分析**：
   - 按手术方式或材料类别分组讨论
   - 总结各组在primary outcome上的表现
   - 结合secondary outcome综合权衡

5. **证据局限性**：
   - 从研究设计角度讨论不足（样本量、随访、盲法等）
   - 从结局选择角度讨论缺失（PROMs、长期数据等）
   - 强调哪些结论只能"谨慎推荐"

6. **未来展望与临床建议**：
   - 基于不足指出改进方向
   - 讨论技术趋势（数字化、AI、新材料等）
   - 给出3-5条清晰的take-home messages

**配图prompt生成规则（重要!）**：
- 在文章中需要配图的位置,直接生成可用于AI绘图工具(如DALL-E, Midjourney等)的提示词
- 格式: 【prompt】具体的绘图提示词【/prompt】
- 提示词要求:
  * 可以是中文或英文,描述清晰具体
  * 包含图片类型(medical illustration/bar chart/cross-sectional view等)
  * 包含关键元素(牙齿结构/数据对比/手术步骤等)
  * 包含风格要求(medical textbook style/scientific publication/anatomical accuracy等)
- 每篇文章建议2-4个配图prompt
- 例子:
  * 概念图: 【prompt】牙周袋形成的医学示意图,剖面视图,显示牙龈组织、牙槽骨吸收、探诊深度测量,医学教科书风格,专业准确【/prompt】
  * 数据图: 【prompt】Horizontal bar chart showing bone height gain (mm) for different graft materials (autograft, xenograft, synthetic), error bars indicating standard deviation, clean minimalist design【/prompt】

**格式要求**：
- 使用Markdown格式
- 每个部分用二级标题(##)
- 适当使用列表和表格
- 引用文献时使用[1][2]等编号
- 配图prompt使用【prompt】...【/prompt】包裹
- 保持专业、客观、准确

请开始撰写综述,确保在合适位置插入2-4个配图prompt。
"""
        return prompt


def generate_topic_from_evidence(
    evidence: Dict[str, Any],
    api_key: str,
    base_url: str
) -> str:
    """
    Auto-generate review topic from evidence.
    
    Args:
        evidence: RAG query results
        api_key: DeepSeek API key
        base_url: API base URL
        
    Returns:
        Generated topic string
    """
    if not evidence or not evidence.get("metadatas"):
        return "Literature Review"
    
    # Extract titles from top papers
    titles = [m.get('title', '') for m in evidence['metadatas'][0][:5]]
    
    summary_prompt = (
        "请阅读以下5篇文献标题，用一句话总结它们共同讨论的核心临床主题，"
        "格式为：'关于...的综述'。\n\n" + "\n".join(titles)
    )
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": summary_prompt}],
            "max_tokens": 100
        }
        
        resp = requests.post(
            f"{base_url}/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if resp.status_code == 200:
            generated = resp.json()["choices"][0]["message"]["content"].strip()
            return generated.strip('"').strip("'")
        else:
            return "Literature Review on Clinical Outcomes"
            
    except Exception:
        return "Literature Review"
