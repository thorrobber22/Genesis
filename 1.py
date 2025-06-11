# In the IPO Scraper tab, replace the button action with:

if st.button("🔄 Scrape IPOScoop", use_container_width=True, type="primary"):
    with st.spinner("Scraping real IPO data..."):
        from services.pipeline_orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator()
        result = run_async(orchestrator.run_full_pipeline(auto_download=False))
        
        if result:
            st.success(f"✅ Scraped {result['summary']['total_ipos']} IPOs!")
            st.info(f"📊 Found CIKs for {result['summary']['with_ciks']} companies")
            st.info(f"📝 Created {result['summary']['new_requests']} new requests")
            
            # Show sample data
            if result['ipo_data'].get('recently_priced'):
                st.subheader("Recently Priced IPOs")
                for ipo in result['ipo_data']['recently_priced'][:5]:
                    st.write(f"**{ipo.get('company_name')}** ({ipo.get('ticker', 'N/A')})")
                    if ipo.get('cik'):
                        st.write(f"CIK: {ipo['cik']}")