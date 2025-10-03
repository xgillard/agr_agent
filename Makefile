run:
	uv run streamlit run arkey_demo.py

quick: 
	uv run ruff check .
	uv run mypy .

check: quick
	echo "pytest"
	uv run pytest 
