# OCR japanese translator overlay

Wonky OCR japanese translator overlay, mainly made for Blue Protocol.

## Development

For development, you will need Tesseract. Get it here: https://github.com/tesseract-ocr/tesseract
You might need to change the `pytesseract.pytesseract.tesseract_cmd` to your tesseract.exe, if you're not using windows or not installing it on the default location.

Additionally you'll need the `jpn.traineddata` from here: https://github.com/tesseract-ocr/tessdata/blob/main/jpn.traineddata
Simply move it into `tessdata` inside your tesseract folder.

Don't forget to `pip install -r requirements.txt` before starting.