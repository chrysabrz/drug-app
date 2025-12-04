#!/usr/bin/env python3
"""
Render functions for AI Agent pages
Q&A, Publication Analysis, and Research Synthesis for atherosclerosis research
"""

import streamlit as st
import os
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import agents
try:
    from agents.qa_agent import AtheroQAAgent
    from agents.publication_analyzer import PublicationAnalyzer
    from agents.synthesis_agent import ResearchSynthesisAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

try:
    from agents.qa_with_metrics import TrustworthyQAAgent
    TRUST_METRICS_AVAILABLE = True
except ImportError:
    TRUST_METRICS_AVAILABLE = False
    TrustworthyQAAgent = None  # type: ignore

def render_qa_page(all_data: List[Dict[str, Any]]):
    """Render Q&A Agent page"""
    st.header("🤖 AI Q&A with PubMed References")
    
    st.markdown("""
    Ask questions about atherosclerosis, cardiovascular disease, and lipoprotein research and get answers based on your publication database with PubMed references.
    """)
    
    if not AGENTS_AVAILABLE:
        st.warning("⚠️ AI Agents not available. Install required packages:")
        st.code("pip install openai anthropic", language="bash")
        return
    
    # Model selection - hidden, default to gpt-4o
    model = "gpt-4o"
    
    # Sources input
    num_sources = st.number_input("Sources", min_value=3, max_value=10, value=5, step=1)
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., How does PCSK9 inhibition reduce LDL cholesterol?",
        height=100,
        key="qa_query"
    )

    metrics_requested = st.toggle(
        "Compute trust metrics (semantic similarity, grounding, faithfulness, etc.)",
        value=False,
        help="Adds QA quality checks powered by embeddings, cross-encoders, and NLI. "
             "Requires OpenAI embeddings plus `sentence-transformers` and `transformers` packages.",
    )
    use_metrics = metrics_requested and TRUST_METRICS_AVAILABLE
    if metrics_requested and not TRUST_METRICS_AVAILABLE:
        st.warning(
            "Trust metrics module unavailable. Install optional dependencies:\n"
            "pip install sentence-transformers transformers"
        )
    
    run_qa = st.button("🔍 Get Answer", type="primary", use_container_width=True)
    
    if run_qa and query:
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            st.error("❌ No API keys configured. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file.")
            return
        
        spinner_msg = (
            "🤖 Generating answer and trust metrics..." if use_metrics
            else "🤖 Finding relevant papers and generating answer..."
        )
        with st.spinner(spinner_msg):
            try:
                if use_metrics and TRUST_METRICS_AVAILABLE and TrustworthyQAAgent:
                    agent = TrustworthyQAAgent(model=model)
                    result = agent.answer_question_with_metrics(query, all_data, top_k=num_sources)
                else:
                    agent = AtheroQAAgent(model=model)
                    result = agent.answer_question(query, all_data, top_k=num_sources)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                    return
                
                st.success("✅ Answer generated!")
                
                # Display answer
                st.markdown("### 📝 Answer")
                st.markdown(result["answer"])
                
                # Display sources
                st.markdown("---")
                st.markdown(f"### 📚 Sources ({result['num_sources']} publications)")
                
                for i, source in enumerate(result["sources"], 1):
                    with st.expander(f"[{i}] {source['title']} ({source['year']})"):
                        st.markdown(f"**Journal**: {source['journal']}")
                        st.markdown(f"**PMID**: {source['pmid']}")
                        st.markdown(f"**Relevance Score**: {source.get('relevance_score', 'N/A')}")
                        if source['pmid'] and source['pmid'] != 'Unknown':
                            st.markdown(f"[View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{source['pmid']}/)")

                metrics = result.get("metrics") or {}
                if metrics:
                    st.markdown("---")
                    st.markdown("### 🛡️ Trust Metrics")
                    metric_items = list(metrics.items())
                    descriptions = result.get("metrics_description", {})
                    for idx in range(0, len(metric_items), 3):
                        cols = st.columns(min(3, len(metric_items) - idx))
                        for col, (name, value) in zip(cols, metric_items[idx: idx + 3]):
                            label = name.replace("_", " ").title()
                            display_value = "N/A" if value is None else f"{value:.2f}"
                            with col:
                                st.metric(label=label, value=display_value)
                                desc = descriptions.get(name)
                                if desc:
                                    st.caption(desc)
                    notes = result.get("metric_notes") or []
                    if notes:
                        st.markdown("#### Notes")
                        for note in notes:
                            st.caption(f"• {note}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure your API keys are configured and you have internet connection.")
    
    elif run_qa and not query:
        st.warning("⚠️ Please enter a question first!")


def render_publication_analysis_page(all_data: List[Dict[str, Any]]):
    """Render Publication Analysis Agent page"""
    st.header("📝 Publication Analysis")
    
    st.markdown("""
    Analyze individual publications to extract key insights, mechanisms, and findings.
    
    **What it extracts:**
    - Main research question
    - Key findings
    - Atherosclerosis focus
    - Lipoproteins, biomarkers, and genes
    - Therapeutic interventions
    - Risk factors and comorbidities
    - Mechanisms
    - Clinical significance
    """)
    
    if not AGENTS_AVAILABLE:
        st.warning("⚠️ AI Agents not available. Install required packages:")
        st.code("pip install openai anthropic", language="bash")
        return
    
    # Publication selection
    st.markdown("### 📄 Select Publication to Analyze")
    
    # Search/filter publications
    search_term = st.text_input("Search publications:", placeholder="e.g., PCSK9 LDL cholesterol")
    
    # Filter publications
    filtered_pubs = all_data
    if search_term:
        query_lower = search_term.lower()
        filtered_pubs = [
            p for p in all_data 
            if query_lower in (p.get('title') or '').lower() or 
               query_lower in (p.get('abstract') or '').lower()
        ]
    
    if not filtered_pubs:
        st.warning("No publications found matching your search.")
        return
    
    # Select publication
    pub_titles = [f"{p.get('title', 'No title')[:100]} ({p.get('year', 'Unknown')})" for p in filtered_pubs[:100]]
    selected_idx = st.selectbox(
        "Choose a publication:",
        range(len(pub_titles)),
        format_func=lambda x: pub_titles[x]
    )
    
    selected_pub = filtered_pubs[selected_idx]
    
    # Show publication info
    st.markdown("---")
    st.markdown("### 📋 Publication Details")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Title**: {selected_pub.get('title', 'N/A')}")
        st.markdown(f"**Year**: {selected_pub.get('year', 'N/A')}")
        st.markdown(f"**Journal**: {selected_pub.get('journal', selected_pub.get('journal_name', 'N/A'))}")
    with col2:
        pmid = selected_pub.get('pmid', selected_pub.get('id', ''))
        if pmid:
            st.markdown(f"**PMID**: {pmid}")
            st.markdown(f"[View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
    
    # Model selection - hidden, default to gpt-4o
    model = "gpt-4o"
    
    analyze_btn = st.button("🔬 Analyze Publication", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            st.error("❌ No API keys configured. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file.")
            return
        
        with st.spinner("🔬 Analyzing publication..."):
            try:
                analyzer = PublicationAnalyzer(model=model)
                result = analyzer.analyze_publication(selected_pub)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                    return
                
                st.success("✅ Analysis complete!")
                st.markdown("---")
                st.markdown("### 📊 Analysis Results")
                st.markdown(result["analysis"])
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_synthesis_page(all_data: List[Dict[str, Any]]):
    """Render Research Synthesis Agent page"""
    st.header("🔬 Research Synthesis")
    
    st.markdown("""
    Synthesize insights across multiple recent publications to identify trends, themes, and emerging research directions.
    
    **What it analyzes:**
    - Emerging trends
    - Common mechanisms
    - Key discoveries
    - Research gaps
    - Future directions
    """)
    
    if not AGENTS_AVAILABLE:
        st.warning("⚠️ AI Agents not available. Install required packages:")
        st.code("pip install openai anthropic", language="bash")
        return
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        num_papers = st.number_input("Number of recent papers", min_value=5, max_value=50, value=10, step=5)
    
    with col2:
        focus = st.selectbox(
            "Focus Area:",
            ["general", "trends", "mechanisms", "clinical", "therapeutics"],
            format_func=lambda x: {
                "general": "General Overview",
                "trends": "Emerging Trends",
                "mechanisms": "Molecular Mechanisms",
                "clinical": "Clinical Applications",
                "therapeutics": "Therapeutic Interventions"
            }[x]
        )
    
    # Model selection - hidden, default to gpt-4o
    model = "gpt-4o"
    
    synthesize_btn = st.button("🔬 Synthesize Research", type="primary", use_container_width=True)
    
    if synthesize_btn:
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            st.error("❌ No API keys configured. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file.")
            return
        
        with st.spinner(f"🔬 Synthesizing insights from {num_papers} recent publications..."):
            try:
                synthesizer = ResearchSynthesisAgent(model=model)
                result = synthesizer.synthesize_recent_research(all_data, num_papers, focus)
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                    return
                
                st.success(f"✅ Synthesis complete! Analyzed {result['num_publications']} publications.")
                
                st.markdown("---")
                st.markdown("### 📊 Research Synthesis")
                st.markdown(result["synthesis"])
                
                st.markdown("---")
                st.markdown(f"**Generated**: {result['timestamp']}")
                st.markdown(f"**Model**: {result['model']}")
                st.markdown(f"**Focus**: {result['focus']}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Show recent papers that will be analyzed
    st.markdown("---")
    st.markdown("### 📚 Recent Publications (will be analyzed)")
    
    recent_pubs = sorted(
        [p for p in all_data if p.get('year') and p.get('year') != 2026],
        key=lambda x: int(x.get('year', 0)),
        reverse=True
    )[:num_papers]
    
    for i, pub in enumerate(recent_pubs, 1):
        with st.expander(f"[{i}] {pub.get('title', 'No title')[:100]} ({pub.get('year', 'Unknown')})"):
            st.markdown(f"**Year**: {pub.get('year', 'N/A')}")
            st.markdown(f"**Journal**: {pub.get('journal', pub.get('journal_name', 'N/A'))}")
            pmid = pub.get('pmid', pub.get('id', ''))
            if pmid:
                st.markdown(f"**PMID**: {pmid}")
                st.markdown(f"[View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
            abstract = pub.get('abstract', '')
            if abstract:
                st.markdown(f"**Abstract**: {abstract[:500]}...")

