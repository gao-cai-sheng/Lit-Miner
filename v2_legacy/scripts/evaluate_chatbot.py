
import os
import sys
import json
import time
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.chatbot.rag_engine import RAGEngine
from core.chatbot.answer_generator import AnswerGenerator
from core.llm.llm_client import LLMClient
from config import GEMINI_API_KEY, DEEPSEEK_API_KEY

def evaluate():
    print("="*60)
    print("🤖 Chatbot Evaluation System (LLM-as-a-Judge)")
    print("="*60)

    # 1. Initialize Components
    print("\n[Init] Loading RAG Context and Judges...")
    try:
        rag = RAGEngine()
        # AnswerGenerator currently uses direct DeepSeek calls, which is fine for testing "as-is" prod state
        generator = AnswerGenerator() 
        # Judge uses our unified client (preferring Gemini for judging)
        judge = LLMClient(gemini_key=GEMINI_API_KEY, deepseek_key=DEEPSEEK_API_KEY)
    except Exception as e:
        print(f"❌ Init failed: {e}")
        return

    # 2. Test Dataset
    questions = [
        {
            "id": 1,
            "q": "What are the primary pathogens associated with periodontitis?",
            "concepts": ["Porphyromonas gingivalis", "Tannerella forsythia", "Treponema denticola", "red complex"]
        },
        {
            "id": 2,
            "q": "How does diabetes mellitus affect periodontal health?",
            "concepts": ["bidirectional", "inflammation", "delayed healing", "glucose"]
        },
         {
            "id": 3,
            "q": "What is the clinical definition of peri-implantitis?",
            "concepts": ["inflammation", "bone loss", "bleeding on probing", "implants"]
        },
        {
            "id": 4,
            "q": "What are the advantages of local drug delivery in periodontics?",
            "concepts": ["concentration", "side effects", "compliance", "site-specific"]
        },
        {
            "id": 5,
            "q": "Describe the Guided Tissue Regeneration (GTR) principle.",
            "concepts": ["barrier membrane", "exclude epithelium", "regeneration", "periodontal ligament"]
        }
    ]

    results = []
    
    print(f"\n[Test] Running pipeline on {len(questions)} questions...\n")

    for item in questions:
        q = item['q']
        print(f"🔹 Q{item['id']}: {q}")
        
        start_time = time.time()
        
        # A. Retrieval
        retrieved = rag.retrieve(q, top_k=5)
        retrieve_time = time.time() - start_time
        
        # Check retrieval content
        retrieved_text = "\n".join([r['content'] for r in retrieved])
        retrieved_titles = [r['metadata'].get('title', 'Unknown') for r in retrieved]
        
        # B. Generation
        gen_start = time.time()
        ans_res = generator.generate(q, retrieved)
        answer = ans_res['answer']
        sources = ans_res['sources']
        gen_time = time.time() - gen_start
        
        # C. Evaluation (The Judge)
        eval_prompt = f"""
        You are an expert Periodontist and AI evaluator. Grade the following RAG interaction.
        
        QUESTION: {q}
        
        EXPECTED CONCEPTS: {', '.join(item['concepts'])}
        
        RETRIEVED CONTEXT TITLES: {retrieved_titles}
        RETRIEVED CONTENT SNIPPET: {retrieved_text[:1000]}...
        
        AI ANSWER: {answer}
        
        Evaluate on 3 metrics (1-5 score):
        1. Retrieval Relevance: Is the retrieved context relevant to the question?
        2. Answer Fidelity: Is the answer supported by the retrieved context? (No hallucinations)
        3. Answer Quality: Is the answer accurate, comprehensive, and helpful?
        
        Output strictly in JSON format:
        {{
            "retrieval_score": <int>,
            "fidelity_score": <int>,
            "quality_score": <int>,
            "reasoning": "<short explanation>"
        }}
        """
        
        try:
            # System prompt for JSON
            judge_res = judge.chat_completion([
                {"role": "system", "content": "You are a helpful assistant that outputs strictly JSON."},
                {"role": "user", "content": eval_prompt}
            ])
            # Clean generic markdown code blocks if present
            judge_res = judge_res.replace("```json", "").replace("```", "").strip()
            scores = json.loads(judge_res)
        except Exception as e:
            print(f"  ⚠️ Judge failed: {e}")
            scores = {"retrieval_score": 0, "fidelity_score": 0, "quality_score": 0, "reasoning": "Judge Error"}

        # Store result
        res_entry = {
            "id": item['id'],
            "q": q,
            "retrieval_count": len(retrieved),
            "cit_count": len(sources),
            "scores": scores,
            "times": {"retrieval": retrieve_time, "generation": gen_time}
        }
        results.append(res_entry)
        
        # Print Summary
        print(f"  ✅ R({len(retrieved)}) | C({len(sources)}) | Time: {retrieve_time+gen_time:.2f}s")
        print(f"  🏆 Scores: R={scores['retrieval_score']} F={scores['fidelity_score']} Q={scores['quality_score']}")
        print(f"  📝 Judge: {scores.get('reasoning', 'No reasoning')[:100]}...")
        print("-" * 40)

    # 3. Final Report
    print("\n" + "="*60)
    print("📊 FINAL EVALUATION REPORT")
    print("="*60)
    
    avg_r = sum(r['scores']['retrieval_score'] for r in results) / len(results)
    avg_f = sum(r['scores']['fidelity_score'] for r in results) / len(results)
    avg_q = sum(r['scores']['quality_score'] for r in results) / len(results)
    avg_cit = sum(r['cit_count'] for r in results) / len(results)
    
    print(f"Overall Metrics (N={len(results)}):")
    print(f"  🔍 Avg Retrieval Relevance: {avg_r:.1f}/5.0")
    print(f"  🤥 Avg Answer Fidelity:     {avg_f:.1f}/5.0")
    print(f"  ⭐ Avg Answer Quality:      {avg_q:.1f}/5.0")
    print(f"  📚 Avg Citations per Ans:   {avg_cit:.1f}")
    
    print("\nRecommendations based on score:")
    if avg_r < 3.5:
        print("  ❌ Retrieval needs improvement. Check embeddings or chunk size.")
    elif avg_r > 4.5:
        print("  ✅ Retrieval is excellent.")
        
    if avg_f < 3.5:
        print("  ❌ Model is hallucinating. Reduce temperature or enforce citation constraints.")
        
    if avg_q < 3.5:
        print("  ❌ Answer quality is low. Improve prompt or model model.")
        
    print("="*60)

if __name__ == "__main__":
    evaluate()
