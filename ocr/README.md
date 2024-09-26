通过 OCR 识别图片中的文字, 临时代码

## related deps

#### install `en_core_web_sm` model for spacy

```bash
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download ja_core_news_sm
# python -m spacy download ja_core_news_lg
```

#### install `tesseract` for pytesseract

```bash
sudo apt install tesseract-ocr

# Install the Language Pack for Tesseract
sudo apt-get install tesseract-ocr-chi-sim
sudo apt-get install tesseract-ocr-jpn
```

install Tesseract on Windows:

<https://github.com/UB-Mannheim/tesseract/wiki>

#### install `libgl1-mesa-glx` for `cv2.imshow()`

```bash
sudo apt-get install libgl1-mesa-glx
```

#### install `sentence_transformers`

```bash
pip install sentence_transformers
```
