"""
Orchestrator - Tool coordination
"""

from typing import Dict, List
from datetime import datetime

from tools.calendar_tool import CalendarTool
from tools.document_tool import DocumentTool
from tools.lockup_tool import LockupTool

class Orchestrator:
    def __init__(self):
        self.calendar_tool = CalendarTool()
        self.document_tool = DocumentTool()
        self.lockup_tool = LockupTool()
        
        self.tool_map = {
            "calendar_tool": self.calendar_tool,
            "document_tool": self.document_tool,
            "lockup_tool": self.lockup_tool
        }
    
    def process_with_tools(self, query: str, intent: Dict) -> Dict:
        """Process query with tools"""
        
        results = {}
        required_tools = intent.get("tools", [])
        
        for tool_name in required_tools:
            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                try:
                    results[tool_name] = tool.process(query, intent)
                except Exception as e:
                    results[tool_name] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        return {
            "status": "success",
            "results": results,
            "timestamp": datetime.now()
        }
