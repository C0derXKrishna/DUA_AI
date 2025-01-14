from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get(InputLanguage, hi) #Default to English if not set

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Create the Data directory if it does not exist and write the modified HTML code to a file.
os.makedirs("Data", exist_ok=True)
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get the current working directory and generate the file path for the HTML file.
current_dir = os.getcwd()
Link = f"file://{current_dir}/Data/Voice.html"

# Set Chrome options for the WebDriver.
chrome_options = ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Allow media streams without user interaction.
chrome_options.add_argument("--use-fake-device-for-media-stream")  # Use fake devices for media.
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--disable-extensions")  # Disable any browser extensions to avoid conflicts
chrome_options.add_argument("--disable-gpu")  # Disable GPU to avoid GPU-related issues
chrome_options.add_argument("--no-sandbox")  # Disable sandbox to avoid permission issues
chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs and warnings.

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(new_query.startswith(word) for word in question_words):
        if not new_query.endswith(('.', '?', '!')):
            new_query += "?"

    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get(Link)
    # Start speech recognition by clicking the start button.
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower() in ["hin", "hi"]:
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating....")
                    return QueryModifier(UniversalTranslator(Text))
                
        except Exception as e:
            pass

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)
