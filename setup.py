#!/usr/bin/env python3
"""
MCP Hub - Simple Setup
"""

from setuptools import setup, find_packages

setup(
    name="mcp-hub",
    version="1.0.0",
    description="A simple MCP tool integration platform with multi-LLM support",
    author="MCP Hub Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "streamlit",
        "openai",
        "anthropic",
        "google-generativeai",
        "sqlite3",
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "mcp-hub=app:main",
        ],
    },
)
