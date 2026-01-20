# VoxGrep Installation Guide

This comprehensive guide covers all installation methods for VoxGrep, ensuring a standardized Python environment across different platforms and use cases.

## 📋 Prerequisites

Before installing VoxGrep, ensure you have:

- **Python 3.10 or later** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** - Required for video processing
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: [FFmpeg Downloads](https://ffmpeg.org/download.html)
- **Git** - For source installation
- **Node.js 18+** (Optional) - Only required for desktop app

## 🎯 Recommended Installation Methods

### Method 1: Poetry (Recommended for Development)

Poetry provides the most reliable and reproducible environment management.

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/virtuadex/voxgrep.git
cd voxgrep

# Install all dependencies (including optional AI features)
poetry install --extras "full"

# Activate the virtual environment
poetry shell

# Verify installation
voxgrep --doctor
```

**Benefits:**

- Automatic virtual environment creation
- Locked dependency versions for reproducibility
- Easy management of optional dependencies
- Isolated from system Python

### Method 2: pip with Virtual Environment (Recommended for Users)

Use pip within a virtual environment for a clean, isolated installation.

```bash
# Create a virtual environment
python3 -m venv voxgrep-env

# Activate the virtual environment
# On macOS/Linux:
source voxgrep-env/bin/activate
# On Windows:
voxgrep-env\Scripts\activate

# Install VoxGrep with all features
pip install "voxgrep[full]"

# Verify installation
voxgrep --doctor
```

**Benefits:**

- Simple and straightforward
- No additional tools required
- Works on all platforms
- Isolated from system Python

### Method 3: pip (Basic Installation)

For a minimal installation without optional AI features:

```bash
# Install core VoxGrep
pip install voxgrep

# Or install from source
git clone https://github.com/virtuadex/voxgrep.git
cd voxgrep
pip install .
```

**Note:** Basic installation excludes semantic search and advanced transcription features.

### Method 4: Conda (For Conda Users)

If you prefer Conda for environment management:

```bash
# Create a new conda environment
conda create -n voxgrep python=3.10

# Activate the environment
conda activate voxgrep

# Install VoxGrep
pip install "voxgrep[full]"

# Verify installation
voxgrep --doctor
```

## 🔧 Installation Extras

VoxGrep provides several optional feature sets you can install:

| Extra         | Description                     | Install Command                      |
| ------------- | ------------------------------- | ------------------------------------ |
| `full`        | All features (recommended)      | `pip install "voxgrep[full]"`        |
| `mlx`         | Apple Silicon GPU transcription | `pip install "voxgrep[mlx]"`         |
| `nlp`         | Advanced NLP features (spaCy)   | `pip install "voxgrep[nlp]"`         |
| `diarization` | Speaker diarization (pyannote)  | `pip install "voxgrep[diarization]"` |
| `openai`      | OpenAI API integration          | `pip install "voxgrep[openai]"`      |

**Combine multiple extras:**

```bash
pip install "voxgrep[mlx,nlp,diarization]"
```

## 🖥️ Desktop Application Setup

The desktop app requires Node.js and additional setup:

```bash
# Navigate to the desktop directory
cd desktop

# Install Node dependencies
npm install

# Run in development mode
npm run tauri dev

# Or build for production
npm run tauri build
```

## 🩺 Verifying Your Installation

After installation, run the environment doctor to verify everything is working:

```bash
voxgrep --doctor
```

This will check:

- ✓ Python version compatibility
- ✓ All required dependencies
- ✓ Optional AI features
- ✓ System commands (FFmpeg, MPV)
- ✓ Data directory access

**Example output:**

```
🔍 VoxGrep Environment Doctor

Environment Information
┌─────────────────────┬──────────────────────────────────┐
│ Check               │ Status                           │
├─────────────────────┼──────────────────────────────────┤
│ Python Version      │ ✓ Python 3.10.0                  │
│ Environment         │ Poetry                           │
│ Installation Method │ Source (Development)             │
│ Data Directory      │ ✓ ~/.local/share/voxgrep         │
└─────────────────────┴──────────────────────────────────┘

✓ All checks passed!
```

## 🚀 Quick Start After Installation

### CLI Usage

```bash
# Run interactive mode (recommended for first-time users)
voxgrep

# Or use command-line arguments
voxgrep -i video.mp4 -s "hello world" -tr
```

### Server + Desktop App

```bash
# Terminal 1: Start the backend server
python -m voxgrep.server.app

# Terminal 2: Start the desktop app
cd desktop && npm run tauri dev
```

## 🔄 Upgrading VoxGrep

### With Poetry

```bash
cd voxgrep
git pull
poetry install --extras "full"
```

### With pip

```bash
pip install --upgrade "voxgrep[full]"
```

### With pip from source

```bash
cd voxgrep
git pull
pip install --upgrade .
```

## 🐛 Troubleshooting

### Python Version Issues

**Problem:** "Python 3.10 or later required"

**Solution:**

```bash
# Check your Python version
python3 --version

# If too old, install newer Python:
# macOS (using Homebrew):
brew install python@3.11

# Ubuntu:
sudo apt install python3.11

# Or download from python.org
```

### FFmpeg Not Found

**Problem:** "FFmpeg not found" error

**Solution:**

```bash
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

### Missing Dependencies

**Problem:** Import errors or missing packages

**Solution:**

```bash
# Reinstall with all features
pip install --force-reinstall "voxgrep[full]"

# Or with Poetry
poetry install --extras "full"

# Verify installation
voxgrep --doctor
```

### Permission Errors

**Problem:** "Permission denied" when creating data directory

**Solution:**

```bash
# Create the directory manually
mkdir -p ~/.local/share/voxgrep

# Set permissions
chmod 755 ~/.local/share/voxgrep
```

### Apple Silicon (M1/M2) MLX Issues

**Problem:** MLX transcription not working on Mac

**Solution:**

```bash
# Ensure you have the MLX extra installed
pip install "voxgrep[mlx]"

# Or with Poetry
poetry install --extras "mlx"

# Verify MLX is available
python -c "import mlx_whisper; print('MLX OK')"
```

## 📊 Comparing Installation Methods

| Method           | Pros                                       | Cons                              | Best For                  |
| ---------------- | ------------------------------------------ | --------------------------------- | ------------------------- |
| **Poetry**       | Reproducible, automatic venv, dev-friendly | Requires Poetry                   | Development, Contributing |
| **pip + venv**   | Simple, standard, portable                 | Manual venv management            | General users             |
| **pip (global)** | Quick, no venv overhead                    | Can conflict with system packages | Testing only              |
| **Conda**        | Familiar to data scientists                | Larger environment size           | Conda users               |

## 🎓 Environment Best Practices

1. **Always use a virtual environment** - Avoid installing directly to system Python
2. **Install the `full` extra** - Get all features unless you have space constraints
3. **Run `voxgrep --doctor`** - Verify your installation after setup
4. **Keep dependencies updated** - Run upgrade commands periodically
5. **Use Poetry for development** - Ensures everyone has the same environment

## 📚 Next Steps

Once installed, check out these guides:

- 📖 [User Guide](USER_GUIDE.md) - Learn how to use VoxGrep
- 🛠️ [CLI Reference](CLI_REFERENCE.md) - All command-line options
- 🏗️ [Architecture](ARCHITECTURE.md) - How VoxGrep works
- 🐍 [API Reference](API_REFERENCE.md) - Use VoxGrep as a library

## 💬 Getting Help

If you encounter issues:

1. Run `voxgrep --doctor` to diagnose problems
2. Check [GitHub Issues](https://github.com/virtuadex/voxgrep/issues)
3. Review the [User Guide](USER_GUIDE.md) troubleshooting section
4. Ask for help on [GitHub Discussions](https://github.com/virtuadex/voxgrep/discussions)

---

**Remember:** The `--doctor` command is your friend! Run it anytime you suspect environment issues.
