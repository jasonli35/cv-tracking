import PIL
import cv2

print('PIL version:', PIL.__version__) 

from PIL import Image, ImageDraw, ImageFont

image = Image.open(r'original.jpg') 
  
draw = ImageDraw.Draw(image) 

# draw white rectangle 100x40 with center in 200,150
draw.rectangle((200-50, 150-20, 200+50, 150+20), fill='white')


# find font size for text `"Hello World"` to fit in rectangle 200x100
selected_size = 1
for size in range(1, 150):
    arial = ImageFont.FreeTypeFont('arial.ttf', size=size)
    w, h = arial.getsize("Red Object")  # older versions
    
    if w > 100 or h > 40:
        break
        
    selected_size = size
    
      
arial = ImageFont.FreeTypeFont('arial.ttf', size=selected_size)


draw.text((200, 150), "Red Object", fill='black', anchor='mm', font=arial)
image.save('center-newer.jpg')

image.show()