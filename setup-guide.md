# Setup Guide for RoboMarty

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Marty robot connected via USB
- [ ] Webcam connected
- [ ] Microphone working
- [ ] OpenAI API key obtained
- [ ] ElevenLabs API key obtained
- [ ] All dependencies installed
- [ ] Workflow diagram added to docs folder

## Detailed Setup Instructions

### 1. Repository Setup

```bash
# Create the repository structure
mkdir robomarty
cd robomarty

# Create docs folder for images
mkdir docs

# Copy your workflow diagram to docs/workflow.png
# (Save the workflow image you showed me as docs/workflow.png)
```

### 2. Add the Workflow Diagram

Save your system workflow diagram as `docs/workflow.png`. This diagram shows:
- Main Coordinator
- Three parallel components (Watching, Talking, Moving)
- Shared Information layer
- Marty the Robot output

### 3. Environment Setup

Create `.env` file:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

⚠️ **Never commit the `.env` file to Git!**

### 4. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Platform-Specific Setup

#### Windows
```bash
# PyAudio usually installs directly
pip install pyaudio

# Find your Marty's COM port:
# Device Manager → Ports (COM & LPT)
# Update main.py line 23 with your COM port
```

#### macOS
```bash
# Install portaudio for PyAudio
brew install portaudio
pip install pyaudio

# Find your Marty's USB port:
ls /dev/tty.*
# Usually /dev/tty.usbmodem* or /dev/ttyUSB0
```

#### Linux
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio

# Find your Marty's USB port:
ls /dev/ttyUSB*
# Usually /dev/ttyUSB0 or /dev/ttyACM0

# Add user to dialout group for USB access
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### 6. Configure Marty Connection

Edit `main.py` line 23:

```python
# Windows example:
my_marty = martypy.Marty("usb", "COM6")

# Linux/Mac example:
my_marty = martypy.Marty("usb", "/dev/ttyUSB0")
```

### 7. Audio Files Setup

Add these audio files to your project root:
- `BALL_LOVE.mp3` - Played when ball is detected in matched mode
- `mismatch.mp3` - Played when ball is detected in mismatch mode

Or modify the code to skip audio playback if files don't exist.

### 8. First Run

```bash
# Test camera module
python Camera_Module.py
# Press 'q' to quit

# Test the full system
python main.py
# Press Ctrl+C to stop
```

## Obtaining API Keys

### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-...`)
6. Add to `.env` file

**Pricing**: Pay-as-you-go
- Whisper: ~$0.006 per minute
- GPT-4o-mini: ~$0.15 per 1M input tokens

### ElevenLabs API Key
1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up for account
3. Go to Profile Settings → API Key
4. Copy your API key
5. Add to `.env` file

**Pricing**: Free tier available (10,000 characters/month)

## Troubleshooting

### Camera Issues
```python
# Try different camera indices
cam = cv2.VideoCapture(0)  # Try 0, 1, 2...
```

### Microphone Not Working
```bash
# Test microphone
python -m speech_recognition
```

### Marty Not Connecting
- Check USB cable
- Verify COM port/device path
- Ensure Marty is powered on
- Try different USB port

### Import Errors
```bash
# Reinstall specific package
pip install --upgrade package-name

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

## Git Commands for First Commit

```bash
# Initialize repository
git init

# Add files
git add .

# First commit
git commit -m "Initial commit: RoboMarty emotion-aware social robot"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/yourusername/robomarty.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Testing Checklist

Before sharing your repository:
- [ ] All dependencies install successfully
- [ ] Camera module runs independently
- [ ] Marty connects via USB
- [ ] Speech recognition works
- [ ] API keys are in `.env` (not committed)
- [ ] Workflow diagram is in `docs/workflow.png`
- [ ] README displays diagram correctly
- [ ] All modules import without errors

## Next Steps

1. Run the system and test all features
2. Record a demo video
3. Take screenshots for documentation
4. Write usage examples
5. Document any platform-specific quirks you encounter

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review error messages carefully
3. Verify API keys are correct
4. Check hardware connections
5. Open an issue on GitHub with detailed error logs