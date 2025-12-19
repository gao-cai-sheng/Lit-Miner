"""
自动PDF下载模块

功能:
1. PMID → DOI 转换
2. 安全下载PDF (使用Playwright模拟浏览器)
3. 批量下载管理 (带速率限制)
"""

import os
import time
import asyncio
from typing import List, Dict, Any, Tuple
from Bio import Entrez
from playwright.async_api import async_playwright


def pmid_to_doi(pmid: str, email: str = "your_email@example.com") -> str:
    """
    通过PubMed API将PMID转换为DOI
    
    Args:
        pmid: PubMed ID
        email: Entrez API所需的email
        
    Returns:
        DOI字符串,如果未找到返回空字符串
    """
    Entrez.email = email
    
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        
        # 从ArticleIdList中查找DOI
        article_ids = (
            record['PubmedArticle'][0]
            .get('PubmedData', {})
            .get('ArticleIdList', [])
        )
        
        for aid in article_ids:
            if hasattr(aid, 'attributes') and aid.attributes.get('IdType') == 'doi':
                return str(aid)
        
        return ""
    except Exception as e:
        print(f"   ⚠️  PMID {pmid} 转换DOI失败: {e}")
        return ""


def convert_pmids_to_dois(
    papers: List[Dict[str, Any]], 
    email: str = "your_email@example.com"
) -> List[Dict[str, Any]]:
    """
    批量转换PMID为DOI
    
    Args:
        papers: 文献列表,每个包含'id'(PMID)字段
        email: Entrez API所需的email
        
    Returns:
        更新后的文献列表,添加了'doi'字段
    """
    print("\n🔄 [Step 9] PMID → DOI 转换中...")
    print("-" * 80)
    
    for p in papers:
        pmid = p['id']
        doi = pmid_to_doi(pmid, email)
        p['doi'] = doi
        
        if doi:
            print(f"   ✅ PMID {pmid} → DOI: {doi}")
        else:
            print(f"   ❌ PMID {pmid} 未找到DOI")
        
        time.sleep(0.5)  # 礼貌延迟,避免API限流
    
    print("-" * 80)
    return papers


async def download_pdf_safe(
    doi: str, 
    pmid: str, 
    output_dir: str = "downloaded_pdfs",
    source_url: str = "https://sci-net.xyz"
) -> str:
    """
    安全下载单篇PDF
    
    Args:
        doi: DOI
        pmid: PMID (用于命名)
        output_dir: 输出目录
        source_url: PDF源网站
        
    Returns:
        下载的PDF文件路径,失败返回空字符串
    """
    os.makedirs(output_dir, exist_ok=True)
    
    url = f"{source_url}/{doi}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        pdf_data = None
        
        async def handle_response(response):
            nonlocal pdf_data
            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" in content_type:
                try:
                    pdf_data = await response.body()
                    print(f"      ✅ PDF捕获成功! 大小: {len(pdf_data)//1024} KB")
                except Exception as e:
                    print(f"      ❌ PDF读取失败: {e}")
        
        page.on("response", handle_response)
        
        try:
            print(f"      🌐 正在访问: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # 等待PDF加载
            
            # 检查DOM中的PDF链接
            if not pdf_data:
                embed_src = await page.evaluate("""() => {
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    if (embed) return embed.src;
                    const iframe = document.querySelector('iframe');
                    if (iframe) return iframe.src;
                    return null;
                }""")
                
                if embed_src:
                    if embed_src.startswith("//"):
                        embed_src = "https:" + embed_src
                    elif embed_src.startswith("/"):
                        from urllib.parse import urljoin
                        embed_src = urljoin(url, embed_src)
                    
                    response = await page.request.get(embed_src)
                    if response.status == 200:
                        pdf_data = await response.body()
                        print(f"      ✅ PDF捕获成功! 大小: {len(pdf_data)//1024} KB")
        
        except Exception as e:
            print(f"      ❌ 下载失败: {e}")
        
        finally:
            await browser.close()
        
        if pdf_data:
            # 保存PDF
            safe_doi = doi.replace("/", "_").replace(":", "_")
            filename = f"PMID_{pmid}_{safe_doi}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(pdf_data)
            
            print(f"      💾 已保存: {filename}")
            return filepath
        else:
            print(f"      ⚠️  下载失败,请手动下载: {url}")
            return ""


async def batch_download_pdfs(
    papers: List[Dict[str, Any]], 
    delay_seconds: int = 60,
    output_dir: str = "downloaded_pdfs"
) -> List[str]:
    """
    批量下载PDF (带延迟,安全策略)
    
    Args:
        papers: 文献列表,每个包含'doi'和'id'(PMID)字段
        delay_seconds: 每篇下载间隔秒数
        output_dir: 输出目录
        
    Returns:
        成功下载的PDF文件路径列表
    """
    print(f"\n📥 [Step 10] 开始下载PDF (每篇间隔{delay_seconds}秒)...")
    print("-" * 80)
    
    downloaded_files = []
    
    for i, p in enumerate(papers):
        doi = p.get('doi', '')
        pmid = p['id']
        title = p.get('title', 'Unknown')[:60]
        
        if not doi:
            print(f"\n   [{i+1}/{len(papers)}] PMID {pmid} 无DOI,跳过")
            print(f"      标题: {title}...")
            continue
        
        print(f"\n   [{i+1}/{len(papers)}] 下载 PMID {pmid}")
        print(f"      标题: {title}...")
        print(f"      DOI: {doi}")
        
        filepath = await download_pdf_safe(doi, pmid, output_dir)
        if filepath:
            downloaded_files.append(filepath)
        
        # 安全延迟 (除了最后一篇)
        if i < len(papers) - 1:
            print(f"      ⏳ 等待{delay_seconds}秒后继续...")
            await asyncio.sleep(delay_seconds)
    
    print("-" * 80)
    print(f"\n✅ 下载完成! 成功: {len(downloaded_files)}/{len(papers)}")
    return downloaded_files


def download_top_papers(
    papers: List[Dict[str, Any]], 
    top_n: int = 5,
    email: str = "your_email@example.com",
    delay_seconds: int = 60,
    output_dir: str = "downloaded_pdfs"
) -> List[str]:
    """
    下载评分最高的N篇文献PDF (同步包装函数)
    
    Args:
        papers: 文献列表
        top_n: 下载前N篇
        email: Entrez API所需的email
        delay_seconds: 每篇下载间隔秒数
        output_dir: 输出目录
        
    Returns:
        成功下载的PDF文件路径列表
    """
    # 提取评分最高的N篇
    top_papers = sorted(papers, key=lambda x: x.get('score', 0), reverse=True)[:top_n]
    
    print(f"\n📥 [Step 8] 准备下载评分最高的 {top_n} 篇文献PDF...")
    print("-" * 80)
    for i, p in enumerate(top_papers):
        print(f"   {i+1}. [分数:{p.get('score', 0)}] {p.get('title', 'Unknown')[:60]}...")
        print(f"      PMID: {p['id']}")
    print("-" * 80)
    
    # Step 9: PMID → DOI
    top_papers_with_doi = convert_pmids_to_dois(top_papers, email)
    
    # Step 10: 批量下载
    downloaded_files = asyncio.run(
        batch_download_pdfs(top_papers_with_doi, delay_seconds, output_dir)
    )
    
    return downloaded_files


if __name__ == "__main__":
    # 测试用例
    test_papers = [
        {
            'id': '36054302',
            'title': 'Clinical outcomes of dental implants in patients with and without history of periodontitis',
            'score': 15
        }
    ]
    
    print("🧪 测试PDF下载模块...")
    downloaded = download_top_papers(
        test_papers, 
        top_n=1, 
        email="test@example.com",
        delay_seconds=5  # 测试时使用较短延迟
    )
    
    print(f"\n✅ 测试完成! 下载文件: {downloaded}")
