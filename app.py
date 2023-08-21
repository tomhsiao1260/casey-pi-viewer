import os
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ID = '20230509182749'

OBJ_INPUT = f'./input/{ID}.obj'
MASK_INPUT = f'./input/{ID}-mask.png'
REGION_OUTPUT = f'./output/region.png'

def parse_obj(filename):
    vertices = []
    normals = []
    uvs = []
    faces = []

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append([float(x) for x in line[2:].split()])
            elif line.startswith('vn '):
                normals.append([float(x) for x in line[3:].split()])
            elif line.startswith('vt '):
                uvs.append([float(x) for x in line[3:].split()])
            elif line.startswith('f '):
                indices = [x.split('/') for x in line.split()[1:]]
                faces.append(indices)

    data = {}
    data['vertices']    = np.array(vertices)
    data['normals']     = np.array(normals)
    data['uvs']         = np.array(uvs)
    data['faces']       = np.array(faces)

    return data

def draw_rectangle(image_path, output_path, coordinates):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    x0, y0, x1, y1 = coordinates
    w, h = image.width, image.height
    draw.rectangle([ x0*w, y0*h, x1*w, y1*h ], outline="red", width=2)  # 绘制红色方框，线宽为2
    
    image.show()
    image.save(output_path)

shutil.rmtree('output', ignore_errors=True)
os.makedirs('output')

data = parse_obj(OBJ_INPUT)
draw_rectangle(MASK_INPUT, REGION_OUTPUT, (0.72, 0.65, 0.78, 0.83))

print(data['vertices'].shape)

