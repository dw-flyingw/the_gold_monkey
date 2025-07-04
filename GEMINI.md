# Project Overview

This Python project utilizes the Model Context Protocol (MCP) and `mcp[cli]` to [briefly describe the project's purpose and how MCP is used, e.g., interact with MCP servers, manage context for LLMs, provide CLI tools through MCP].

# Project Goals

- [List the main goals of your project, e.g., Integrate with specific MCP servers like GitHub or Sentry, Provide a command-line interface for interacting with data via MCP, Facilitate testing and development of MCP servers].
- [Specify any specific functionalities you want Gemini to help with, particularly those involving MCP tools or resources].

# Model Context Protocol (MCP) Integration

-   **MCP Servers:** This project interacts with [mention the specific MCP servers you plan to use or integrate with, e.g., the GitHub MCP server, a custom-built MCP server].
-   **`mcp[cli]` Usage:** We use `mcp[cli]` for [describe how you use the MCP CLI, e.g., testing MCP servers, exploring available tools, managing MCP configurations].
-   **Key MCP Concepts:** This project utilizes key MCP concepts like [mention concepts relevant to your project, e.g., Tools, Resources, Prompts].

# Code Style and Conventions

-   [Describe your preferred coding style, e.g., PEP 8, specific formatting rules].
-   [Mention any specific documentation practices, e.g., use docstrings in reStructuredText format].
-   [Specify any naming conventions for variables, functions, etc., especially those related to MCP tool or resource naming].

# Architecture and Design

-   [Briefly describe the project's architecture, especially how it leverages MCP, e.g., client-server interactions with MCP servers, how data is accessed via MCP Resources].
-   [Explain any key design patterns used, particularly those related to MCP integration].

# Dependencies:

-   This project uses `uv` instead of `pip` for dependency management.
-   [List major project dependencies, including `mcp` and other relevant libraries, and their purpose].

# Security Considerations

-   [Mention any security concerns or best practices relevant to your project, especially concerning the use of MCP servers and accessing data through them].

# Tips for Interacting with Gemini

-   **Leverage MCP Tools:** Ask Gemini to utilize available MCP tools for specific tasks, e.g., `Use the GitHub MCP tool to list recent commits`.
-   **Explore MCP Resources:** If your project exposes data via MCP Resources, you can ask Gemini to analyze them, e.g., `Read the content of the 'README.md' MCP resource`.
-   **Provide MCP Context:** When asking Gemini questions, provide context by referencing relevant MCP tools, resources, or configuration details, e.g., `@github_mcp_server.py`.
-   **Break down complex tasks:** For complex tasks, break them down into smaller, more manageable steps, especially if they involve multiple MCP interactions.
-   **Use the `@` symbol:** Reference specific files in your project using the `@` symbol, e.g., `@my_mcp_client.py`.
-   **Be careful when modifying `.env` files:** Do not remove needed information when adding new environment variables.
-   **NEVER overwrite the `.env` file:** Always append to it or ask the user for permission before overwriting.

# Example Scenarios (Optional)

-   [Provide examples of how you might use Gemini to assist with tasks in this project].
    -   Example 1: `Help me create a new MCP server for accessing a database.`
    -   Example 2: `Debug the issue in @my_mcp_client.py when connecting to the Sentry MCP server.`
    -   Example 3: `Generate a new test case for the 'process_data' function in @data_handler.py, ensuring it uses the configured MCP resource.`
    -   Example 4: `Explain the purpose of the '/mcp__github__list_issues' prompt.`

