# Memory System Setup Guide

This guide explains how to set up the memory knowledge graph system for a new project.

## Step 1: Create the wrapper script

Create a file named `run_memory_server.sh` in your project root with the following content:

```bash
#!/bin/bash

# Get the absolute path of the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the environment variable to point to the knowledge_graph.json in the current project
export MEMORY_FILE_PATH="$SCRIPT_DIR/knowledge_graph.json"

# Print the environment variable for debugging
echo "MEMORY_FILE_PATH set to: $MEMORY_FILE_PATH"

# Don't start the server, let Cursor handle that
# Just keep the script running so the environment variable persists
exec "$@"
```

Make the script executable:

```bash
chmod +x run_memory_server.sh
```

## Step 2: Create the knowledge graph file

Create a file named `knowledge_graph.json` in your project root. You can start with an empty knowledge graph:

```json
{
  "entities": [],
  "relations": []
}
```

## Step 3: Configure Cursor MCP

Create a `.cursor` directory in your project root if it doesn't exist already:

```bash
mkdir -p .cursor
```

Create a file named `mcp.json` in the `.cursor` directory with the following content:

```json
{
  "mcpServers": {
    "memory": {
      "command": "/bin/bash",
      "args": [
        "/path/to/your/project/run_memory_server.sh",
        "node",
        "/path/to/global/memory/server/index.js"
      ],
      "env": {}
    }
  }
}
```

Replace:
- `/path/to/your/project` with the absolute path to your project
- `/path/to/global/memory/server/index.js` with the path to your global memory server installation

## Step 4: Test the setup

Restart Cursor and try to use the memory knowledge graph in your project. You can test it by running a command that interacts with the knowledge graph.

## Notes

- Each project will have its own isolated knowledge graph stored in its `knowledge_graph.json` file
- The global memory server is reused across all projects
- The environment variable `MEMORY_FILE_PATH` is set dynamically by the wrapper script to point to the project-specific knowledge graph file
- The wrapper script uses `exec "$@"` to run the server command that's passed to it, while preserving the environment variables 