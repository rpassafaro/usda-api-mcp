#!/usr/bin/env python3
"""
Simple GUI Installer for debugging - minimal version
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import webbrowser

def main():
    # Create main window
    root = tk.Tk()
    root.title("USDA Food Tools Installer")
    root.geometry("500x400")
    
    # Add some basic content
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title = ttk.Label(frame, text="USDA Food Tools for Claude", font=("Arial", 18, "bold"))
    title.pack(pady=10)
    
    # Subtitle
    subtitle = ttk.Label(frame, text="Add powerful food and nutrition tools to Claude for Desktop")
    subtitle.pack(pady=5)
    
    # Features
    features_frame = ttk.LabelFrame(frame, text="What You'll Get", padding="10")
    features_frame.pack(fill=tk.X, pady=20)
    
    features = [
        "🔍 Search 500,000+ foods from USDA database",
        "📊 Get complete nutrition facts for any food",
        "🍎 Compare foods side-by-side",
        "🧪 Analyze nutrients in detail",
        "📋 Browse food categories"
    ]
    
    for feature in features:
        ttk.Label(features_frame, text=feature).pack(anchor=tk.W, pady=2)
    
    # API Key section
    api_frame = ttk.LabelFrame(frame, text="USDA API Key", padding="10")
    api_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(api_frame, text="Get your free API key:").pack(anchor=tk.W)
    
    def open_api_page():
        webbrowser.open("https://fdc.nal.usda.gov/api-guide.html")
    
    ttk.Button(api_frame, text="🌐 Get Free API Key", command=open_api_page).pack(pady=5)
    
    # API key entry
    ttk.Label(api_frame, text="Enter your API key:").pack(anchor=tk.W, pady=(10, 0))
    api_entry = ttk.Entry(api_frame, width=50, show="*")
    api_entry.pack(fill=tk.X, pady=5)
    
    # Install button
    def install():
        api_key = api_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        messagebox.showinfo("Success", "This is a test version!\n\nAPI Key received: " + api_key[:10] + "...")
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=20)
    
    ttk.Button(button_frame, text="🚀 Test Install", command=install).pack(side=tk.RIGHT)
    ttk.Button(button_frame, text="❌ Cancel", command=root.quit).pack(side=tk.RIGHT, padx=(0, 10))
    
    print("Simple GUI starting...")
    root.mainloop()
    print("Simple GUI closed.")

if __name__ == "__main__":
    print("Python version:", sys.version)
    print("Starting simple GUI installer...")
    main()
