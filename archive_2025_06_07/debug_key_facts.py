#!/usr/bin/env python3
"""
Debug key facts extraction issue
Date: 2025-06-05 14:03:37 UTC
Author: thorrobber22
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.document_processor import DocumentProcessor

# Test content
TEST_S1_CONTENT = """
<html>
<body>
<h1>REGISTRATION STATEMENT UNDER THE SECURITIES ACT OF 1933</h1>
<p>Circle Internet Financial, Inc. is incorporated in Delaware.</p>
<p>We are listing our shares on the New York Stock Exchange under the symbol "CRCL".</p>

<h2>THE OFFERING</h2>
<p>We are offering 15,000,000 shares of our common stock.</p>
<p>Price range: $26.00 to $29.00 per share</p>

<h2>RISK FACTORS</h2>
<p>• Cryptocurrency market volatility</p>
<p>• Regulatory uncertainty</p>
<p>• Competition from other stablecoins</p>

<h2>USE OF PROCEEDS</h2>
<p>We intend to use the proceeds for general corporate purposes.</p>

<h2>CAPITALIZATION</h2>
<p>As of December 31, 2024, we had 450,000,000 shares outstanding.</p>

<h2>PRINCIPAL STOCKHOLDERS</h2>
<table>
<tr><td>Jeremy Allaire</td><td>12.5%</td></tr>
<tr><td>Goldman Sachs</td><td>8.2%</td></tr>
<tr><td>General Catalyst</td><td>7.8%</td></tr>
</table>

<h2>UNDERWRITING</h2>
<p>Goldman Sachs & Co. LLC, Morgan Stanley, and J.P. Morgan are acting as lead underwriters.</p>

<h2>LOCK-UP AGREEMENTS</h2>
<p>Our officers and directors have agreed to a 180 day lock-up period.</p>
</body>
</html>
"""

# Debug the extraction
processor = DocumentProcessor()
sections = processor.extract_sections_s1(TEST_S1_CONTENT)

print("Sections found:")
for section, content in sections.items():
    if content:
        print(f"  ✓ {section}: {len(content)} chars")
    else:
        print(f"  ✗ {section}: empty")

print("\n" + "="*50 + "\n")

# Now test key facts
key_facts = processor.extract_key_facts_s1(sections, TEST_S1_CONTENT)

print("Key facts extracted:")
for key, value in key_facts.items():
    print(f"  {key}: {value}")

# Check specific extractions
print("\n" + "="*50 + "\n")
print("Debugging specific patterns:")

# Test ticker extraction
import re
ticker_match = re.search(r"(?:symbol|ticker)[:\s\"']+([A-Z]{2,5})[\"\']?", TEST_S1_CONTENT, re.IGNORECASE)
if ticker_match:
    print(f"✓ Ticker regex found: {ticker_match.group(1)}")
else:
    print("✗ Ticker regex failed")
    # Try alternative
    alt_match = re.search(r'symbol\s*"([A-Z]+)"', TEST_S1_CONTENT)
    if alt_match:
        print(f"✓ Alternative ticker found: {alt_match.group(1)}")

# Test shares extraction
shares_match = re.search(r"(?:offering|offer|selling)\s+(?:of\s+)?(\d{1,3}(?:,\d{3})*)\s+shares", 
                        TEST_S1_CONTENT, re.IGNORECASE)
if shares_match:
    print(f"✓ Shares regex found: {shares_match.group(1)}")
else:
    print("✗ Shares regex failed")

# Test price range
price_match = re.search(r"\$(\d+(?:\.\d{2})?)\s*(?:to|-)\s*\$(\d+(?:\.\d{2})?)\s*per\s+share", 
                       TEST_S1_CONTENT, re.IGNORECASE)
if price_match:
    print(f"✓ Price range found: ${price_match.group(1)} to ${price_match.group(2)}")
else:
    print("✗ Price range regex failed")