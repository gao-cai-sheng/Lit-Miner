"""
Unified LLM Client
Handles interactions with multiple LLM providers (Gemini, DeepSeek) with priority logic.
Priority: Gemini > DeepSeek > Error
"""

import os
import requests
import google.generativeai as genai
from typing import List, Dict, Optional, Union

class LLMClient:
    def __init__(self, gemini_key: Optional[str] = None, deepseek_key: Optional[str] = None):
        """
        Initialize LLM Client with API keys.
        
        Args:
            gemini_key: Google Gemini API Key
            deepseek_key: DeepSeek API Key
        """
        self.gemini_key = gemini_key
        self.deepseek_key = deepseek_key
        
        # Configure Gemini if key is provided
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)

    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "auto", 
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate chat completion using the highest priority available provider.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model name (ignored for auto-selection logic usually, but passed if specific)
            temperature: Randomness
            max_tokens: Max output length
            
        Returns:
            Generated text content
        """
        # Priority 1: Gemini
        if self.gemini_key:
            try:
                return self._call_gemini(messages, temperature=temperature)
            except Exception as e:
                print(f"⚠️ Gemini call failed: {e}, falling back to DeepSeek...")
                # Fallback to DeepSeek if Gemini fails
                if self.deepseek_key:
                    return self._call_deepseek(messages, temperature=temperature, max_tokens=max_tokens)
                raise e

        # Priority 2: DeepSeek
        elif self.deepseek_key:
            return self._call_deepseek(messages, temperature=temperature, max_tokens=max_tokens)
            
        else:
            raise ValueError("No API keys provided. Please set GEMINI_API_KEY or DEEPSEEK_API_KEY.")

    def _call_gemini(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Call Google Gemini API"""
        # Convert OpenAI-style messages to Gemini format
        # Gemini uses 'user' and 'model' roles. OpenAI uses 'user' and 'assistant'.
        # Also, Gemini history structure is slightly different.
        
        # Simple System Prompt handling:
        # If the first message is system, prepend it to the first user message or set config
        # Here we'll just prepend to user message for simplicity or use system_instruction if supported
        
        history = []
        system_instruction = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_instruction = content
            elif role == "user":
                history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})
        
        # Ensure the last message is from user (Gemini restriction on chat history usually requires alternating)
        # But for 'generate_content' with a prompt, it's easier.
        # Let's use `GenerativeModel.generate_content` for stateless or construct a chat session.
        # For simple completion, we can concatenate or use chat.
        
        model_name = "gemini-pro" # Default to a good model
        generation_config = genai.types.GenerationConfig(
            temperature=temperature
        )
        
        model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        
        # For simplicity in this unified interface, we'll assume the last message is the prompt
        # and previous ones are history.
        if not history:
            raise ValueError("No messages provided for Gemini generation")
            
        # If it's just one prompt (common case in this app)
        if len(history) == 1 and history[0]["role"] == "user":
             response = model.generate_content(
                 history[0]["parts"][0], 
                 generation_config=generation_config
             )
             return response.text
             
        # Multi-turn chat
        chat = model.start_chat(history=history[:-1])
        response = chat.send_message(
            history[-1]["parts"][0],
            generation_config=generation_config
        )
        return response.text

    def _call_deepseek(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """Call DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            json=data,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
