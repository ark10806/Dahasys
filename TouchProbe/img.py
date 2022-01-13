from PIL import Image
import parameter as param

img = Image.open(param.img_path)
print(img.size[0], img.size[1])
img = img.resize((int(img.size[0]/2), int(img.size[1]/2)))
img.save(param.base + 'src/new_logo.png')