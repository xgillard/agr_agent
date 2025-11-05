:

# Bump all dependencies of the project.

# on va utiliser python3.10
uv python install cpython-3.10.18-linux-x86_64-gnu

# Utilities
uv add \
	uv add \
	setuptools \
	wheel \
	python-dotenv \
	scikit-learn \
	pyarrow \
	html5lib \
	textdistance \
	streamlit

# Torch
uv add \
	torch

# HF
uv add \
	accelerate \
	transformers \
	sentence-transformers

# Langchain
uv add \
	langchain\
	langchain-core \
	langchain-docling \
	langchain-text-splitters \
	langchain-chroma \
	langchain-huggingface \
	langchain-ollama \
	langchain-mistralai \
	langchain-google-genai \
	langchain-openai 

# Langgraph
uv add \
	langgraph \
	agentevals


# Dev dependencies
uv add --dev \
	mypy \
	ruff \
	types-requests \
	behave \
	pytest \
	python-lsp-server \
	jupyter-lsp \
	matplotlib \
	umap-learn

