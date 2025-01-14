from groq import Groq  # Import the Groq library
from json import load, dump  # For reading and writing JSON files
import datetime  # For real-time date and time information
from dotenv import dotenv_values  # For reading environment variables from a .env file

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get(Username)
Assistantname = env_vars.get(Assistantname)
GroqAPiKey = env_vars.get(GroqAPiKey)

# Debugging: Check if the API key and other variables are loaded
if not all([Username, Assistantname, GroqAPiKey]):
    raise ValueError("One or more environment variables are missing. Please check your .env file.")

print(f"API Key: {GroqAPiKey}")  # Optional: Remove this after verifying it works

# Initialize the Groq Client using the provided API key
client = Groq(api_key=GroqAPiKey)

# Define a system message
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only Hindi, even if the question is in Hindi, reply in Hindi.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot
SystemChatBot = [
    {"role": "system", "content": System}
]

# Attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)  # Load existing messages from the chat log
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Main chatbot function to handle user queries
def ChatBot(Query):
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": f"{Query}"})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

# Main program entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))

 