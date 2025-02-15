import numpy
from PIL import Image
from OpenGL.GL import *
import os


def read(filename):
  
    img_path = os.path.join(os.path.dirname(__file__), 'assets', filename)
    print(f"Loading texture from: {img_path}")

    try:
        img = Image.open(img_path)
        img = img.convert('RGB') 
        print(f"Image loaded: {img.size}, Mode: {img.mode}")


        img_data = numpy.array(img.getdata(), dtype=numpy.uint8)
        print(f"Image data shape: {img_data.shape}")

    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None


    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glBindTexture(GL_TEXTURE_2D, 0)

    print(f"Texture {filename} loaded successfully.")
    return textID
