import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random
from datetime import datetime
import io
import os
from google.cloud import vision
from google.oauth2 import service_account
import requests
import base64
import json
import re


st.set_page_config(
    page_title="Transpose Chords Utility",
    page_icon="👋",
)
st.title("Transpose Chords Utility")

def initLayout():
    
    #transposeDirection = st.selectbox("Transpose up or down",("Up","Down"),key="transposeDirection")
    transposeByCapo = st.number_input("Number of capo to transpose:",value=5, min_value=-11,max_value=11, key='transposeByCapo')
    languageOfSong = st.selectbox("Language of Song",("English","Chinese Simplifed","Chinese Traditional"),index=1,key="languageOfSong")
    useFlat = st.selectbox("Prefer Flat or Sharp chords",("Use Flat","Use Sharp"), index = 1, key="useFlat")
    chordFontSize = st.number_input("Font Size:",value=28, min_value=10,max_value=50, key='chordFontSize')

    FILE_TYPES = ["png","img","jpg","jpeg"]
    uploaded_file = st.file_uploader("Choose image file for conversion", type=FILE_TYPES,accept_multiple_files=False)

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img)
        usingVisionAsRPC(uploaded_file)


def languageChosen(lang):
     
    if lang == 'English':
        lang = 'eng'
    elif lang == 'Chinese Simplifed':
        lang = 'chi_sim'
    elif lang == 'Chinese Traditional':
        lang = 'chi_tra'

    return lang

def usingVisionAsRPC(image_file):
    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    scoped_credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])

    client_options = {"api_endpoint": "eu-vision.googleapis.com"}
    client = vision.ImageAnnotatorClient(client_options=client_options,credentials=scoped_credentials)
    content = image_file.getvalue()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    
    drawPdf(response)

def drawPdf(response):
    
    texts = response.text_annotations
    semitone = st.session_state['transposeByCapo']
    fontSize = st.session_state['chordFontSize']
    useFlat = st.session_state['useFlat']
    preferFlat = False

    if useFlat == 'Use Flat':
        preferFlat = True
    
    vertex_1_x = 0
    vertex_1_y = 0
    vertex_2_x = 0
    vertex_2_y = 0
    vertex_3_x = 0
    vertex_3_y = 0
    vertex_4_x = 0
    vertex_4_y = 0
    i=0
    lyrics = ""

    for text in texts:
        if i == 0:
            #lyrics = lyrics + text.description
            #vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
            #st.text('bounds: {}'.format(','.join(vertices)))
            n=0
            for vertex in text.bounding_poly.vertices:
                if n == 0:
                    vertex_1_x = vertex.x
                    vertex_1_y = vertex.y
                elif n == 1:
                        vertex_2_x = vertex.x
                        vertex_2_y = vertex.y
                elif n == 2:
                        vertex_3_x = vertex.x
                        vertex_3_y = vertex.y
                elif n == 3:
                        vertex_4_x = vertex.x
                        vertex_4_y = vertex.y
                n = n+1
        break
        
    widthHeightList = generateWidthHeight(vertex_1_x,vertex_2_x,vertex_1_y,vertex_3_y)
    pdf = Image.new("RGB", (widthHeightList[0], widthHeightList[1]), (255, 255, 255))
    draw = ImageDraw.Draw(pdf)
    font = ImageFont.truetype('SimSun.ttf',fontSize)
    i = 0
    for text in texts:
        if 'I' in text.description and i != 0:
             text.description = text.description.replace('I','|') 
        chord =  findChords(text.description)
        st.text(chord)
        if chord != "":
             oldChords =[chord]
             newChords = []
             newChords = transposeChords(oldChords,semitone, preferFlat)
             if len(newChords) > 0:
                text.description = newChords[0]
             else:
                 st.warning(chord + " not transposed")
             
        v1 =0
        v2 = 0
        n = 0
        for vertex in text.bounding_poly.vertices:
            if n == 0:
                  v1 = vertex.x
                  v2 = vertex.y
            break
        if i != 0:
            draw.text((v1,v2),text.description,fill=(0,0,0),font=font)
        
        i=i+1

    
    #pdf.save('pdf.png')
    st.image(pdf)

def generateWidthHeight(x1, x2, y1, y2):
    widthHeight = []
    #st.write('X1:'+ str(x1))
    #st.write('X2:'+str(x2))
    width = x2 - x1 +400
    height = y2 - y1 +400

    widthHeight.append(width)
    widthHeight.append(height)

    #st.write(widthHeight)

    return widthHeight 

def transposeChords(chords, index, preferFlats):
    
    _flats = st.secrets['major_chords_flat']
    _sharps = st.secrets['major_chords_sharp']
    newChords = []
    _preferFlats = preferFlats
    notes = _flats if _preferFlats else _sharps
 
    for chord in chords:
        noteParts = (chord[:1], chord[1:])
        if (chord.find("b") == 1 or chord.find("#") == 1):
            noteParts = (chord[:2], chord[2:])
 
        oldNoteIndex = -1
        if (noteParts[0] in _flats):
            oldNoteIndex = _flats.index(noteParts[0])
        elif (noteParts[0] in _sharps):
            oldNoteIndex = _sharps.index(noteParts[0])
 
        if (oldNoteIndex == -1): # Not a note
            newChords.append("".join(noteParts))
        else:
            newNote = notes[(oldNoteIndex + index) % len(notes)]
            newChords.append("".join([newNote, noteParts[1]]))
 
    return newChords

def transpose_chord(chord, semitones):
    # Dictionary mapping each chord to its index in the circle of fifths
    majorChords = []
    circle_of_fifths = {
        'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
        'Gb': 6, 'Db': 5, 'Ab': 4, 'Eb': 3, 'Bb': 2, 'F': 1
    }

    # Reverse dictionary to map index back to chord
    fifths_circle_reverse = {v: k for k, v in circle_of_fifths.items()}

    # Split chord into base and modifier
    base_chord = chord[:-1]
    modifier = chord[-1]

    # Find index of base chord in circle of fifths
    base_index = circle_of_fifths[base_chord]

    # Transpose the index
    transposed_index = (base_index + semitones) % 12

    # Get the transposed base chord
    transposed_base_chord = fifths_circle_reverse[transposed_index]

    # Check if the modifier needs to be changed due to enharmonic equivalence
    if modifier == '#':
        transposed_modifier = 'b' if transposed_base_chord[-1] == 'b' else '#'
    elif modifier == 'b':
        transposed_modifier = '#' if transposed_base_chord[-1] == '#' else 'b'
    else:
        transposed_modifier = modifier

    # Return transposed chord
    return transposed_base_chord + transposed_modifier


# Example usage
#chord = input("Enter the chord to transpose (e.g., C, Am, F#m): ")
#semitones = int(input("Enter the number of semitones to transpose (positive for up, negative for down): "))

#transposed_chord = transpose_chord(chord, semitones)
#print("Transposed chord:", transposed_chord)

def findChords(line):
    # normalize case so both "Am" and "am" match
    text = line.strip()

    note = r"[A-G]"                       # root note
    accidental = r"(?:#|##|b|bb)?"        # optional single/double accidental
    quality = r"(?:maj|min|m|sus|aug|dim|add)?"  # chord quality
    number = r"(?:\d{1,2})?"              # optional one- or two-digit extension (e.g. 7, 11, 13)
    extras = r"(?:/[A-G](?:#|b)?)?"       # optional bass note like C/E
    pattern = rf"\b{note}{accidental}{quality}{number}{extras}\b"
    chordsList = re.findall(pattern, text, flags=re.IGNORECASE)
    #st.text(chordsList)
    if len(chordsList) >0:
        #st.text(chordsList[0])
        return chordsList[0]
    else:
        return ""
    #return re.findall(pattern, text, flags=re.IGNORECASE)


initLayout()
