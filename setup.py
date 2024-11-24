from setuptools import setup, find_packages

setup(
    name="llm_tests",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "openai>=1.40.0",
        "anthropic>=0.7.0",
        "pyautogen>=0.2.0", 
        "google-generativeai",
        "autogen-agentchat[gemini]~=0.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    python_requires=">=3.9",
)