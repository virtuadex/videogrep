.PHONY: dev gui install clean

# Default target
dev: gui

# Run the Desktop GUI in development mode
gui:
	cd desktop && npm run tauri dev

# Install GUI dependencies
install-gui:
	cd desktop && npm install

# Install Python dependencies
install-python:
	poetry install

# Run the full setup
install: install-python install-gui

# Run Videogrep CLI
search:
	poetry run videogrep

# Clean build artifacts
clean:
	rm -rf desktop/src-tauri/target
