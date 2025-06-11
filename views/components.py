"""
View Components - Clean UI components (NO EMOJIS)
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

def render_sidebar():
    """Render sidebar navigation"""
    st.markdown("### Navigation")
    
    # Clean navigation - no descriptions or hovers
    nav_items = [
        ("Ask G", "chat"),
        ("IPO Calendar", "calendar"),
        ("Recent Filings", "filings"),
        ("Lock-ups", "lockups"),
        ("Settings", "settings")
    ]
    
    for label, view in nav_items:
        if st.button(label, use_container_width=True, key=f"nav_{view}"):
            st.session_state.current_view = view
    
    st.markdown("---")
    
    # System Status - simplified
    st.markdown("### System Status")
    st.markdown("IPO Tracker: Online", unsafe_allow_html=True)
    st.markdown("SEC EDGAR: Online", unsafe_allow_html=True)
    st.markdown("AI Models: Online", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User info - minimal
    st.caption(f"User: {st.session_state.email}")
    
    if st.button("Sign Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_chat():
    """Render chat interface - fixed at bottom"""
    st.markdown("## Ask G")
    
    # Chat messages area
    chat_container = st.container()
    with chat_container:
        for item in st.session_state.chat_history:
            col1, col2 = st.columns([1, 5])
            
            # User message
            with col2:
                st.markdown(
                    f'<div class="chat-message user-message">{item["query"]}</div>',
                    unsafe_allow_html=True
                )
            
            # Assistant response
            with col1:
                st.write("")  # Spacing
            with col2:
                st.markdown(
                    f'<div class="chat-message assistant-message">{item["response"]}</div>',
                    unsafe_allow_html=True
                )
    
    # Spacer to push input to bottom
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    
    # Input area - fixed at bottom
    with st.container():
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([10, 1])
            
            with col1:
                query = st.text_input(
                    "Message",
                    placeholder="Ask about IPOs, filings, or lock-ups...",
                    label_visibility="collapsed"
                )
            
            with col2:
                submitted = st.form_submit_button("Send", use_container_width=True)
            
            # Small grey suggestions under input
            if len(st.session_state.chat_history) == 0:
                st.markdown(
                    '<div class="chat-suggestions">'
                    '<span class="suggestion-item">What IPOs are pricing this week?</span>'
                    '<span class="suggestion-item">Show me recent S-1 filings</span>'
                    '<span class="suggestion-item">Which lock-ups expire soon?</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
            
            if submitted and query:
                # Process query
                response = st.session_state.chat_engine.process_query(query)
                
                # Execute tools if needed
                if response.get("requires_tools"):
                    tool_results = st.session_state.orchestrator.process_with_tools(
                        query, response["intent"]
                    )
                    response["tool_results"] = tool_results
                
                # Add to history
                st.session_state.chat_history.append({
                    "query": query,
                    "response": response["response"],
                    "timestamp": datetime.now()
                })
                
                st.rerun()

def render_calendar():
    """Render IPO calendar with all data"""
    st.markdown("## IPO Calendar")
    st.caption(f"Week of {datetime.now().strftime('%B %d, %Y')}")
    
    # Load calendar
    calendar_file = Path("data/cache/ipo_calendar.json")
    
    if calendar_file.exists():
        with open(calendar_file) as f:
            data = json.load(f)
        
        ipos = data.get("data", [])
        
        if ipos:
            # IPO list with G button
            for ipo in ipos:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{ipo.get('company', 'Unknown')}**")
                        st.caption(f"Ticker: {ipo.get('ticker', 'TBD')}")
                    
                    with col2:
                        st.write(ipo.get('price_range', 'TBD'))
                        st.caption("Price Range")
                    
                    with col3:
                        st.write(ipo.get('shares', 'TBD'))
                        st.caption("Shares")
                    
                    with col4:
                        st.write(ipo.get('date', 'TBD'))
                    
                    with col5:
                        # G button for analysis
                        if st.button("G", key=f"g_{ipo.get('ticker', '')}", 
                                   help="Analyze with G"):
                            # Switch to chat with context
                            st.session_state.current_view = "chat"
                            query = f"Tell me about {ipo.get('ticker')} IPO"
                            st.session_state.pending_query = query
                            st.rerun()
                    
                    # Additional data
                    cols = st.columns(4)
                    with cols[0]:
                        st.caption(f"Lead: {ipo.get('underwriter', 'TBD')}")
                    with cols[1]:
                        st.caption(f"Exchange: {ipo.get('exchange', 'TBD')}")
                    with cols[2]:
                        st.caption(f"Sector: {ipo.get('sector', 'TBD')}")
                    with cols[3]:
                        st.caption(f"Revenue: {ipo.get('revenue', 'TBD')}")
                    
                    st.markdown("---")
        else:
            st.info("No IPOs scheduled this week")
    else:
        st.info("IPO calendar loading... (Updates every 30 minutes)")

def render_filings():
    """Render recent filings"""
    st.markdown("## Recent SEC Filings")
    
    tabs = st.tabs(["S-1 Filings", "Amendments", "Final Prospectus"])
    
    edgar_file = Path("data/cache/edgar_filings.json")
    
    if edgar_file.exists():
        with open(edgar_file) as f:
            edgar_data = json.load(f)
        
        with tabs[0]:
            filings = [f for f in edgar_data.get("s1_filings", []) 
                      if f.get("form_type") == "S-1"]
            
            for filing in filings[:10]:
                render_filing_card(filing)
        
        with tabs[1]:
            amendments = [f for f in edgar_data.get("s1_filings", []) 
                         if f.get("form_type") == "S-1/A"]
            
            for filing in amendments[:10]:
                render_filing_card(filing)
        
        with tabs[2]:
            final_filings = edgar_data.get("final_prospectuses", [])
            
            for filing in final_filings[:10]:
                render_filing_card(filing)
    else:
        st.info("SEC data loading... (Updates every 5 minutes)")

def render_filing_card(filing: dict):
    """Render filing card"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"**{filing.get('company', 'Unknown')}**")
        st.caption(f"{filing.get('form_type')} - Filed: {filing.get('filed_at', '')[:10]}")
    
    with col2:
        if filing.get('filing_link'):
            st.link_button("SEC", filing['filing_link'])
    
    st.markdown("---")

def render_lockups():
    """Render lock-up calendar - show all, not just 60 days"""
    st.markdown("## Lock-up Expiration Calendar")
    
    lockup_file = Path("data/cache/lockup_calendar.json")
    
    if lockup_file.exists():
        with open(lockup_file) as f:
            data = json.load(f)
        
        # Get ALL lockups from processed files
        all_lockups = []
        processed_dir = Path("data/processed")
        
        if processed_dir.exists():
            for file in processed_dir.glob("*_ipo_data.json"):
                try:
                    with open(file) as f:
                        ipo_data = json.load(f)
                    
                    if 'ipo_date' in ipo_data:
                        ipo_date = datetime.fromisoformat(ipo_data['ipo_date'])
                        lockup_date = ipo_date + timedelta(days=180)
                        days_until = (lockup_date - datetime.now()).days
                        
                        all_lockups.append({
                            "ticker": ipo_data.get('ticker'),
                            "company": ipo_data.get('company'),
                            "ipo_date": ipo_data['ipo_date'],
                            "lockup_expiration": lockup_date.isoformat(),
                            "days_until": days_until,
                            "shares_unlocking": ipo_data.get('shares_locked', 0)
                        })
                except:
                    pass
        
        # Sort by days until
        all_lockups.sort(key=lambda x: x['days_until'])
        
        # Group display
        upcoming = [l for l in all_lockups if 0 <= l['days_until'] <= 30]
        future = [l for l in all_lockups if l['days_until'] > 30]
        past = [l for l in all_lockups if l['days_until'] < 0]
        
        if upcoming:
            st.markdown("### Next 30 Days")
            for lockup in upcoming:
                render_lockup_card(lockup)
        
        if future:
            st.markdown("### Future Expirations")
            for lockup in future[:20]:  # Limit display
                render_lockup_card(lockup)
        
        if past:
            st.markdown("### Recently Expired")
            for lockup in past[:10]:
                render_lockup_card(lockup)
        
        if not all_lockups:
            st.info("No lock-up data available yet. Processing IPO documents...")
    else:
        st.info("Lock-up calculations running... (Updates hourly)")

def render_lockup_card(lockup: dict):
    """Render lockup card"""
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown(f"**{lockup.get('company', 'Unknown')} ({lockup.get('ticker', '')})**")
        st.caption(f"IPO: {lockup.get('ipo_date', '')[:10]}")
    
    with col2:
        shares = lockup.get('shares_unlocking', 0)
        if shares > 1_000_000:
            st.write(f"{shares / 1_000_000:.1f}M shares")
        else:
            st.write(f"{shares:,} shares")
    
    with col3:
        days = lockup.get('days_until', 0)
        if days < 0:
            st.write(f"{abs(days)}d ago")
        elif days == 0:
            st.write("**Today**")
        else:
            st.write(f"{days} days")
    
    st.markdown("---")

def render_settings():
    """Settings page"""
    st.markdown("## Settings")
    
    tabs = st.tabs(["Notifications", "Data Sources"])
    
    with tabs[0]:
        st.checkbox("Daily IPO Brief (7 AM EST)", value=True)
        st.checkbox("Lock-up Alerts (7 days prior)", value=True)
        st.checkbox("New S-1 Alerts", value=False)
        st.checkbox("Material Amendment Alerts", value=True)
    
    with tabs[1]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("IPOScoop", "Active", delta="14 IPOs")
        with col2:
            st.metric("SEC EDGAR", "Active", delta="27 filings")
        with col3:
            st.metric("AI Models", "Active", delta="2 models")
