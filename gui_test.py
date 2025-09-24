#!/usr/bin/env python3
"""
Minimal GUI test to debug the blank window issue
"""

import tkinter as tk
from tkinter import ttk
import sys

def test_gui():
    print("Starting GUI test...")
    
    root = tk.Tk()
    root.title("Test GUI")
    root.geometry("400x300")
    
    # Force the window to the front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(lambda: root.attributes('-topmost', False))
    
    # Add content
    label = tk.Label(root, text="Hello! Can you see this?", font=("Arial", 16))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Click me!", command=lambda: print("Button clicked!"))
    button.pack(pady=20)
    
    # Force update
    root.update()
    root.deiconify()
    
    print("GUI should be visible now")
    root.mainloop()
    print("GUI closed")

if __name__ == "__main__":
    test_gui()
