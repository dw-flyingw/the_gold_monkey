# MCP Server Analytics Integration

## Overview

The Analytics Dashboard has been enhanced with comprehensive MCP (Model Context Protocol) server analytics, providing real-time monitoring and insights into all MCP servers in The Gold Monkey system.

## Features Added

### 🤖 MCP Server Analytics Tab

The Analytics Dashboard now includes a dedicated "MCP Server Analytics" tab with the following features:

#### 🖥️ Server Status & Health
- **Real-time Status Monitoring**: Shows current status of all MCP servers (Online/Idle/Offline)
- **Health Indicators**: Visual indicators for server health status
- **Status Metrics**: Displays server status with health delta indicators

#### 📊 Key Performance Indicators
- **Total Tool Calls**: Count of all tool calls across all servers
- **Total Errors**: Aggregate error count with daily tracking
- **Most Active Server**: Identifies the server with highest activity
- **Most Used Tool**: Shows the most frequently used tool across all servers

#### 📈 Recent Activity Analysis
- **24-Hour Activity Chart**: Bar chart showing server activity in the last 24 hours
- **Activity Level Classification**: Categorizes activity as High/Medium/Low
- **Activity Breakdown Table**: Detailed breakdown of server activity

#### 🔧 Tool Usage Analysis
- **Tool Usage Trends**: Line chart showing tool usage over time
- **Usage Breakdown**: Percentage-based breakdown of tool usage
- **Server-Specific Usage**: Shows which servers are using which tools
- **Usage Statistics**: Detailed statistics for each tool

#### ⚠️ Error Analysis & Trends
- **Error Trend Charts**: Visual representation of error patterns over time
- **Error Severity Analysis**: Breakdown of errors by severity level
- **Recent Error Display**: Formatted display of recent errors with timestamps
- **Error Categorization**: Groups errors by server and severity

#### ⚡ Server Performance Metrics
- **Performance Dashboard**: Comprehensive performance metrics for each server
- **Health Scores**: Calculated health scores based on error rates
- **Uptime Tracking**: Server uptime calculations
- **Performance Comparison**: Visual comparison of server performance

#### 🔍 Detailed Server Information
- **Expandable Server Details**: Detailed information for each server
- **Daily Statistics**: Daily breakdown of server activity
- **Daily Trends**: Visual trends for server activity over time
- **Comprehensive Metrics**: Total entries, errors, warnings, and rates

#### 💡 System Recommendations
- **Automated Recommendations**: AI-powered system recommendations
- **Error Management Suggestions**: Recommendations for error handling
- **Server Optimization Tips**: Suggestions for resource optimization
- **Recovery Recommendations**: Guidance for offline server recovery

### 🔄 Real-Time Features

#### Auto-Refresh Capability
- **Auto-refresh Toggle**: Option to automatically refresh data every 30 seconds
- **Manual Refresh Button**: Manual refresh capability
- **Last Updated Timestamp**: Shows when data was last refreshed

#### Live Data Integration
- **Real-time Log Parsing**: Continuously parses MCP server log files
- **Live Status Updates**: Real-time server status monitoring
- **Dynamic Metrics**: Metrics that update based on current log data

## Technical Implementation

### MCP Analytics Module (`utils/mcp_analytics.py`)

The analytics functionality is powered by a comprehensive MCP analytics module that includes:

#### Log Parsing
- **Multi-format Support**: Parses various log formats
- **Timestamp Extraction**: Extracts and normalizes timestamps
- **Level Classification**: Categorizes log entries by severity

#### Data Analysis
- **Tool Call Extraction**: Identifies and tracks tool calls
- **Error Analysis**: Analyzes error patterns and trends
- **Performance Metrics**: Calculates server performance indicators

#### Server Monitoring
- **Status Detection**: Determines server online/offline status
- **Activity Tracking**: Monitors server activity levels
- **Health Scoring**: Calculates server health scores

### Supported MCP Servers

The analytics system monitors the following MCP servers:

1. **TPLink Server** (`tplink_server.log`)
   - Smart lighting control
   - Device management
   - Power monitoring

2. **Spotify Server** (`spotify_server.log`)
   - Music playback control
   - Playlist management
   - Audio streaming

3. **Roku Server** (`roku_server.log`)
   - Media device control
   - App management
   - Content streaming

4. **RAG Server** (`rag_server.log`)
   - Knowledge base queries
   - Document retrieval
   - Semantic search

5. **Voice Server** (`voice_server.log`)
   - Text-to-speech
   - Voice synthesis
   - Audio processing

6. **Saltybot Server** (`saltybot_server.log`)
   - Chat functionality
   - Conversation management
   - AI interactions

## Usage

### Accessing MCP Analytics

1. Navigate to the **Analytics Dashboard** in the main application
2. Click on the **"🤖 MCP Server Analytics"** tab
3. View real-time server status and performance metrics

### Interpreting the Data

#### Server Status Colors
- 🟢 **Green**: Server is online and active
- 🟡 **Yellow**: Server is idle (no recent activity)
- 🔴 **Red**: Server is offline or not responding

#### Health Scores
- **100%**: Perfect health (no errors)
- **80-99%**: Good health (minimal errors)
- **60-79%**: Fair health (some errors)
- **Below 60%**: Poor health (many errors)

#### Activity Levels
- **High**: More than 10 activities in 24 hours
- **Medium**: 5-10 activities in 24 hours
- **Low**: Less than 5 activities in 24 hours

## Benefits

### For System Administrators
- **Proactive Monitoring**: Identify issues before they become problems
- **Performance Optimization**: Optimize server resources based on usage patterns
- **Error Tracking**: Track and resolve errors systematically
- **Capacity Planning**: Plan for future capacity needs

### For Developers
- **Debugging Support**: Identify problematic servers and tools
- **Performance Analysis**: Analyze server performance patterns
- **Usage Insights**: Understand how tools are being used
- **Optimization Opportunities**: Identify areas for improvement

### For Users
- **System Transparency**: Understand system health and status
- **Reliability Assurance**: Know when systems are working properly
- **Issue Awareness**: Be informed about any system issues

## Future Enhancements

### Planned Features
- **Alert System**: Automated alerts for critical issues
- **Historical Analysis**: Long-term trend analysis
- **Predictive Analytics**: Predict potential issues before they occur
- **Custom Dashboards**: User-configurable dashboard layouts
- **Export Capabilities**: Export analytics data for external analysis

### Integration Opportunities
- **Notification System**: Integration with notification services
- **External Monitoring**: Integration with external monitoring tools
- **API Access**: REST API for external analytics access
- **Mobile Dashboard**: Mobile-optimized analytics view

## Troubleshooting

### Common Issues

#### No Data Available
- **Check Log Files**: Ensure MCP server log files exist in the `logs/` directory
- **Server Status**: Verify that MCP servers are running and generating logs
- **File Permissions**: Check that log files are readable

#### Missing Servers
- **Server Configuration**: Verify that all expected servers are configured
- **Log File Names**: Ensure log file names match expected patterns
- **Server Status**: Check if servers are actually running

#### Performance Issues
- **Log File Size**: Large log files may cause performance issues
- **Refresh Rate**: Reduce auto-refresh frequency if needed
- **Data Filtering**: Consider implementing data filtering for large datasets

## Conclusion

The MCP Server Analytics integration provides comprehensive monitoring and insights into the MCP server ecosystem of The Gold Monkey. This enhancement enables better system management, performance optimization, and proactive issue resolution, ultimately improving the overall user experience and system reliability. 