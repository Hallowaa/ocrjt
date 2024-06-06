import re
import pyautogui
import pytesseract
from PIL import Image
import time
import tkinter as tk
from tkinter import Label
import ctypes
from mtranslate import translate
from langdetect import detect

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set DPI awareness to avoid scaling issues
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print("Could not set DPI awareness:", e)

# Regular expression to match Japanese characters
japanese_pattern = re.compile(r'[\u3040-\u3096\u30A0-\u30FF\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A]+')
padding = 5

def extract_text_with_positions():
    return pytesseract.image_to_data(pyautogui.screenshot(), output_type=pytesseract.Output.DICT, lang='jpn')

def should_translate(text):
    if japanese_pattern.search(text):
        try:
            return detect(text) == 'ja'
        except:
            return False
    else:
        return False

def extract_japanese_text(data):
    japanese_text_segments = []
    
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 30: # confidence check [0, 100]
          text = data['text'][i].strip()
          if text and should_translate(text):
              japanese_text_segments.append({
                  'text': text,
                  'x': data['left'][i],
                  'y': data['top'][i],
                  'w': data['width'][i],
                  'h': data['height'][i]
              })

    return japanese_text_segments
    
def sort_text_segments_into_rows(text_segments):
    sorted_text_segments = sorted(text_segments, key=lambda x: x['y'])  # sort by y

    rows = []
    current_row = []

    for segment in sorted_text_segments:
        if not current_row or abs(current_row[-1]['y'] - segment['y']) < 12:  # y threshold
            current_row.append(segment)
        else:
            rows.append(sorted(current_row, key=lambda p: p['x'])) # sort by x
            current_row = [segment]
    
    if current_row:
        rows.append(sorted(current_row, key=lambda p: p['x']))

    return rows

def find_sentences_in_row(row):
    sentences = []
    current_sentence = []

    for segment in row:
        if not current_sentence or abs(current_sentence[-1]['x'] + current_sentence[-1]['w'] - segment['x']) < 120:  # x threshold
            current_sentence.append(segment)
        else:
            sentences.append(current_sentence)
            current_sentence = [segment]
    
    if current_sentence:
        sentences.append(current_sentence)

    return sentences

def update_overlay(data):
    # clear
    for widget in overlay.winfo_children():
        widget.destroy()

    segments = extract_japanese_text(data)
    rows = sort_text_segments_into_rows(segments)
    #for segment in segments:
    #    label = Label(overlay, text="", bg="yellow", font=("Arial", 12, "bold"), padx=padding, pady=padding)
    #    label.place(x=segment['x'], y=segment['y']-27, width=segment['w']+2*padding, height=segment['h']+2*padding)

    for row in rows:
      for sentence in find_sentences_in_row(row):
        text = ""
        for i in range(len(sentence)):
            text += sentence[i]['text']
        translated = translate(text)
        label = Label(overlay, text=translated, bg="yellow", font=("Arial", 12, "bold"), padx=padding, pady=padding)
        w = 0
        for c in range(len(sentence)):
            w += sentence[c]['w']
        # -25 on y to compensate for top bar
        label.place(x=sentence[0]['x'], y=sentence[0]['y']-27, width=w+2*padding, height=max(sentence, key=lambda x: x['h'])['h']+2*padding)          

overlay = tk.Tk()
overlay.attributes("-topmost", True)
overlay.attributes("-transparentcolor", overlay["bg"])
overlay.geometry("{0}x{1}+0+0".format(overlay.winfo_screenwidth(), overlay.winfo_screenheight()))
overlay.wm_attributes("-alpha", 0.8)

def refresh_overlay(event):
    data = extract_text_with_positions()
    update_overlay(data)

def clear(event):
    for widget in overlay.winfo_children():
        widget.destroy()

overlay.bind("<0>", refresh_overlay)
overlay.bind("<+>", clear)

overlay.mainloop()