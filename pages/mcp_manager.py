import streamlit as st
from utils.shared import set_page_config, show_page_header, check_server_status
from utils.tool_registry import ToolRegistry
import asyncio
import time
import subprocess
import os
from pathlib import Path
import psutil
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.streamlit_async import safe_async_call

# Load environment variables
load_dotenv()

def get_server_ports():
    """Get server ports from environment variables with fallbacks"""
    return {
        "RAG": int(os.getenv("RAG_MCP_PORT", "9002")),
        "Voice": int(os.getenv("VOICE_SERVER_PORT", "9006")),
        "SaltyBot": int(os.getenv("SALTYBOT_MCP_PORT", "9005")),
        "TP-Link": int(os.getenv("TPLINK_MCP_PORT", "9001")),
        "Spotify": int(os.getenv("SPOTIFY_MCP_PORT", "9003")),
        "Roku": int(os.getenv("ROKU_MCP_PORT", "9004")),
    }

def get_server_uptime(pid):
    """Get server uptime in human readable format"""
    try:
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            create_time = datetime.fromtimestamp(proc.create_time())
            uptime = datetime.now() - create_time
            
            if uptime.days > 0:
                return f"{uptime.days}d {uptime.seconds//3600}h"
            elif uptime.seconds > 3600:
                return f"{uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
            else:
                return f"{uptime.seconds//60}m"
        return "N/A"
    except:
        return "N/A"

def get_cpu_usage(pid):
    """Get CPU usage percentage"""
    try:
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            return f"{proc.cpu_percent():.1f}%"
        return "N/A"
    except:
        return "N/A"

def get_recent_logs(server_name, lines=3):
    """Get recent log entries for a server"""
    try:
        log_file = Path(f"logs/{server_name.lower().replace('-', '_')}_server.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines_list = f.readlines()
                if lines_list:
                    # Get last few lines, strip whitespace
                    recent = [line.strip() for line in lines_list[-lines:] if line.strip()]
                    return recent
        return []
    except:
        return []

def get_usage_metrics(pid):
    """Get current CPU and memory usage for a process"""
    try:
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            cpu_percent = proc.cpu_percent()
            memory_mb = proc.memory_info().rss / 1024 / 1024
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'timestamp': datetime.now().isoformat()
            }
        return None
    except:
        return None

def save_usage_data(server_name, metrics):
    """Save usage metrics to a JSON file"""
    try:
        data_dir = Path("data/usage_metrics")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = data_dir / f"{server_name.lower().replace('-', '_')}_usage.json"
        
        # Load existing data
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Add new metrics
        data.append(metrics)
        
        # Keep only last 100 data points to prevent file from growing too large
        if len(data) > 100:
            data = data[-100:]
        
        # Save data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving usage data: {e}")

def load_usage_data(server_name):
    """Load usage data for a server"""
    try:
        data_dir = Path("data/usage_metrics")
        file_path = data_dir / f"{server_name.lower().replace('-', '_')}_usage.json"
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        return []
    except:
        return []

def create_usage_chart(server_name, data):
    """Create a mini usage chart for a server"""
    if not data or len(data) < 2:
        return None
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add CPU line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cpu_percent'],
            name='CPU %',
            line=dict(color='#ff6b6b', width=2),
            yaxis='y'
        ))
        
        # Add Memory line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['memory_mb'],
            name='Memory MB',
            line=dict(color='#4ecdc4', width=2),
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{server_name} Usage",
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(
                title="CPU %",
                side="left",
                range=[0, max(df['cpu_percent'].max() * 1.1, 10)]
            ),
            yaxis2=dict(
                title="Memory MB",
                side="right",
                overlaying="y",
                range=[0, max(df['memory_mb'].max() * 1.1, 50)]
            ),
            xaxis=dict(
                title="",
                showgrid=True,
                gridcolor='lightgray'
            )
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None

def show_mcp_manager():
    """
    Displays the MCP Tool Manager page.
    """
    set_page_config()
    show_page_header("🛠️ MCP Manager", "Manage and discover MCP tools")

    tab1, tab2 = st.tabs(["🖥️ Servers", "🔧 Tools"])

    with tab1:
        st.subheader("MCP Server Management")
        st.markdown("*🦜 Manage all MCP servers for The Gold Monkey*")
        
        # Create .pids directory if it doesn't exist
        pids_dir = Path(".pids")
        pids_dir.mkdir(exist_ok=True)
        
        # Server control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start All Servers", key="start_all", help="Start all MCP servers"):
                try:
                    result = subprocess.run(
                        ["python", "utils/start_servers.py", "all"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        st.success("✅ All servers started successfully!")
                    else:
                        st.error(f"❌ Error starting servers: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("⏰ Timeout while starting servers")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                time.sleep(2)
                st.rerun()
        
        with col2:
            if st.button("🛑 Stop All Servers", key="stop_all", help="Stop all MCP servers"):
                try:
                    result = subprocess.run(
                        ["python", "utils/stop_servers.py", "all"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        st.success("✅ All servers stopped successfully!")
                    else:
                        st.error(f"❌ Error stopping servers: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("⏰ Timeout while stopping servers")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                time.sleep(2)
                st.rerun()
        
        with col3:
            if st.button("🔄 Restart All Servers", key="restart_all", help="Restart all MCP servers"):
                try:
                    # Stop all servers first
                    subprocess.run(["python", "utils/stop_servers.py", "all"], timeout=10)
                    time.sleep(2)
                    # Start all servers
                    result = subprocess.run(
                        ["python", "utils/start_servers.py", "all"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        st.success("✅ All servers restarted successfully!")
                    else:
                        st.error(f"❌ Error restarting servers: {result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("⏰ Timeout while restarting servers")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                time.sleep(2)
                st.rerun()
        
        # Refresh status button
        if st.button("🔄 Refresh Status", key="refresh_status"):
            st.rerun()

        st.markdown("---")

        # Display server status
        st.subheader("📊 Server Status")
        
        try:
            server_status = check_server_status()
            
            if not server_status:
                st.warning("⚠️ No server status information available")
            else:
                # Create a more detailed status display
                for server_name, status_info in server_status.items():
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                        
                        with col1:
                            # Determine status icon and color
                            if "🟢" in status_info.get('status', ''):
                                status_icon = "🟢"
                                status_color = "success"
                            elif "🟡" in status_info.get('status', ''):
                                status_icon = "🟡"
                                status_color = "warning"
                            else:
                                status_icon = "🔴"
                                status_color = "error"
                            
                            st.markdown(f"**{server_name}** {status_icon}")
                            st.caption(f"Status: {status_info.get('status', 'Unknown')}")
                        
                        with col2:
                            if st.button(f"Start", key=f"start_{server_name}", help=f"Start {server_name} server"):
                                try:
                                    result = subprocess.run(
                                        ["python", "utils/start_servers.py", server_name],
                                        capture_output=True,
                                        text=True,
                                        timeout=15
                                    )
                                    if result.returncode == 0:
                                        st.success(f"✅ {server_name} started!")
                                    else:
                                        st.error(f"❌ Error: {result.stderr}")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                time.sleep(1)
                                st.rerun()
                        
                        with col3:
                            if st.button(f"Stop", key=f"stop_{server_name}", help=f"Stop {server_name} server"):
                                try:
                                    result = subprocess.run(
                                        ["python", "utils/stop_servers.py", server_name],
                                        capture_output=True,
                                        text=True,
                                        timeout=15
                                    )
                                    if result.returncode == 0:
                                        st.success(f"✅ {server_name} stopped!")
                                    else:
                                        st.error(f"❌ Error: {result.stderr}")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                time.sleep(1)
                                st.rerun()
                        
                        with col4:
                            # Show PID, Port, and Memory if available
                            pid_file = Path(f".pids/{server_name}.pid")
                            server_ports = get_server_ports()
                            port = server_ports.get(server_name, "Unknown")
                            if pid_file.exists():
                                try:
                                    pid = int(pid_file.read_text().strip())
                                    st.caption(f"PID: {pid}")
                                    st.caption(f"Port: {port}")
                                    
                                    # Track usage metrics if process exists
                                    if psutil.pid_exists(pid):
                                        try:
                                            proc = psutil.Process(pid)
                                            mem_mb = proc.memory_info().rss / 1024 / 1024
                                            st.caption(f"Memory: {mem_mb:.1f} MB")
                                            
                                            # Save current usage metrics
                                            metrics = get_usage_metrics(pid)
                                            if metrics:
                                                save_usage_data(server_name, metrics)
                                        except Exception:
                                            st.caption("Memory: N/A")
                                    else:
                                        st.caption("Memory: N/A")
                                except:
                                    st.caption("PID: Unknown")
                                    st.caption(f"Port: {port}")
                                    st.caption("Memory: N/A")
                            else:
                                st.caption("PID: None")
                                st.caption(f"Port: {port}")
                                st.caption("Memory: N/A")
                        
                        with col5:
                            # Show additional metrics
                            pid_file = Path(f".pids/{server_name}.pid")
                            server_ports = get_server_ports()
                            port = server_ports.get(server_name, "Unknown")
                            if pid_file.exists():
                                try:
                                    pid = int(pid_file.read_text().strip())
                                    if psutil.pid_exists(pid):
                                        # CPU Usage
                                        cpu_usage = get_cpu_usage(pid)
                                        st.caption(f"CPU: {cpu_usage}")
                                        
                                        # Uptime
                                        uptime = get_server_uptime(pid)
                                        st.caption(f"Uptime: {uptime}")
                                    else:
                                        st.caption("CPU: N/A")
                                        st.caption("Uptime: N/A")
                                except:
                                    st.caption("CPU: N/A")
                                    st.caption("Uptime: N/A")
                        
                        # Show usage chart if server is running
                        pid_file = Path(f".pids/{server_name}.pid")
                        if pid_file.exists():
                            try:
                                pid = int(pid_file.read_text().strip())
                                if psutil.pid_exists(pid):
                                    # Load usage data and create chart
                                    usage_data = load_usage_data(server_name)
                                    if usage_data and len(usage_data) > 1:
                                        chart = create_usage_chart(server_name, usage_data)
                                        if chart:
                                            with st.expander(f"📈 Usage Chart - {server_name}", expanded=False):
                                                st.plotly_chart(chart, use_container_width=True)
                            except:
                                pass
                        
                        # Show recent logs in an expander
                        recent_logs = get_recent_logs(server_name)
                        if recent_logs:
                            with st.expander(f"📋 Recent Logs - {server_name}", expanded=False):
                                for log_line in recent_logs:
                                    st.text(log_line)
                        
                        st.markdown("---")
        
        except Exception as e:
            st.error(f"❌ Error checking server status: {str(e)}")
        
        # System Overview
        st.markdown("---")
        st.subheader("📊 System Overview")
        
        try:
            # Calculate total system usage
            total_cpu = 0
            total_memory = 0
            running_servers = 0
            
            for server_name, status_info in server_status.items():
                pid_file = Path(f".pids/{server_name}.pid")
                if pid_file.exists():
                    try:
                        pid = int(pid_file.read_text().strip())
                        if psutil.pid_exists(pid):
                            proc = psutil.Process(pid)
                            total_cpu += proc.cpu_percent()
                            total_memory += proc.memory_info().rss / 1024 / 1024
                            running_servers += 1
                    except:
                        pass
            
            # Display system overview metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Running Servers", running_servers)
            
            with col2:
                st.metric("Total CPU Usage", f"{total_cpu:.1f}%")
            
            with col3:
                st.metric("Total Memory Usage", f"{total_memory:.1f} MB")
            
            # Show system-wide chart if we have data (full width)
            all_usage_data = []
            for server_name in server_status.keys():
                usage_data = load_usage_data(server_name)
                if usage_data:
                    all_usage_data.extend(usage_data)
            
            if all_usage_data and len(all_usage_data) > 5:
                try:
                    df = pd.DataFrame(all_usage_data)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['timestamp'],
                        y=df['cpu_percent'],
                        name='Total CPU %',
                        line=dict(color='#ff6b6b', width=3)
                    ))
                    fig.add_trace(go.Scatter(
                        x=df['timestamp'],
                        y=df['memory_mb'],
                        name='Total Memory MB',
                        line=dict(color='#4ecdc4', width=3),
                        yaxis='y2'
                    ))
                    
                    fig.update_layout(
                        title="System Usage Overview",
                        height=600,
                        yaxis=dict(title="CPU %", titlefont=dict(size=14)),
                        yaxis2=dict(title="Memory MB", overlaying="y", side="right", titlefont=dict(size=14)),
                        xaxis=dict(title="Time", titlefont=dict(size=14)),
                        showlegend=True,
                        legend=dict(font=dict(size=12)),
                        margin=dict(l=60, r=60, t=100, b=60),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("📈 Usage charts will appear as data accumulates")
            else:
                st.info("📈 Usage charts will appear as data accumulates")
        
        except Exception as e:
            st.error(f"❌ Error calculating system overview: {str(e)}")

    with tab2:
        st.subheader("🔧 Discovered Tools")
        st.markdown("*🦜 Tools available from all MCP servers*")
        
        # Add refresh button for tools
        if st.button("🔄 Refresh Tools", key="refresh_tools"):
            st.rerun()
        
        try:
            # Create tool registry and discover tools
            tool_registry = ToolRegistry()
            
            # Use safe async call instead of asyncio.run()
            async def discover_all_tools():
                await tool_registry.discover_tools()
                return tool_registry.get_tools()
            
            # Run the async function safely
            tools = safe_async_call(discover_all_tools)
            
            if not tools:
                st.warning("⚠️ No tools discovered. Make sure MCP servers are running.")
                st.info("💡 Start the servers using the 'Servers' tab to discover tools.")
            else:
                st.success(f"✅ Discovered {len(tools)} tools")
                
                # Display tools by category
                tool_categories = {}
                for tool_name in tools.keys():
                    if "." in tool_name:
                        category = tool_name.split(".")[0]
                    else:
                        category = "Other"
                    
                    if category not in tool_categories:
                        tool_categories[category] = []
                    tool_categories[category].append(tool_name)
                
                for category, tool_list in tool_categories.items():
                    with st.expander(f"📦 {category.title()} ({len(tool_list)} tools)", expanded=True):
                        for tool_name in sorted(tool_list):
                            st.code(tool_name)
        except Exception as e:
            st.error(f"Error discovering tools: {e}")

if __name__ == "__main__":
    show_mcp_manager()
