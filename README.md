# 🔄 Mangal to Kruti Dev Converter

A production-grade web application to convert Hindi documents from **Unicode (Mangal)** font to **Kruti Dev 010** legacy font.

## ✨ Features

- 📄 **DOCX File Conversion** - Upload Word documents and download converted files
- 🔤 **Accurate Character Mapping** - Comprehensive mapping for all Devanagari characters
- 🔗 **Conjunct Handling** - Proper support for क्ष, त्र, ज्ञ, श्र and 30+ conjuncts
- 📍 **Matra Positioning** - Correct placement of vowel signs (matras)
- 🔙 **Reph Handling** - Proper र् (reph) positioning
- 🌐 **Mixed Language Support** - English text preserved as-is
- ⚫ **Nukta Support** - Correct handling of ड़, ढ़, ज़, etc.

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/fontchanger.git
cd fontchanger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Open http://localhost:8000 in your browser.

## ☁️ Deployment

### Option 1: Railway (Recommended)

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub repository
4. Railway will auto-detect the configuration and deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/ZweBXA)

### Option 2: Render

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will use the `render.yaml` configuration

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option 3: Docker

```bash
# Build the image
docker build -t mangal-to-krutidev .

# Run the container
docker run -p 8000:8000 mangal-to-krutidev
```

### Option 4: Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Open the app
heroku open
```

## 📁 Project Structure

```
fontchanger/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── Procfile            # Process definition (Heroku/Railway)
├── Dockerfile          # Container configuration
├── render.yaml         # Render deployment config
├── railway.json        # Railway deployment config
├── core/
│   ├── converter.py    # DOCX file processor
│   ├── reorder.py      # Unicode to Kruti Dev converter
│   └── mappings.py     # Character mapping tables
└── ui/
    ├── web_app.py      # FastAPI web application
    └── templates/
        └── index.html  # Web interface
```

## 🔧 Technical Details

### Conversion Process

1. **Tokenization** - Split text into Hindi, English, numbers, punctuation
2. **Normalization** - Handle special Unicode characters, dashes, quotes
3. **Syllable Parsing** - Parse Hindi words into syllable structures
4. **Conjunct Detection** - Identify and handle special character combinations
5. **Matra Positioning** - Place vowel signs correctly (especially ि before consonant)
6. **Reph Handling** - Move र् to correct position (Z after syllable)
7. **Rendering** - Convert to Kruti Dev character codes

### Supported Characters

- All Devanagari consonants (क-ह)
- All vowels and matras
- Nukta consonants (क़, ख़, ग़, ज़, ड़, ढ़, फ़)
- Numerals (०-९ → 0-9)
- Special conjuncts (30+ combinations)
- Punctuation (preserved as-is)

## ⚠️ Important Note

The output DOCX file must be viewed with **Kruti Dev 010** font installed on your system. Without this font, the converted text will appear as random characters.

[Download Kruti Dev 010 Font](https://www.wfonts.com/font/kruti-dev-010)

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
