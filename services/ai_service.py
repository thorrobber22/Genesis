"""
services/ai_service.py - Flexible AI service for IPO data
"""

import os
from typing import Dict, List, Union
import json
from pathlib import Path
from datetime import datetime

class AIService:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_KEY')
        self.provider = 'openai' if self.openai_key else 'gemini' if self.gemini_key else None
        self.openai_model = "gpt-3.5-turbo"
        self.gemini_model = "gemini-pro"
        self.openai_client = None

        if self.provider == 'openai':
            try:
                import openai
                if hasattr(openai, 'OpenAI'):
                    self.openai_client = openai.OpenAI(api_key=self.openai_key)
            except:
                pass

        self.ipo_data = self._load_ipo_data()
        self.ipo_list = self._convert_to_list(self.ipo_data)
        self.company_data = self._load_company_data()
        print(f"AI Service initialized with {len(self.ipo_list)} IPOs loaded")

    def _load_ipo_data(self) -> Dict:
        data_sources = [
            'data/ipo_calendar.json',
            'data/ipo_data.json',
            'data/scraped_ipo_data.json'
        ]
        ipo_data = {}
        for file_path in data_sources:
            path = Path(file_path)
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        ipo_data.update(data)
                    elif isinstance(data, list):
                        for item in data:
                            ticker = item.get('ticker') or item.get('symbol')
                            if ticker:
                                ipo_data[ticker] = item
                except:
                    pass
        return ipo_data

    def _convert_to_list(self, ipo_data: Dict) -> List[Dict]:
        result = []
        for k, v in ipo_data.items():
            if isinstance(v, dict):
                v['ticker'] = k
                result.append(v)
        return result

    def _load_company_data(self) -> Dict:
        path = Path('data/processed_financials.json')
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def chat(self, message: str, context: str = None) -> str:
        try:
            system_prompt = "You are an IPO analyst assistant with access to SEC filings and IPO calendar."
            ipo_summary = f"Total IPOs: {len(self.ipo_list)}"
            full_message = f"{ipo_summary}\n\nUser: {message}"

            if self.provider == 'openai' and self.openai_client:
                return self._chat_openai(full_message, system_prompt)
            return "⚠️ No AI provider configured"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def _chat_openai(self, message: str, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": message}],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ OpenAI Error: {str(e)}"
