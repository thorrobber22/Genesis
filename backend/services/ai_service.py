# backend/services/ai_service.py - FIXED WITH DEBUG
"""AI Service with validation and citation extraction - DEBUG VERSION"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import traceback

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import AsyncOpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai==1.3.0")
    from openai import AsyncOpenAI

try:
    import google.generativeai as genai
except ImportError:
    print("Installing google-generativeai...")
    os.system("pip install google-generativeai")
    import google.generativeai as genai

class AIService:
    """Enhanced AI service with validation and chat"""
    
    def __init__(self):
        # Get API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        print(f"🔑 OpenAI Key: {'✅' if openai_key else '❌'}")
        print(f"🔑 Gemini Key: {'✅' if gemini_key else '❌'}")
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize AI clients
        try:
            self.openai = AsyncOpenAI(api_key=openai_key)
            print("✅ OpenAI client initialized")
        except Exception as e:
            print(f"❌ OpenAI init error: {e}")
            self.openai = None
            
        # Initialize Gemini
        try:
            genai.configure(api_key=gemini_key)
            self.gemini = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini client initialized")
        except Exception as e:
            print(f"❌ Gemini init error: {e}")
            self.gemini = None
        
    async def validate_ipo_data(self, ipo: Dict[str, Any]) -> Dict[str, Any]:
        """Silently validate IPO data with both models"""
        
        print(f"\n🔍 Validating IPO: {ipo.get('ticker')} - {ipo.get('company')}")
        
        # Run validations
        results = []
        
        # Try OpenAI
        if self.openai:
            try:
                openai_result = await self._validate_with_openai(ipo)
                print(f"  OpenAI result: {openai_result}")
                results.append(openai_result)
            except Exception as e:
                print(f"  ❌ OpenAI error: {e}")
                traceback.print_exc()
        
        # Try Gemini
        if self.gemini:
            try:
                gemini_result = await self._validate_with_gemini(ipo)
                print(f"  Gemini result: {gemini_result}")
                results.append(gemini_result)
            except Exception as e:
                print(f"  ❌ Gemini error: {e}")
                traceback.print_exc()
        
        # Combine results
        return self._combine_validations(results, ipo)
    
    async def _validate_with_openai(self, ipo: Dict) -> Dict:
        """OpenAI validation"""
        try:
            prompt = f"""
            Validate this IPO data:
            Company: {ipo.get('company')}
            Ticker: {ipo.get('ticker')}
            CIK: {ipo.get('cik')}
            
            Return JSON: {{"cik_valid": true, "lockup_valid": true, "confidence": 0.8}}
            """
            
            response = await self.openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Use 3.5 for testing
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            print(f"    OpenAI raw response: {content}")
            
            # Try to parse JSON
            try:
                return json.loads(content)
            except:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {"error": "Could not parse response"}
            
        except Exception as e:
            print(f"    OpenAI exception: {str(e)}")
            return {"error": str(e), "source": "openai"}
    
    async def _validate_with_gemini(self, ipo: Dict) -> Dict:
        """Gemini validation"""
        try:
            prompt = f"""
            Validate IPO data and return ONLY JSON:
            Company: {ipo.get('company')}
            CIK: {ipo.get('cik')}
            
            {{"cik_valid": true, "lockup_valid": true, "confidence": 0.8}}
            """
            
            response = await asyncio.to_thread(
                self.gemini.generate_content,
                prompt
            )
            
            text = response.text.strip()
            print(f"    Gemini raw response: {text}")
            
            # Clean up response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            # Try to find JSON
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {"error": "Could not parse Gemini response"}
            
        except Exception as e:
            print(f"    Gemini exception: {str(e)}")
            return {"error": str(e), "source": "gemini"}
    
    def _combine_validations(self, results: List[Dict], ipo: Dict) -> Dict:
        """Combine validation results"""
        print(f"\n  Combining {len(results)} results...")
        
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            print("  ❌ No valid results")
            return {
                "validated": False,
                "confidence": 0.0,
                "error": "No successful validations"
            }
        
        # Calculate averages
        cik_valid = all(r.get('cik_valid', False) for r in valid_results)
        lockup_valid = all(r.get('lockup_valid', False) for r in valid_results)
        avg_confidence = sum(r.get('confidence', 0) for r in valid_results) / len(valid_results)
        
        result = {
            "validated": True,
            "cik_valid": cik_valid,
            "lockup_valid": lockup_valid,
            "confidence": avg_confidence,
            "validators_agreed": len(set(r.get('cik_valid') for r in valid_results)) == 1,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"  ✅ Combined result: {result}")
        return result