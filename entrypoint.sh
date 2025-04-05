#!/bin/bash
# Start the Ollama server in the background
ollama serve &

# Wait for a few seconds to let the server initialize
sleep 5

# Pull the "mistral" model (if not already present)
ollama pull mistral

# Wait indefinitely so the container doesn’t exit
wait
