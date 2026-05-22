PLUGINNAME = pluginbuilder4

.PHONY: deploy dclean clean doc test lint

# Deploy for local development using pb_tool
deploy:
	cd $(PLUGINNAME) && pb_tool deploy

# Remove the deployed plugin
dclean:
	cd $(PLUGINNAME) && pb_tool dclean

# Remove compiled Python files and build artifacts
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -f $(PLUGINNAME).zip

# Build Sphinx documentation
doc:
	cd help && make html

# Run the test suite
test:
	pytest

# Lint with ruff
lint:
	ruff check .
