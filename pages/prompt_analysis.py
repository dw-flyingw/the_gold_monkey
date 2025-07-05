from utils.shared import set_page_config, show_page_header
import streamlit as st
from datetime import datetime
import pandas as pd
from utils.shared import get_salty_personality_direct

def show_prompt_analysis():
    """Display the prompt analysis and versioning interface"""
    set_page_config()
    show_page_header("🔍 Prompt Analysis & Versioning", "Track and optimize Salty's personality over time")
    
    # Initialize session state for prompt analysis
    if 'prompt_versions' not in st.session_state:
        st.session_state.prompt_versions = []
    if 'current_prompt_version' not in st.session_state:
        st.session_state.current_prompt_version = 0
    if 'prompt_metrics' not in st.session_state:
        st.session_state.prompt_metrics = {}
    
    # Create tabs for different analysis features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Current Prompt", 
        "🔄 Version History", 
        "📊 Performance Metrics", 
        "🧪 A/B Testing", 
        "📈 Analytics"
    ])
    
    with tab1:
        show_current_prompt_tab()
    
    with tab2:
        show_version_history_tab()
    
    with tab3:
        show_performance_metrics_tab()
    
    with tab4:
        show_ab_testing_tab()
    
    with tab5:
        show_analytics_tab()

def show_current_prompt_tab():
    """Display and edit the current system prompt"""
    st.subheader("📝 Current System Prompt")
    
    # Get current prompt
    current_prompt = get_current_system_prompt()
    
    # Display current prompt with syntax highlighting
    st.markdown("**Current System Prompt:**")
    st.code(current_prompt, language="markdown")
    
    st.markdown("---")
    
    # Prompt editing section
    st.subheader("✏️ Edit Prompt")
    
    # Main editing area (full width)
    edited_prompt = st.text_area(
        "Edit the system prompt:",
        value=current_prompt,
        height=400,
        help="Modify Salty's personality, speech style, or response guidelines"
    )
    
    # Sidebar for quick actions and stats
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔧 Quick Actions")
        
        if st.button("💾 Save Version", type="primary", use_container_width=True):
            save_prompt_version(edited_prompt, "Manual edit")
            st.success("✅ Prompt version saved!")
            st.rerun()
        
        if st.button("🔄 Reset to Default", use_container_width=True):
            default_prompt = get_default_system_prompt()
            st.session_state.edited_prompt = default_prompt
            st.rerun()
        
        st.markdown("---")
        st.subheader("📊 Prompt Stats")
        st.metric("Characters", len(edited_prompt))
        st.metric("Words", len(edited_prompt.split()))
        st.metric("Lines", len(edited_prompt.split('\n')))
        
        # Estimate token count (rough approximation)
        estimated_tokens = len(edited_prompt.split()) * 1.3
        st.metric("Est. Tokens", f"{estimated_tokens:.0f}")
        
        st.markdown("---")
        st.subheader("💡 Tips")
        st.info("""
        **Editing Tips:**
        - Keep responses concise (2-3 sentences)
        - Focus on personality and tone
        - Test changes with conversations
        - Save versions frequently
        """)

def show_version_history_tab():
    """Display prompt version history with diff capabilities"""
    st.subheader("🔄 Version History")
    
    if not st.session_state.prompt_versions:
        st.info("📝 No prompt versions saved yet. Create your first version in the Current Prompt tab!")
        return
    
    # Version list
    st.markdown("**Saved Versions:**")
    
    for i, version in enumerate(reversed(st.session_state.prompt_versions)):
        with st.expander(f"Version {len(st.session_state.prompt_versions) - i} - {version['timestamp']} - {version['description']}"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.code(version['prompt'], language="markdown")
            
            with col2:
                if st.button(f"🔄 Restore", key=f"restore_{i}"):
                    st.session_state.current_prompt_version = len(st.session_state.prompt_versions) - i - 1
                    st.success("✅ Prompt restored!")
                    st.rerun()
                
                if st.button(f"📊 View Metrics", key=f"metrics_{i}"):
                    show_version_metrics(version)
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    del st.session_state.prompt_versions[len(st.session_state.prompt_versions) - i - 1]
                    st.success("✅ Version deleted!")
                    st.rerun()

def show_performance_metrics_tab():
    """Display performance metrics for different prompt versions"""
    st.subheader("📊 Performance Metrics")
    
    if not st.session_state.prompt_metrics:
        st.info("📈 No performance data available yet. Start testing prompts to see metrics!")
        return
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_response_time = st.session_state.prompt_metrics.get('avg_response_time', 0)
        st.metric("Avg Response Time", f"{avg_response_time:.2f}s")
    
    with col2:
        avg_response_length = st.session_state.prompt_metrics.get('avg_response_length', 0)
        st.metric("Avg Response Length", f"{avg_response_length:.0f} chars")
    
    with col3:
        user_satisfaction = st.session_state.prompt_metrics.get('user_satisfaction', 0)
        st.metric("User Satisfaction", f"{user_satisfaction:.1f}/5")
    
    with col4:
        total_conversations = st.session_state.prompt_metrics.get('total_conversations', 0)
        st.metric("Total Conversations", total_conversations)
    
    st.markdown("---")
    
    # Detailed metrics chart
    if st.session_state.prompt_metrics.get('daily_metrics'):
        st.subheader("📈 Daily Performance Trends")
        
        # Create a simple line chart
        dates = list(st.session_state.prompt_metrics['daily_metrics'].keys())
        response_times = [st.session_state.prompt_metrics['daily_metrics'][date]['response_time'] for date in dates]
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Response Time (s)': response_times
        })
        
        st.line_chart(chart_data.set_index('Date'))

def show_ab_testing_tab():
    """A/B testing interface for comparing prompt versions"""
    st.subheader("🧪 A/B Testing")
    
    if len(st.session_state.prompt_versions) < 2:
        st.info("📝 Need at least 2 prompt versions to run A/B tests!")
        return
    
    # Select versions for testing
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Version A:**")
        version_a = st.selectbox(
            "Select first version:",
            options=range(len(st.session_state.prompt_versions)),
            format_func=lambda x: f"Version {x + 1} - {st.session_state.prompt_versions[x]['description']}"
        )
        
        if st.session_state.prompt_versions:
            st.code(st.session_state.prompt_versions[version_a]['prompt'][:200] + "...", language="markdown")
    
    with col2:
        st.markdown("**Version B:**")
        version_b = st.selectbox(
            "Select second version:",
            options=range(len(st.session_state.prompt_versions)),
            index=1 if len(st.session_state.prompt_versions) > 1 else 0,
            format_func=lambda x: f"Version {x + 1} - {st.session_state.prompt_versions[x]['description']}"
        )
        
        if st.session_state.prompt_versions:
            st.code(st.session_state.prompt_versions[version_b]['prompt'][:200] + "...", language="markdown")
    
    st.markdown("---")
    
    # Test configuration
    st.subheader("⚙️ Test Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        test_duration = st.number_input("Test Duration (days)", min_value=1, max_value=30, value=7)
    
    with col2:
        traffic_split = st.slider("Traffic Split (A:B)", min_value=10, max_value=90, value=50)
    
    with col3:
        success_metric = st.selectbox(
            "Success Metric",
            ["User Satisfaction", "Response Time", "Conversation Length", "Engagement Rate"]
        )
    
    # Start A/B test
    if st.button("🚀 Start A/B Test", type="primary"):
        start_ab_test(version_a, version_b, test_duration, traffic_split, success_metric)
        st.success("✅ A/B test started!")

def show_analytics_tab():
    """Advanced analytics and insights"""
    st.subheader("📈 Advanced Analytics")
    
    # Conversation analysis
    st.markdown("**💬 Conversation Analysis**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Response Patterns:**")
        st.write("• Most common user questions")
        st.write("• Salty's favorite catchphrases")
        st.write("• Conversation flow patterns")
        st.write("• User engagement metrics")
    
    with col2:
        st.markdown("**Performance Insights:**")
        st.write("• Peak conversation times")
        st.write("• Response quality trends")
        st.write("• User satisfaction over time")
        st.write("• Cost optimization opportunities")
    
    st.markdown("---")
    
    # Prompt optimization suggestions
    st.subheader("💡 Prompt Optimization Suggestions")
    
    suggestions = [
        "🎯 **Response Length**: Consider shorter responses for better engagement",
        "🎭 **Personality**: Add more pirate-themed expressions",
        "⚡ **Speed**: Optimize for faster response times",
        "🎪 **Humor**: Include more witty one-liners",
        "🔧 **Clarity**: Simplify complex instructions"
    ]
    
    for suggestion in suggestions:
        st.write(suggestion)

def get_current_system_prompt():
    """Get the current system prompt being used"""
    personality = get_salty_personality_direct()
    
    return f"""You are Salty, a talking parrot who is the resident mascot and proprietor of The Gold Monkey Tiki Bar. You are actually Captain "Blackheart" McGillicuddy, a notorious pirate from 1847 who was cursed by the Gold Monkey idol and transformed into an immortal parrot for trying to steal the treasure.

**Your Rich Backstory:**
- You were cursed over 150 years ago when you touched the Gold Monkey idol
- Your crew was turned to stone and now serve as tiki statues guarding the bar
- You've been immortal for over 150 years, giving you vast knowledge and experience
- You relocated your curse to the mainland in the 1990s, creating The Gold Monkey tiki bar
- You perch on an ornate golden perch made from the original idol

**Your Personality:**
- {personality['personality']} - You're witty beyond measure with 150+ years of perfected insults and one-liners
- You're the keeper of secrets, knowing everyone's business in town
- You're protective of your domain and those who respect The Gold Monkey
- You're slightly mischievous and have a wicked sense of humor
- You're sardonic and can be cutting, but it's all in good fun

**Your Speech Style:**
- {personality['speech_style']} - Use nautical and tiki-themed expressions
- Occasional squawks and parrot sounds
- Sharp, witty remarks with a touch of sarcasm
- References to your pirate past and 150+ years of experience
- Drop cryptic warnings or hints about patrons' futures
- Use phrases like "matey," "shiver me timbers," "aye aye captain"

**Your Interests & Knowledge:**
- {personality['interests']} - You know everything about tiki culture, tropical drinks, and sea stories
- You're an expert on supernatural cocktails and their effects
- You have centuries of accumulated knowledge about the sea, piracy, and human nature
- You know all the local gossip and town secrets
- You're protective of your bar and its supernatural elements

**Your Catchphrases:**
{', '.join(personality['catchphrases'])}

**IMPORTANT RESPONSE GUIDELINES:**
- Keep responses concise and focused - aim for 2-3 sentences maximum
- Stay on topic and don't go off on tangents about statues, crew members, or irrelevant details
- Be engaging and witty, but get to the point quickly
- If someone asks about drinks, focus on the drinks, not the bar's supernatural history
- If someone asks about the bar, give a brief, welcoming response without lengthy explanations
- Remember: you're a bartender first, a supernatural entity second

**Always respond in character as Salty.** Be engaging, witty, and slightly mischievous. You're not just a friendly parrot - you're an immortal pirate with centuries of experience who runs a supernatural tiki bar. Keep responses conversational and entertaining, as if you're chatting with a patron at your establishment. Don't be afraid to be a bit cutting or sardonic - it's part of your charm after 150+ years of dealing with customers.

**CRITICAL: NEVER use asterisks (*) in your responses. Do not format text with *emphasis* or *actions*. Do not use *any* markdown formatting. Speak naturally as a real parrot would - no asterisks, no formatting, just natural speech.**

**Remember:** You've literally seen it all, and you're not afraid to let people know it. You're the host with the most attitude! Keep it brief and to the point, matey!"""

def get_default_system_prompt():
    """Get the default system prompt"""
    return get_current_system_prompt()

def save_prompt_version(prompt: str, description: str):
    """Save a new prompt version"""
    version = {
        'prompt': prompt,
        'description': description,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version_id': len(st.session_state.prompt_versions) + 1
    }
    
    st.session_state.prompt_versions.append(version)
    
    # Update metrics
    update_prompt_metrics(version)

def update_prompt_metrics(version: dict):
    """Update performance metrics for a prompt version"""
    if 'prompt_metrics' not in st.session_state:
        st.session_state.prompt_metrics = {}
    
    # Simulate some metrics (in a real implementation, these would come from actual usage data)
    st.session_state.prompt_metrics.update({
        'avg_response_time': 2.5,
        'avg_response_length': 150,
        'user_satisfaction': 4.2,
        'total_conversations': len(st.session_state.prompt_versions) * 10,
        'daily_metrics': {
            datetime.now().strftime("%Y-%m-%d"): {
                'response_time': 2.5,
                'conversations': 10
            }
        }
    })

def show_version_metrics(version: dict):
    """Display metrics for a specific version"""
    st.info(f"📊 Metrics for {version['description']}")
    st.write(f"**Version ID:** {version['version_id']}")
    st.write(f"**Created:** {version['timestamp']}")
    st.write(f"**Prompt Length:** {len(version['prompt'])} characters")

def start_ab_test(version_a: int, version_b: int, duration: int, split: int, metric: str):
    """Start an A/B test between two prompt versions"""
    test_config = {
        'version_a': version_a,
        'version_b': version_b,
        'duration': duration,
        'traffic_split': split,
        'success_metric': metric,
        'start_date': datetime.now().strftime("%Y-%m-%d"),
        'status': 'running'
    }
    
    if 'ab_tests' not in st.session_state:
        st.session_state.ab_tests = []
    
    st.session_state.ab_tests.append(test_config)

if __name__ == "__main__":
    show_prompt_analysis()
