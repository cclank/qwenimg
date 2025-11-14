# Contributing to QwenImg

Thank you for your interest in contributing to QwenImg! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/qwenimg.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Linux/macOS: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
5. Install dependencies: `pip install -e ".[dev]"`

## Development Setup

1. Create a `.env` file with your API key:
   ```
   DASHSCOPE_API_KEY=sk-your-key-here
   ```

2. Run tests (when available):
   ```bash
   pytest
   ```

3. Format code with Black:
   ```bash
   black qwenimg/ examples/
   ```

4. Check code style:
   ```bash
   flake8 qwenimg/
   ```

## Guidelines

### Code Style

- Follow PEP 8
- Use Black for formatting
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issues when applicable

### Pull Requests

1. Create a new branch for your feature: `git checkout -b feature-name`
2. Make your changes
3. Test your changes
4. Commit your changes: `git commit -m "Add feature X"`
5. Push to your fork: `git push origin feature-name`
6. Create a Pull Request

### Adding Examples

- Add example scripts to the `examples/` directory
- Include comments explaining what the code does
- Make sure examples are self-contained and runnable

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions and classes
- Update CHANGELOG.md

## Questions?

Feel free to open an issue for any questions or suggestions!
