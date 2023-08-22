import os
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ID = '20230509182749'

OBJ_INPUT = f'./input/{ID}.obj'
MASK_INPUT = f'./input/{ID}-mask.png'

OBJ_OUTPUT = './output/segment'
OBJ_INFO   = './output/segment/meta.json'
OBJ_MASK   = f'./output/segment/{ID}-mask.obj'
REGION_OUTPUT = f'./output/segment/region.png'

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

def processing(data):
    vertices = data['vertices']
    normals  = data['normals']
    uvs      = data['uvs']
    faces    = data['faces']

    # calculate bounding box
    mean_vertices = np.mean(vertices, axis=0)
    max_x = np.max(np.abs(vertices[:, 0] - mean_vertices[0]))
    max_y = np.max(np.abs(vertices[:, 1] - mean_vertices[1]))
    max_z = np.max(np.abs(vertices[:, 2] - mean_vertices[2]))

    bounding_box = {}
    bounding_box['min'] = mean_vertices - np.array([max_x, max_y, max_z])
    bounding_box['max'] = mean_vertices + np.array([max_x, max_y, max_z])

    # translate & rescale
    p_vertices = vertices
    p_normals = normals
    p_uvs = uvs
    p_faces = faces

    p_data = {}
    p_data['vertices']    = p_vertices
    p_data['normals']     = p_normals
    p_data['uvs']         = p_uvs
    p_data['faces']       = p_faces
    p_data['boundingBox'] = bounding_box

    return p_data

def subclip(data):
    vertices     = data['vertices']
    uvs          = data['uvs']
    bounding_box = data['boundingBox']

    w, h, d = 150, 150, 150
    min_x, min_y, min_z = bounding_box['min']
    max_x, max_y, max_z = bounding_box['max']

    subclip_list = []
    for x in range(int(min_x), int(max_x), w):
        for y in range(int(min_y), int(max_y), h):
            for z in range(int(min_z), int(max_z), d):
                if (x < 0): x = 0
                if (y < 0): y = 0
                if (z < 0): z = 0
                ws, hs, ds = w, h, d
                if (x + w > max_x): ws = int(max_x - x)
                if (y + h > max_y): hs = int(max_y - y)
                if (z + d > max_z): ds = int(max_z - z)

                if np.any((vertices[:, 0] >= x) & (vertices[:, 0] < x + w) &
                          (vertices[:, 1] >= y) & (vertices[:, 1] < y + h) &
                          (vertices[:, 2] >= z) & (vertices[:, 2] < z + d)):
                    item = {}
                    item['id'] = str(len(subclip_list))
                    item['clip'] = { 'x': x, 'y': y, 'z': z, 'w': ws, 'h': hs, 'd': ds }
                    item['shape'] = { 'w': ws, 'h': hs, 'd': ds }
                    subclip_list.append(item)

    return subclip_list

# clear .obj output folder
shutil.rmtree(OBJ_OUTPUT, ignore_errors=True)
os.makedirs(OBJ_OUTPUT)

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

save_obj(OBJ_MASK, filtered_data)

p_data = processing(filtered_data)

c = p_data['boundingBox']['min']
b = p_data['boundingBox']['max']

c[c < 0] = 0
b[b < 0] = 0

info = {}
info['id'] = f'{ID}-mask'
info['clip'] = {}
info['clip']['x'] = int(c[0])
info['clip']['y'] = int(c[1])
info['clip']['z'] = int(c[2])
info['clip']['w'] = int(b[0] - c[0])
info['clip']['h'] = int(b[1] - c[1])
info['clip']['d'] = int(b[2] - c[2])

SUBCLIP_LIST = subclip(p_data)

subclip_meta = {}
subclip_meta['subclip'] = SUBCLIP_LIST

with open('./input/subclip_meta.json', "w") as outfile:
    json.dump(subclip_meta, outfile, indent=4)

meta = {}
meta['obj'] = []
meta['obj'].append(info)

with open(OBJ_INFO, "w") as outfile:
    json.dump(meta, outfile, indent=4)

with open(f'{OBJ_OUTPUT}/.gitkeep', 'w'): pass


