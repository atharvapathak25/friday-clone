import customtkinter
import pyttsx3
import time
import speech_recognition as sr
import datetime
import requests
from bs4 import BeautifulSoup
import os
import pyautogui
from PIL import Image
import pywhatkit
import webbrowser
import smtplib
import wikipedia
import openai
import pyjokes
import json
import cv2
import numpy as np
import threading

# Initialize OpenAI API key
openai.api_key = ''

# Set appearance for customtkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

face1 = "D:/fridayy/.idea/opencv_face_detector.pbtxt"
face2 = "D:/fridayy/.idea/opencv_face_detector_uint8.pb"
age1 = "D:/fridayy/.idea/age_deploy.prototxt"
age2 = "D:/fridayy/.idea/age_net.caffemodel"
gen1 = "D:/fridayy/.idea/gender_deploy.prototxt"
gen2 = "D:/fridayy/.idea/gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

# Using models
face_net = cv2.dnn.readNet(face2, face1)
age_net = cv2.dnn.readNet(age2, age1)
gen_net = cv2.dnn.readNet(gen2, gen1)

# Categories of distribution
age_list = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
gender_list = ['Male', 'Female']

class VirtualAssistant(customtkinter.CTk):
    def _init_(self):
        super()._init_()
        self.geometry("800x600")
        self.title("CYPHER")
        self.configure(bg_color="#2b2b2b")

        self.header_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        self.header_frame.pack(pady=20, padx=20, fill="x")

        self.header_label = customtkinter.CTkLabel(self.header_frame, text="VOX CYPHER", font=("Arial", 24))
        self.header_label.pack(pady=10, padx=10)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10, fg_color="#2b2b2b")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.text_1 = customtkinter.CTkTextbox(self.main_frame, height=200, width=600, border_width=2, corner_radius=10)
        self.text_1.pack(pady=10, padx=10)
        self.text_1.insert("end", "Welcome to VOX CYPHER! How can I help you?\n")

        self.button_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, fg_color="#2b2b2b")
        self.button_frame.pack(pady=10, padx=10, fill="x")

        self.button_1 = customtkinter.CTkButton(self.button_frame, text="Run Assistant", command=self.run_assistant, width=150)
        self.button_1.pack(side="left", padx=10, pady=10)

        self.face_detection_button = customtkinter.CTkButton(self.button_frame, text="Face Detection", command=self.start_face_detection, width=150)
        self.face_detection_button.pack(side="left", padx=10, pady=10)

        self.weather_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, fg_color="#2b2b2b")
        self.weather_frame.pack(pady=10, padx=10, fill="x")

        self.weather_label = customtkinter.CTkLabel(self.weather_frame, text="Enter city for weather:")
        self.weather_label.pack(side="left", padx=10, pady=10)

        self.weather_entry = customtkinter.CTkEntry(self.weather_frame, width=250)
        self.weather_entry.pack(side="left", padx=10, pady=10)

        self.weather_button = customtkinter.CTkButton(self.weather_frame, text="Get Weather", command=self.get_weather_from_entry, width=150)
        self.weather_button.pack(side="left", padx=10, pady=10)

        self.weather_speak_button = customtkinter.CTkButton(self.weather_frame, text="Speak City", command=self.get_weather_from_speech, width=150)
        self.weather_speak_button.pack(side="left", padx=10, pady=10)

        self.voices = []
        self.engine = self.initialize_tts_engine()
        if self.engine:
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[0].id)
        self.introduce_itself()

        self.face_detection_thread = None

    def initialize_tts_engine(self):
        try:
            engine = pyttsx3.init('sapi5')
            return engine
        except ImportError:
            print("Pyttsx3 initialization failed. Please check the installation.")
        except RuntimeError:
            print("Pyttsx3 runtime error. Please check the installation.")
        except Exception as e:
            print(e)
        return None

    def display_and_speak(self, message):
        self.text_1.insert("end", f"{message}\n")
        self.text_1.see("end")
        self.update_idletasks()
        if self.engine:
            self.engine.say(message)
            self.engine.runAndWait()

    def introduce_itself(self):
        self.display_and_speak("Hello, I am CYPHER, your personal assistant. How may I assist you today?")

    def takecommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.display_and_speak("Listening...")
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            try:
                self.display_and_speak("Recognizing...")
                query = r.recognize_google(audio, language='en-in')
                self.display_and_speak(f"User said: {query}")
                return query
            except sr.UnknownValueError:
                self.display_and_speak("Sorry, I didn't catch that. Could you please repeat?")
            except sr.RequestError:
                self.display_and_speak("Sorry, I'm having trouble. Please try again later.")
            except Exception as e:
                print(e)
        return "none"

    def wish(self):
        hour = int(datetime.datetime.now().hour)
        tt = time.strftime("%I:%M %p")
        if 0 <= hour < 12:
            self.display_and_speak(f"Good morning, it's {tt}")
        elif 12 <= hour < 18:
            self.display_and_speak(f"Good afternoon, it's {tt}")
        else:
            self.display_and_speak(f"Good evening, it's {tt}")
        self.display_and_speak("How may I assist you")

    def news(self, source='techcrunch', count=5):
        api_key = "YOUR_NEWS_API_KEY"
        main_url = f'http://newsapi.org/v2/top-headlines?sources={source}&apiKey={api_key}'
        main_page = requests.get(main_url).json()
        articles = main_page["articles"][:count]
        for i, article in enumerate(articles):
            self.display_and_speak(f"Headline {i + 1}: {article['title']}")

    def take_screenshot(self):
        SCREENSHOT_DIR = "C:/Users/Savita Pathak/Pictures/Screenshots"
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        image_path = os.path.join(SCREENSHOT_DIR, filename)
        image = pyautogui.screenshot()
        image.save(image_path)
        Image.open(image_path).show()

    def open_notepad(self):
        notepad_path = r"C:\Windows\system32\notepad.exe"
        os.startfile(notepad_path)

    def write_notepad(self):
        self.display_and_speak("What do you want to write in Notepad?")
        content = self.takecommand()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"notepad_{timestamp}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w") as f:
            f.write(content)
        os.startfile(filepath)

    def tell_joke(self):
        joke = pyjokes.get_joke()
        self.display_and_speak(joke)

    def play_youtube(self):
        self.display_and_speak("What do you want me to search on YouTube?")
        search_query = self.takecommand()
        self.display_and_speak(f"Playing {search_query} on YouTube")
        pywhatkit.playonyt(search_query)

    def google_search(self, query):
        self.display_and_speak(f"Searching Google for {query}")
        query = query.replace(" ", "+")
        url = f"https://google.com/search?q={query}"
        webbrowser.open(url)

    def open_facebook(self):
        self.display_and_speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")

    def open_instagram(self):
        self.display_and_speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com")

    def open_github(self):
        self.display_and_speak("Opening GitHub")
        webbrowser.open("https://www.github.com")

    def open_stackoverflow(self):
        self.display_and_speak("Opening StackOverflow")
        webbrowser.open("https://stackoverflow.com")

    def send_email(self):
        self.display_and_speak("Whom do you want to email?")
        recipient = self.takecommand().lower()
        self.display_and_speak("What should be the subject?")
        subject = self.takecommand()
        self.display_and_speak("What should be the content?")
        content = self.takecommand()
        email_details = {
            'recipient': recipient,
            'subject': subject,
            'content': content
        }
        self.display_and_speak(f"Sending email to {recipient}")
        # Your email sending logic goes here

    def chat_with_openai(self, prompt):
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.9,
        )
        reply = response.choices[0].text.strip()
        self.display_and_speak(reply)

    def run_assistant(self):
        self.wish()
        while True:
            query = self.takecommand().lower()
            if 'open youtube' in query:
                self.play_youtube()
            elif 'google search' in query:
                search_query = query.replace("google search", "")
                self.google_search(search_query)
            elif 'open facebook' in query:
                self.open_facebook()
            elif 'open instagram' in query:
                self.open_instagram()
            elif 'open github' in query:
                self.open_github()
            elif 'open stackoverflow' in query:
                self.open_stackoverflow()
            elif 'news' in query:
                self.news()
            elif 'screenshot' in query:
                self.take_screenshot()
            elif 'open notepad' in query:
                self.open_notepad()
            elif 'write notepad' in query:
                self.write_notepad()
            elif 'joke' in query:
                self.tell_joke()
            elif 'send email' in query:
                self.send_email()
            elif 'chat' in query:
                self.display_and_speak("What's your question?")
                prompt = self.takecommand()
                self.chat_with_openai(prompt)
            elif 'stop' in query or 'exit' in query:
                self.display_and_speak("Goodbye!")
                break
            else:
                self.display_and_speak("I didn't understand that. Can you please repeat?")

    def get_weather_from_entry(self):
        city = self.weather_entry.get()
        self.get_weather(city)

    def get_weather_from_speech(self):
        self.display_and_speak("Which city?")
        city = self.takecommand()
        self.get_weather(city)

    def get_weather(self, city):
        api_key = "b7a69dcee9468dce40ca14e1cd980aca"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + api_key + "&q=" + city
        response = requests.get(complete_url)
        weather_data = response.json()
        if weather_data["cod"] != "404":
            main = weather_data["main"]
            temperature = main["temp"]
            pressure = main["pressure"]
            humidity = main["humidity"]
            weather = weather_data["weather"]
            weather_description = weather[0]["description"]
            weather_report = (f"Temperature: {temperature}K\n"
                              f"Atmospheric pressure: {pressure}hPa\n"
                              f"Humidity: {humidity}%\n"
                              f"Description: {weather_description}")
            self.display_and_speak(weather_report)
        else:
            self.display_and_speak("City Not Found!")

    def start_face_detection(self):
        if self.face_detection_thread is None or not self.face_detection_thread.is_alive():
            self.face_detection_thread = threading.Thread(target=self.face_detection)
            self.face_detection_thread.start()
        else:
            self.display_and_speak("Face detection is already running")

    def face_detection(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_face, bboxes = self.get_face_box(face_net, frame)
            if not bboxes:
                self.display_and_speak("No face detected")
            for bbox in bboxes:
                face = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                gen_net.setInput(blob)
                gender_preds = gen_net.forward()
                gender = gender_list[gender_preds[0].argmax()]
                age_net.setInput(blob)
                age_preds = age_net.forward()
                age = age_list[age_preds[0].argmax()]
                label = f"{gender}, {age}"
                cv2.putText(frame_face, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow("Age-Gender", frame_face)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def get_face_box(self, net, frame, conf_threshold=0.7):
        frame_opencv_dnn = frame.copy()
        frame_height = frame_opencv_dnn.shape[0]
        frame_width = frame_opencv_dnn.shape[1]
        blob = cv2.dnn.blobFromImage(frame_opencv_dnn, 1.0, (300, 300), [104, 117, 123], True, False)
        net.setInput(blob)
        detections = net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frame_width)
                y1 = int(detections[0, 0, i, 4] * frame_height)
                x2 = int(detections[0, 0, i, 5] * frame_width)
                y2 = int(detections[0, 0, i, 6] * frame_height)
                bboxes.append([x1, y1, x2, y2])
                cv2.rectangle(frame_opencv_dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
        return frame_opencv_dnn, bboxes


if __name__ == "_main_":
    app = VirtualAssistant()
    app.mainloop()