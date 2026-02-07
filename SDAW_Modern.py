import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import threading
import speech_recognition as sr
import pyttsx3
import mediawiki as mw
import pywhatkit as yt
import xml.etree.ElementTree as ET
import webbrowser
import os
import subprocess
import datetime
import time
import requests
import sys

# Initialize CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("SDAW - Desktop Assistant")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Variables
        self.is_listening = False
        self.wolfram_app_id = 'UXA89R7337' 
        self.mediawiki = mw.MediaWiki()
        
        # Engine Setup
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        # Try to find a female voice or specific one, fallback to default
        voice_found = False
        for voice in voices:
            if "en-in" in voice.id:
                self.engine.setProperty('voice', voice.id)
                voice_found = True
                break
        if not voice_found and len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id) # Often Zira (female) on Windows

        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate - 20)

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Animation/Status Area
        self.grid_rowconfigure(1, weight=1)  # Output/Text Area
        self.grid_rowconfigure(2, weight=0)  # Input Controls

        # 1. Animation Area (Top)
        self.anim_frame = ctk.CTkFrame(self, fg_color="black")
        self.anim_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        
        self.avatar_label = ctk.CTkLabel(self.anim_frame, text="", fg_color="black")
        self.avatar_label.pack(expand=True, fill="both")

        # Load GIF
        try:
            self.gif_image = Image.open(".venv/Assests/AI Interface.gif")
            self.gif_frames = [ctk.CTkImage(frame.copy(), size=(500, 300)) for frame in ImageSequence.Iterator(self.gif_image)]
            self.current_frame = 0
            self.animate_gif()
        except Exception as e:
            self.avatar_label.configure(text=f"Animation Error: {e}")

        # 2. Output Area (Middle) - For Wikipedia/Logs
        self.output_box = ctk.CTkTextbox(self, font=("Roboto", 14), wrap="word")
        self.output_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.output_box.insert("0.0", "System Initialized...\n")
        self.output_box.configure(state="disabled") # Read-only mostly

        # 3. Input Area (Bottom)
        self.input_frame = ctk.CTkFrame(self, height=80, corner_radius=10)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(0, weight=1) # Entry expands

        # Input Widgets
        self.entry_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(
            self.input_frame, 
            textvariable=self.entry_var, 
            placeholder_text="Type command or speak...",
            font=("Roboto", 14),
            height=40
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=15)
        self.entry.bind("<Return>", lambda e: self.process_text_input())

        self.submit_btn = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.process_text_input,
            width=80,
            height=40
        )
        self.submit_btn.grid(row=0, column=1, padx=(0, 10), pady=15)

        # Status Label (Overlay)
        self.status_label = ctk.CTkLabel(self.anim_frame, text="Waiting...", font=("Roboto", 16), text_color="gray", fg_color="black")
        self.status_label.place(relx=0.5, rely=0.9, anchor="center")

        # Startup
        self.after(1000, self.welcome)
        
        # Start Listening Loop (in background)
        self.listen_thread = threading.Thread(target=self.voice_listen_loop, daemon=True)
        self.listen_thread.start()

    def animate_gif(self):
        if hasattr(self, 'gif_frames'):
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.avatar_label.configure(image=self.gif_frames[self.current_frame])
            # Adjust speed if needed - 50ms is 20fps
            self.after(50, self.animate_gif)

    def append_text(self, text, sender="System"):
        self.output_box.configure(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.output_box.insert("end", f"[{timestamp}] {sender}: {text}\n\n")
        self.output_box.see("end")
        self.output_box.configure(state="disabled")

    def speak(self, text):
        # Update UI
        self.status_label.configure(text="Speaking...")
        # Run in thread
        threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()

    def _speak_thread(self, text):
        self.is_speaking = True
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            pass
        self.is_speaking = False
        self.after(0, lambda: self.status_label.configure(text="Ready"))

    def check_internet(self):
        try:
            # Try to connect to a reliable host
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    def update_connection_status(self):
        is_connected = self.check_internet()
        
        if is_connected:
             self.status_label.configure(text="Online - Voice & Text Ready", text_color="white")
        else:
             self.status_label.configure(text="⚠ Offline - Text Only Mode", text_color="orange")

        # Check again every 10 seconds
        self.after(10000, self.update_connection_status)

    def process_text_input(self):
        text = self.entry_var.get().strip()
        if text:
            self.append_text(text, "User")
            self.entry_var.set("")
            self.process_command(text)

    def voice_listen_loop(self):
        r = sr.Recognizer()
        while True:
            # Don't listen if offline
            if self.check_internet():
                # Pause listening if the assistant is speaking to avoid feedback loops
                if getattr(self, 'is_speaking', False):
                    time.sleep(0.5)
                    continue

                try:
                    with sr.Microphone() as source:
                        self.after(0, lambda: self.status_label.configure(text="Listening..."))
                        r.adjust_for_ambient_noise(source, duration=0.5)
                        # Check again before listening
                        if getattr(self, 'is_speaking', False): continue
                        
                        audio = r.listen(source)
                        
                        self.after(0, lambda: self.status_label.configure(text="Processing Voice..."))
                        query = r.recognize_google(audio).lower()
                        
                        self.after(0, lambda: self.append_text(query, "User (Voice)"))
                        self.after(0, lambda: self.process_command(query))

                except sr.UnknownValueError:
                     # Just go back to ready state silently if nothing heard
                     self.after(0, self.update_connection_status)
                except sr.RequestError:
                    self.after(0, lambda: self.status_label.configure(text="Connection Lost...", text_color="orange"))
                    time.sleep(2)
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)
            else:
                time.sleep(1)

    def welcome(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            wish = "Good Morning"
        elif 12 <= hour < 16:
            wish = "Good Afternoon"
        else:
            wish = "Good Evening"
        
        greeting = f"{wish}, I am your Assistant. How can I help you?"
        self.append_text(greeting)
        self.speak(greeting)
        # Start monitoring connection
        self.update_connection_status()

    def process_command(self, query):
        query = query.lower()
        
        # Logic from SDAW.py
        if any(w in query for w in ['goodbye', 'bye', 'see you']):
            self.append_text("Goodbye! Closing application...")
            self.speak("Goodbye! Have a nice day.")
            self.after(2000, self.destroy)
            
        elif 'command prompt' in query or 'cmd' in query:
            self.run_app("Command Prompt", "cmd.exe")
            
        elif 'paint' in query:
            self.run_app("Paint", "mspaint.exe")
            
        elif 'setting' in query or 'control panel' in query:
            self.run_app("Control Panel", "control.exe")
            
        elif 'calculator' in query or 'calc' in query:
            self.run_app("Calculator", "calc.exe")
            
        elif 'notepad' in query:
            self.run_app("Notepad", "notepad.exe")
            
        elif 'wordpad' in query:
            self.run_app("Wordpad", "wordpad.exe")
            
        elif any(x in query for x in ['folder', 'explorer', 'file', 'thispc']):
            self.run_app("File Explorer", "explorer.exe")
            
        elif 'vlc' in query:
            self.run_app("VLC", "vlc.exe")
            
        elif 'chrome' in query or 'browser' in query:
            self.run_app("Chrome", "chrome.exe")
            
        elif 'firefox' in query:
            self.run_app("Firefox", "firefox.exe")
            
        elif 'shutdown' in query:
            self.speak("Shutting down the system")
            subprocess.run(["shutdown", "-s"])
            
        # Internet Dependent Features - Check Connection First
        elif 'search' in query or 'google' in query:
            if not self.check_internet():
                self.speak("I cannot search Google without an internet connection.")
                return
            term = query.replace("search", "").replace("google", "").strip()
            url = f"https://google.com/search?q={term}"
            self.append_text(f"Searching Google for: {term}")
            self.speak(f"Searching for {term}")
            webbrowser.open(url)
            
        elif 'youtube' in query:
            if not self.check_internet():
                self.speak("I cannot play YouTube without an internet connection.")
                return
            term = query.replace("youtube", "").strip()
            url = f"https://youtube.com/results?search_query={term}"
            self.append_text(f"Opening YouTube for: {term}")
            self.speak(f"Opening YouTube for {term}")
            webbrowser.open(url)
            
        elif 'wikipedia' in query:
            if not self.check_internet():
                self.speak("Wikipedia is unavailable without internet.")
                return
            term = query.replace("wikipedia", "").strip()
            # If term is empty, ask user
            if not term:
                self.speak("What should I search on Wikipedia?")
                return
                
            self.append_text(f"Searching Wikipedia for: {term}")
            threading.Thread(target=self.search_wikipedia, args=(term,), daemon=True).start()
            
        elif 'play' in query:
            if not self.check_internet():
                self.speak("I cannot play online videos without internet.")
                return
            term = query.replace("play", "").strip()
            self.append_text(f"Playing on YouTube: {term}")
            self.speak(f"Playing {term} on YouTube")
            try:
                yt.playonyt(term)
            except Exception as e:
                self.append_text(f"Error playing video: {e}")
                
        else:
            if not self.check_internet():
                 self.append_text("Offline: Cannot query Knowledge Base.", "System")
                 self.speak("I am offline and cannot answer that.")
                 return

            # WolframAlpha fallback
            self.append_text(f"Querying Knowledge Base: {query}")
            threading.Thread(target=self.query_wolfram, args=(query,), daemon=True).start()

    def run_app(self, name, cmd):
        try:
            self.speak(f"Opening {name}")
            # Use os.startfile for better Windows application support (e.g. VLC)
            # If it's a direct command like cmd.exe, startfile works too if in path.
            # For some apps, we might need shell=True in Popen, but startfile is 'double click' equivalent.
            try:
                os.startfile(cmd)
            except FileNotFoundError:
                # Fallback to Popen if startfile fails (though startfile is usually better for registered apps)
                 subprocess.Popen(cmd, shell=True) 
        except Exception as e:
            self.append_text(f"Failed to open {name}: {e}")
            self.speak(f"I could not open {name}")

    def search_wikipedia(self, query):
        try:
            summary = self.mediawiki.summary(query, sentences=3)
            self.after(0, lambda: self.append_text(f"Wikipedia: {summary}\n", "Wikipedia"))
            self.speak("According to Wikipedia, " + summary)
        except mw.DisambiguationError as e:
            # Handle disambiguation by picking the first option or asking
            try:
                options = e.options[:3] # Take top 3
                suggestion = ", ".join(options)
                self.after(0, lambda: self.append_text(f"Ambiguous: Did you mean {suggestion}?", "Wikipedia"))
                self.speak(f"That is ambiguous. Did you mean {options[0]}?")
            except:
                 self.speak("That query is ambiguous.")
        except Exception as e:
            self.after(0, lambda: self.append_text(f"Wikipedia Error: {e}"))
            self.speak("I encountered an error searching Wikipedia.")

    def query_wolfram(self, query):
        print(f"DEBUG: Starting Wolfram Query for '{query}'")
        if not self.check_internet():
             self.speak("I am offline.")
             return

        try:
            # Direct API call to bypass library bug (Content-Type assertion error)
            url = "http://api.wolframalpha.com/v2/query"
            params = {
                "appid": self.wolfram_app_id,
                "input": query,
                "format": "plaintext",
                "scantimeout": "10.0" 
            }
            
            print(f"DEBUG: sending request to {url}")
            response = requests.get(url, params=params, timeout=15)
            print(f"DEBUG: Response Status: {response.status_code}")
            
            if response.status_code != 200:
                self.after(0, lambda: self.append_text(f"Wolfram API Error: {response.status_code}", "Error"))
                self.speak("I couldn't access the knowledge base.")
                return

            # Parse XML
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as xml_err:
                print(f"DEBUG: XML Parse Error: {xml_err}")
                self.after(0, lambda: self.append_text(f"Wolfram XML Error: {xml_err}", "Error"))
                return
            
            # Check success
            if root.get('success') != 'true':
                 self.after(0, lambda: self.append_text("WolframAlpha could not understand the query.", "Error"))
                 self.speak("I'm not sure about that.")
                 return

            answer = None

            # 1. Search for 'Result' pod or primary pod
            for pod in root.findall('pod'):
                if pod.get('primary') == 'true' or pod.get('title') == 'Result':
                    for subpod in pod.findall('subpod'):
                        plaintext = subpod.find('plaintext')
                        if plaintext is not None and plaintext.text:
                            answer = plaintext.text
                            break
                if answer: break
            
            # 2. Fallback: Look for "Decimal approx" or similar if no primary result
            if not answer:
                 for pod in root.findall('pod'):
                    if "decimal" in pod.get('title', '').lower():
                         for subpod in pod.findall('subpod'):
                            plaintext = subpod.find('plaintext')
                            if plaintext is not None and plaintext.text:
                                answer = plaintext.text
                                break
                    if answer: break

            # 3. Last Result: Use the second pod (usually the answer after Input)
            if not answer:
                pods = root.findall('pod')
                if len(pods) > 1:
                     # pod[0] is usually "Input", pod[1] is result
                     for subpod in pods[1].findall('subpod'):
                        plaintext = subpod.find('plaintext')
                        if plaintext is not None and plaintext.text:
                            answer = plaintext.text
                            break

            if answer:
                print(f"DEBUG: Answer found: {answer[:50]}...")
                self.after(0, lambda: self.append_text(answer, "WolframAlpha"))
                self.speak(answer)
            else:
                print("DEBUG: No answer found in pods")
                self.after(0, lambda: self.append_text("WolframAlpha returned data but no readable text found.", "Info"))
                self.speak("I found some data but couldn't read a summary.")

        except Exception as e:
            print(f"DEBUG: General Exception: {e}")
            self.after(0, lambda: self.append_text(f"Wolfram Error: {e}", "Error"))
            self.speak("I encountered an error with the knowledge base.")

if __name__ == "__main__":
    app = AssistantApp()
    app.mainloop()
