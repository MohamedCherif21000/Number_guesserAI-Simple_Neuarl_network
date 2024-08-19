import tkinter as tk
from tkinter import ttk
import random
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import os
import json

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class GuessApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Guessing Game")
        self.master.geometry("300x200")
        self.master.configure(bg="#f0f0f0")

        self.total_guesses = 0
        self.ai_wins = 0

        self.current_range = range(1, 101)
        self.ai_model = self.create_model()
        self.history = self.load_history()
        self.all_guesses = self.load_all_guesses()

        self.style = ttk.Style()
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))

        self.label = ttk.Label(master, text="AI Guess: ")
        self.label.pack(pady=10)

        self.entry = ttk.Entry(master, width=20)
        self.entry.pack(pady=5)

        self.submit_button = ttk.Button(master, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        self.result_label = ttk.Label(master, text="")
        self.result_label.pack(pady=5)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_model(self):
        model = Sequential([
            Input(shape=(5,)),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(loss='mse', optimizer='adam')
        return model

    def load_history(self):
        try:
            with open('history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_history(self):
        with open('history.json', 'w') as f:
            json.dump(self.history, f)

    def load_all_guesses(self):
        try:
            with open('all_guesses.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_all_guesses(self):
        with open('all_guesses.json', 'w') as f:
            json.dump(self.all_guesses, f)

    def submit(self):
        user_guess = int(self.entry.get())
        self.total_guesses += 1

        self.history.append(user_guess)
        self.all_guesses.append(user_guess)
        if len(self.history) > 5:
            self.history = self.history[-5:]

        if len(self.history) == 5:
            X = np.array([self.history])
            y = np.array([[user_guess]])

            self.ai_model.fit(X, y, epochs=10, verbose=0)

            ai_guess_raw = self.ai_model.predict(np.array([self.history]))[0][0]
            ai_guess = max(1, min(100, int(round(ai_guess_raw))))
        else:
            ai_guess = random.randint(1, 100)

        win_rate = self.ai_wins / self.total_guesses * 100

        if ai_guess == user_guess:
            self.ai_wins += 1
            self.result_label.config(text="AI wins!", foreground="green")
        else:
            self.result_label.config(text="AI loses!", foreground="red")

        self.label.config(text="AI Guess: {}".format(ai_guess))
        self.result_label.config(text=f"{self.result_label.cget('text')} Win rate: {win_rate:.2f}%")
        self.entry.delete(0, tk.END)

    def on_closing(self):
        self.save_history()
        self.save_all_guesses()
        self.master.destroy()

root = tk.Tk()
app = GuessApp(root)
root.mainloop()
