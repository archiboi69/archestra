#!/bin/bash

# Set the environment variable to point to the knowledge_graph.json with absolute path
export MEMORY_FILE_PATH="/Users/michaldeja/Documents/GitHub/archestra/knowledge_graph.json"

# Run the memory server
npx -y @modelcontextprotocol/server-memory