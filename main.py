import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random
import os
from gtts import gTTS
import pygame

# ---------------------------- CONSTANTS & CONFIG ------------------------------- #
BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn = {}

# Initialize Pygame Mixer for Audio
pygame.mixer.init()

# ---------------------------- FILE PATHS ------------------------------- #
# Directories
DATA_FILE_ORIGINAL = "data/german_words.csv"
DATA_FILE_LEARNING = "data/words_to_learn_german.csv"
IMAGE_CARD_FRONT = "assets/images/card_front.png"
IMAGE_CARD_BACK = "assets/images/card_back.png"
IMAGE_RIGHT = "assets/images/right.png"
IMAGE_WRONG = "assets/images/wrong.png"
AUDIO_TEMP_PATH = "assets/sounds/temp_voice.mp3"

# ---------------------------- DATA MANAGEMENT ------------------------------- #
try:
    # Try to load the progress file first
    data = pd.read_csv(DATA_FILE_LEARNING)
except FileNotFoundError:
    # If not found, load the original dataset
    try:
        data = pd.read_csv(DATA_FILE_ORIGINAL)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {DATA_FILE_ORIGINAL}\nPlease check 'data' folder.")
        exit()

# Convert DataFrame to a list of dictionaries
to_learn = data.to_dict(orient="records")


# ---------------------------- AUDIO FUNCTION ------------------------------- #
def play_word_audio(german_word):
    """Generates and plays pronunciation for the given German word."""
    try:
        # Create TTS object
        tts = gTTS(text=german_word, lang="de")
        # Save to assets folder
        tts.save(AUDIO_TEMP_PATH)

        # Play the sound
        pygame.mixer.music.load(AUDIO_TEMP_PATH)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Audio Error: {e}")


# ---------------------------- CARD FUNCTIONS ------------------------------- #
def next_card():
    """Selects a random word and updates the UI."""
    global current_card, flip_timer

    # Cancel the previous flip timer
    window.after_cancel(flip_timer)

    if not to_learn:
        messagebox.showinfo("Completed", "Herzlichen Glückwunsch! You've learned all the words.")
        window.quit()
        return

    current_card = random.choice(to_learn)
    german_word = current_card["German"]

    # Update Canvas to Front Side (German)
    canvas.itemconfig(card_title, text="German", fill="black")
    canvas.itemconfig(card_word, text=german_word, fill="black")
    canvas.itemconfig(card_background, image=card_front_img)

    # Play Audio automatically (Optional)
    play_word_audio(german_word)

    # Set timer to flip card
    flip_timer = window.after(3000, func=flip_card)


def flip_card():
    """Flips the card to show the English translation."""
    english_word = current_card["English"]

    # Update Canvas to Back Side (English)
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=english_word, fill="white")
    canvas.itemconfig(card_background, image=card_back_img)


def is_known():
    """Removes the current card from the list and saves progress."""
    to_learn.remove(current_card)

    # Save the remaining words to CSV
    new_data = pd.DataFrame(to_learn)
    new_data.to_csv(DATA_FILE_LEARNING, index=False)

    next_card()


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Flashy - German Learning App")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

flip_timer = window.after(3000, func=flip_card)

canvas = tk.Canvas(width=800, height=526)
# Loading Images
try:
    card_front_img = tk.PhotoImage(file=IMAGE_CARD_FRONT)
    card_back_img = tk.PhotoImage(file=IMAGE_CARD_BACK)
    right_img = tk.PhotoImage(file=IMAGE_RIGHT)
    wrong_img = tk.PhotoImage(file=IMAGE_WRONG)
except tk.TclError:
    messagebox.showerror("Error", "Images not found!\nPlease check 'assets/images/' folder.")
    exit()

card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Ariel", 60, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=2)

# Buttons
unknown_button = tk.Button(image=wrong_img, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

known_button = tk.Button(image=right_img, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=1)

# Start the game
next_card()

window.mainloop()