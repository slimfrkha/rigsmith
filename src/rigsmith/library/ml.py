"""Machine learning and LLM tooling."""

from rigsmith.backends import UvTool
from rigsmith.library._util import tool

tool("jupyterlab", "JupyterLab, installed as an isolated uv tool.", sources=[UvTool("jupyterlab")], bin="jupyter-lab")
tool("marimo", "Reactive Python notebooks stored as plain .py files.", sources=[UvTool("marimo")])
tool(
    "huggingface-cli",
    "Hugging Face Hub CLI: log in, download and upload models and datasets (`hf download …`).",
    sources=[UvTool("huggingface_hub[cli]")],
    bin="hf",
)
tool("llm", "Simon Willison's llm: talk to LLMs from the terminal, log everything to SQLite.", sources=[UvTool("llm")])
tool(
    "nvitop",
    "Interactive NVIDIA GPU monitor: utilization, memory and processes per GPU (Linux).",
    sources=[UvTool("nvitop", os="linux")],
    tags=["tui"],
)
tool("ollama", "Run open LLMs locally: `ollama run llama3.2`.")
