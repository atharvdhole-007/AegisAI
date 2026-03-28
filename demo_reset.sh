#!/bin/bash
# CyberSentinel AI — Clean Demo Reset Script
# Use this during a live presentation to instantly reset all states.

echo "Resetting AegisAI Backend State..."
curl -X POST http://localhost:8000/api/reset
echo -e "\nDemo Reset Complete! Playbooks, Simulations, and Logs deleted."
