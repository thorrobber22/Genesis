"""
Data Cards for Chat Display
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class DataCards:
    def calendar_card(self):
        """Generate calendar view card"""
        # Load IPO calendar
        cal_file = Path("data/cache/ipo_calendar.json")
        if not cal_file.exists():
            return "No IPO calendar data available yet."
        
        with open(cal_file) as f:
            data = json.load(f)
        
        ipos = data.get("data", [])
        
        # Group by week
        output = "### Upcoming IPOs\n\n"
        
        # This week
        this_week = [ipo for ipo in ipos if self._is_this_week(ipo.get("date"))]
        if this_week:
            output += "**This Week**\n"
            for ipo in this_week:
                ticker = ipo.get("ticker", "")
                company = ipo.get("company", "Unknown")
                price_range = ipo.get("price_range", "TBD")
                coverage = "Full Coverage" if self._has_docs(ticker) else "No Docs"
                output += f"• **{ticker}** - {company} [{price_range}] - {coverage}\n"
        
        # Next week
        output += "\n**Next Week**\n"
        next_week = [ipo for ipo in ipos if self._is_next_week(ipo.get("date"))]
        if next_week:
            for ipo in next_week[:3]:  # Show max 3
                ticker = ipo.get("ticker", "")
                company = ipo.get("company", "Unknown")
                output += f"• **{ticker}** - {company}\n"
        else:
            output += "• Check back for updates\n"
        
        output += "\n*Type any ticker name to see details*"
        
        return output
    
    def pricing_card(self):
        """Generate pricing analysis card"""
        cal_file = Path("data/cache/ipo_calendar.json")
        if not cal_file.exists():
            return "No pricing data available yet."
        
        with open(cal_file) as f:
            data = json.load(f)
        
        output = "### IPO Pricing Analysis\n\n"
        output += "| Ticker | Price Range | Shares | Val @Mid |\n"
        output += "|--------|-------------|--------|----------|\n"
        
        for ipo in data.get("data", [])[:5]:  # Top 5
            ticker = ipo.get("ticker", "")
            price_range = ipo.get("price_range", "TBD")
            shares = ipo.get("shares", "TBD")
            
            # Calculate valuation if possible
            val = self._calculate_valuation(price_range, shares)
            
            output += f"| {ticker} | {price_range} | {shares} | {val} |\n"
        
        output += "\n*Ask me about any ticker for detailed metrics*"
        
        return output
    
    def lockup_card(self):
        """Generate lock-up calendar card"""
        lockup_file = Path("data/cache/lockup_calendar.json")
        
        output = "### Lock-up Expiration Calendar\n\n"
        
        if lockup_file.exists():
            with open(lockup_file) as f:
                data = json.load(f)
            
            lockups = data.get("data", [])
            
            for lockup in lockups[:5]:  # Top 5 upcoming
                ticker = lockup.get("ticker")
                days = lockup.get("days_until", 0)
                shares = lockup.get("shares_unlocking", 0)
                
                output += f"**{ticker}** - {days} days\n"
                output += f"• {shares:,} shares unlocking\n"
                output += f"• {lockup.get('lockup_days', 180)}-day lock-up\n\n"
        else:
            output += "Lock-up data will be available once S-1s are processed.\n"
        
        output += "*Ask me to generate detailed lock-up reports*"
        
        return output
    
    def filings_card(self):
        """Generate recent filings card"""
        output = "### Recent SEC Filings\n\n"
        
        # Check documents directory
        doc_dir = Path("data/documents")
        if not doc_dir.exists():
            return output + "No documents uploaded yet."
        
        # Get recent files
        files = sorted(doc_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not files:
            return output + "No documents uploaded yet."
        
        # Group by date
        today_count = 0
        yesterday_count = 0
        week_count = len(files)
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        for file in files[:10]:
            file_date = datetime.fromtimestamp(file.stat().st_mtime).date()
            
            if file_date == today:
                today_count += 1
            elif file_date == yesterday:
                yesterday_count += 1
        
        output += f"**Today**: {today_count} documents\n"
        output += f"**Yesterday**: {yesterday_count} documents\n"
        output += f"**This Week**: {week_count} total\n\n"
        
        # Show recent uploads
        output += "**Recent Uploads:**\n"
        for file in files[:3]:
            ticker = file.name.split('_')[0]
            upload_time = datetime.fromtimestamp(file.stat().st_mtime).strftime("%I:%M %p")
            output += f"• {ticker} - {upload_time}\n"
        
        return output
    
    def _is_this_week(self, date_str):
        """Check if date is this week"""
        # Simple check - implement proper date logic
        return True
    
    def _is_next_week(self, date_str):
        """Check if date is next week"""
        # Simple check - implement proper date logic
        return False
    
    def _has_docs(self, ticker):
        """Check if ticker has documents"""
        doc_dir = Path("data/documents")
        if doc_dir.exists():
            return any(doc_dir.glob(f"{ticker}_*"))
        return False
    
    def _calculate_valuation(self, price_range, shares_str):
        """Calculate market cap at midpoint"""
        try:
            # Extract midpoint price
            if "-" in price_range and "$" in price_range:
                prices = price_range.replace("$", "").split("-")
                midpoint = (float(prices[0]) + float(prices[1])) / 2
                
                # Extract share count
                if "M" in str(shares_str):
                    shares = float(str(shares_str).replace("M", "")) * 1_000_000
                    
                    # Calculate market cap
                    market_cap = midpoint * shares / 1_000_000_000
                    return f"${market_cap:.1f}B"
        except:
            pass
        
        return "TBD"
