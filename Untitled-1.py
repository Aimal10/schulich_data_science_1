
import speech_recognition as sr
from gtts import gTTS
import os
import random  # Import the random module
import csv
import spacy


nlp = spacy.load("en_core_web_sm")



def speak_message(message):
    """Converts the given message to speech and plays it."""
    tts = gTTS(text=message, lang='en')
    save_path = f'/Users/aimaldastagirzada/voice_orders/temp_message.mp3'  # Adjust the path as necessary
    tts.save(save_path)
    os.system(f"mpg123 '{save_path}'")

def listen_for_speech(prompt=None):
    """Listens for a single speech input, recognizes text, and processes it with NLP to identify intents and entities."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            speak_message(prompt)
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    try:
        speech_text = recognizer.recognize_google(audio)
        print("Recognized:", speech_text)
        doc = nlp(speech_text.lower())
        
        # Process the recognized text to identify intents and entities
        intents_entities = process_nlp(doc)
        return intents_entities
    except sr.UnknownValueError:
        ...
    except sr.RequestError as e:
        ...

def confirm_order():
    """Asks for user's order, confirms it, and handles the confirmation response."""
    order = listen_for_speech("Please say your order.")
    if order in ["retry", "error"]:
        return False
    confirm_message = f"You said {order}. Is that correct? Please say 'yes' or 'no'."
    speak_message(confirm_message)

    confirmation = listen_for_speech()
    if "yes" in confirmation:
        speak_message("Thank you, your order has been confirmed.")
        return order
    elif "no" in confirmation:
        speak_message("Sorry, let's try that again.")
        return False
    else:
        return False

def handle_next_step():
    """Asks the user if they want to add another item or proceed to checkout."""
    while True:
        response_doc = listen_for_speech("If you would like to add another item, please say 'add another item'. If you are ready to proceed to checkout, please say 'checkout'.")
        if not response_doc or response_doc.text in ["retry", "error"]:
            continue  # This handles retries or errors effectively

        # Using NLP (Spacy) to understand the response better
        # For simplicity, here we directly check text, but you could use NLP analysis for more complex intents
        response_text = response_doc.text.lower()
        if "add another item" in response_text:
            return "add"
        elif "checkout" in response_text or "proceed" in response_text:
            return "checkout"
        else:
            speak_message("Sorry, I didn't catch that. For adding another item, please say 'add another item', or say 'checkout' to complete your purchase.")


def generate_item_cost():
    """Generates a random cost for an item between $4 and $10."""
    return random.uniform(4, 10)  # Generates a random float number


def main_process():
    """Main process to handle orders and checkout, including item costs."""
    speak_message("Welcome to Walmart. How can I assist you in what you're looking for today?")
    
    orders = []
    item_costs = []

    while True:
        order = confirm_order()
        if order and order not in ["retry", "error"]:
            orders.append(order)
            item_costs.append(generate_item_cost())  # Store the cost for each item
            
            next_step = handle_next_step()
            if next_step == "add":
                continue  # If the user wants to add another item, the loop continues
            elif next_step == "checkout":
                # Create a summary of orders with their costs
                orders_summary = ", ".join([f"{order} at ${cost:.2f}" for order, cost in zip(orders, item_costs)])
                total_cost = sum(item_costs)
                speak_message(f"Thank you for shopping at Walmart: Your total cost is ${total_cost:.2f}. Proceeding to checkout.")
                break  # Exits the loop to proceed to checkout
        else:
            # If the order is to retry or an error, you might want to handle these cases specifically
            # For example, repeat the prompt or handle the error accordingly
            continue

if __name__ == "__main__":
    main_process()




