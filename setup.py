from setuptools import setup, find_packages

setup(
    name="mcp-server-ticktick",
    version="0.2.2",
    description="Model Context Protocol (MCP) server for TickTick task management",
    author="broven",
    author_email="",
    url="https://github.com/broven/mcp-server-ticktick",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.2.0,<2.0.0",
        "requests>=2.30.0,<3.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ticktick-mcp=ticktick_mcp.cli:main",
            "mcp-server-ticktick=ticktick_mcp.cli:main",
            "ticktick-auth=ticktick_mcp.authenticate:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)