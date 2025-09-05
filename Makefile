check:
	echo "ruff checks"
	uv run ruff check .
	echo "mypy checks"
	uv run mypy .
	echo "pytest"
	uv run pytest 
