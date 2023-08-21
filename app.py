import os
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ID = '20230509182749'

OBJ_INPUT = f'./input/{ID}.obj'
MASK_INPUT = f'./input/{ID}-mask.png'

REGION_OUTPUT = f'./output/region.png'
OBJ_OUTPUT = f'./output/{ID}-mask.obj'

uvs = (0.72, 0.17, 0.78, 0.35)

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

def save_obj(filename, data):
    vertices = data['vertices']
    normals  = data['normals']
    uvs      = data['uvs']
    faces    = data['faces']

    with open(filename, 'w') as f:

        for i in range(len(vertices)):
            vertex = vertices[i]
            f.write(f"v {' '.join(str(x) for x in vertex)}\n")

        for i in range(len(normals)):
            normal = normals[i]
            f.write(f"vn {' '.join(str(x) for x in normal)}\n")

        for uv in uvs:
            f.write(f"vt {' '.join(str(x) for x in uv)}\n")

        for face in faces:
            indices = ' '.join(['/'.join(map(str, vertex)) for vertex in face])
            f.write(f"f {indices}\n")

def draw_rectangle(image_path, output_path, coordinates):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    x0, y0, x1, y1 = coordinates
    w, h = image.width, image.height
    draw.rectangle([ x0*w, (1.0-y1)*h, x1*w, (1.0-y0)*h ], outline="red", width=2)  # 绘制红色方框，线宽为2
    
    # image.show()
    image.save(output_path)

shutil.rmtree('output', ignore_errors=True)
os.makedirs('output')

data = parse_obj(OBJ_INPUT)
draw_rectangle(MASK_INPUT, REGION_OUTPUT, uvs)

filtered_indices = np.where(
    (data['uvs'][:, 0] >= uvs[0]) & (data['uvs'][:, 0] <= uvs[2]) &
    (data['uvs'][:, 1] >= uvs[1]) & (data['uvs'][:, 1] <= uvs[3])
)[0]

filtered_data = {}
filtered_data['vertices'] = data['vertices'][filtered_indices]
filtered_data['normals'] = data['normals'][filtered_indices]
filtered_data['uvs'] = data['uvs'][filtered_indices]

def check_first_item(matrix):
    return all(int(item)-1 in filtered_indices for item in matrix[:, 0])
filtered_faces = data['faces'][[check_first_item(matrix) for matrix in data['faces']]]

for i, matrix in enumerate(filtered_faces):
    for j in range(3):
        matrix[j, :] = str(1 + filtered_indices.tolist().index(int(matrix[j, 0])-1))
filtered_data['faces'] = filtered_faces

save_obj(OBJ_OUTPUT, filtered_data)

# print("Filtered data_uv shape:", filtered_data_uv.shape)
# print("Filtered data_vertices shape:", filtered_data_vertices.shape)

