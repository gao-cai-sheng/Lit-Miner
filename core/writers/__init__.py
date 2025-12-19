"""
Core Writers Package
AI-powered content generation for literature reviews
"""

from .deepseek_writer import DeepSeekWriter, generate_topic_from_evidence

__all__ = ['DeepSeekWriter', 'generate_topic_from_evidence']
