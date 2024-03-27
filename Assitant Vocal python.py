from config import key

import speech_recognition as sr
from gtts import gTTS
import wikipedia
import re
import playsound
from googlesearch import search
import openai

openai.api_key = key

wikipedia.set_lang('fr')

def speak(text):
    tts = gTTS(text=text, lang='fr')
    tts.save("output.mp3")
    playsound.playsound("output.mp3")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Je vous écoute...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio, language='fr-FR')
        print(f"Vous avez dit: {command}")
        return command
    except sr.UnknownValueError:
        speak("Je suis désolé, je n'ai pas compris.")
        return None
    except sr.RequestError:
        speak("Je ne peux pas accéder au service de reconnaissance vocale.")
        return None

def rechercher_sur_wikipedia(sujet):
    try:
        info = wikipedia.summary(sujet, sentences=2, auto_suggest=True, redirect=True)
        return info
    except Exception as e:
        print(f"Erreur lors de la recherche sur Wikipedia: {e}")
        return None

def rechercher_sur_chatgpt(question):
    try:
        openai.api_key = key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erreur lors de la recherche sur ChatGPT: {e}")
        return None
    
def rechercher_sur_autre_source(sujet):
    try:
        site_url = "https://archive.wikiwix.com/trinet/#/fr/"
        query = f"{sujet} site:{site_url}"
        result = next(search(query, num=1, stop=1, lang='fr'), None)

        if result:
            return f"Informations trouvées sur le site Wikiwix : {result}"
        else:
            return f"Aucune information trouvée sur le site Wikiwix pour {sujet}"

    except Exception as e:
        print(f"Erreur lors de la recherche sur le site Wikiwix : {e}")
        return None
    
def rechercher_information(sujet):
    info_chatgpt = rechercher_sur_chatgpt(sujet)
    if info_chatgpt:
        return info_chatgpt
    
    info_wikipedia = rechercher_sur_wikipedia(sujet)
    if info_wikipedia:
        return info_wikipedia
    
    info_autre_source = rechercher_sur_autre_source(sujet)
    if info_autre_source:
        return info_autre_source
    
    return f"Aucune information trouvée pour {sujet}"

def handle_date_question(question):
    match = re.search(r"quelle est la date de (.+)", question, re.IGNORECASE)
    if match:
        topic = match.group(1)
        info = rechercher_information(topic)
        if not info:
            speak(f"Je suis désolé, je n'ai pas trouvé d'informations pour {topic}.")
        else:
            speak(info)
    else:
        speak("Je suis désolé, je peux répondre uniquement aux questions sur les dates d'événements historiques. Veuillez formuler votre question comme suit : 'Quelle est la date de... ?'")

def main():
    speak("Bonjour, je suis votre assistant virtuel spécialisé dans les dates d'événements historiques. Quelle date souhaitez-vous connaître ?")
    while True:
        command = listen()
        if command:
            command = command.lower()
            if 'quitte' in command or 'arrête' in command or 'merci' in command:
                speak("Je vous en prie, n'hésitez pas si vous avez une autre question!")
                break
            handle_date_question(command)

if __name__ == "__main__":
    main()
