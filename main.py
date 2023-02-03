from PIL import Image

colors = {}

def load_colors(image: Image, gradient):
    addition = im.width
    sr = 0.0
    
    while sr <= 9:
        colors[sr] = gradient[min(round(addition * (sr  / 9)), image.width - 1), 0]
        sr += 0.1
        sr = round(sr, 1)

'''
for y in range(image.height):
        for x in range(image.width):
'''

def render_colors(image: Image, mode: int = 0):
    match mode:
        case 0:
            mode = 'std'
        case 1:
            mode = 'taiko'
        case 2:
            mode = 'ctb'
        case 3:
            mode = 'mania'
        case _:
            mode = 'unknown'
    
    for color in colors:
        print(f'[{mode}] Rendering for Star Rating "{color}" with color {colors[color]}')
        
        data = image.load()
        new_data = []
        
        for y in range(image.height):
            for x in range(image.width):
                if data[x, y][3] != 0:
                    new_data.append((colors[color][0], colors[color][1], colors[color][2], data[x, y][3]))
                else:
                    new_data.append((0, 0, 0, 0))
                    
        file_end = str(color)
        
        new_im = Image.new(image.mode, image.size)
        new_im.putdata(new_data)
        
                
        new_im = new_im.resize((32, 32), Image.BICUBIC)
        new_im.save(f'rendered/{mode}/stars_{file_end}@2x.png')
        new_im = new_im.resize((16, 16), Image.BICUBIC)
        new_im.save(f'rendered/{mode}/stars_{file_end}.png')    
                    
 
im = Image.open('difficulty_gradient.png')
gradient = im.load()

load_colors(im, gradient)

render_colors(Image.open('base_std.png'), 0)
render_colors(Image.open('base_taiko.png'), 1)
render_colors(Image.open('base_ctb.png'), 2)
render_colors(Image.open('base_mania.png'), 3)