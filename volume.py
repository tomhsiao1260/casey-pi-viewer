import os
import json
import nrrd
import shutil
import numpy as np
import tifffile as tiff

ID = '20230509182749'
SUBCLIP_DIR = './input/subclip_meta.json'

NRRD_OUTPUT = './output/volume'
NRRD_INFO   = './output/volume/meta.json'

c = { 'x': 3059, 'y': 2017, 'z': 1439, 'w': 596, 'h': 432, 'd': 662 }
image_stack = np.zeros((c['w'], c['h'], c['d']), dtype=np.float32)

def write_nrrd(NRRD_DIR, data):
    # header = {'spacings': [1.0, 1.0, 1.0]}
    # nrrd.write(NRRD_DIR, data, header)
    nrrd.write(NRRD_DIR, data)

def add_data(n, p, s, c, image_stack, image_path):
    # z, y, x -> x, y, z
    image = tiff.imread(image_path)
    image = np.transpose(image, (2, 1, 0))

    x, y, z = p
    nx, ny, nz = n
    xc, yc, zc = (nx-1) * 500, (ny-1) * 500, (nz-1) * 500

    xs, xe = sorted([ xc, xc + 500, c['x'], c['x'] + c['w'] ])[1:3]
    ys, ye = sorted([ yc, yc + 500, c['y'], c['y'] + c['h'] ])[1:3]
    zs, ze = sorted([ zc, zc + 500, c['z'], c['z'] + c['d'] ])[1:3]

    w, h, d = xe-xs, ye-ys, ze-zs
    image_stack[x:x+w, y:y+h, z:z+d] = image[xs-xc:xe-xc, ys-yc:ye-yc, zs-zc:ze-zc]
    s[(nx, ny, nz)] = { 'w': w, 'h': h, 'd': d }

s = {}
n = (7, 5, 3)
p = (0, 0, 0)
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

n = (7, 5, 4)
p = (0, 0, s[(7, 5, 3)]['d'])
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

n = (7, 5, 5)
p = (0, 0, s[(7, 5, 3)]['d'] + s[(7, 5, 4)]['d'])
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

n = (8, 5, 3)
p = (s[(7, 5, 3)]['w'], 0, 0)
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

n = (8, 5, 4)
p = (s[(7, 5, 3)]['w'], 0, s[(7, 5, 3)]['d'])
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

n = (8, 5, 5)
p = (s[(7, 5, 3)]['w'], 0, s[(7, 5, 3)]['d'] + s[(7, 5, 4)]['d'])
# put into stack
print(f'processing {n} ...')
add_data(n, p, s, c, image_stack, f'./input/cell_yxz_{n[1]:03d}_{n[0]:03d}_{n[2]:03d}.tif')

# clear .nrrd output folder
shutil.rmtree(NRRD_OUTPUT, ignore_errors=True)
os.makedirs(NRRD_OUTPUT)

with open(SUBCLIP_DIR, 'r') as json_file:
    data = json.load(json_file)
SUBCLIP_LIST = data['subclip']

# generate .nrrd file from image stack
for item in SUBCLIP_LIST:
    sc = item['clip']
    sc_id = item['id']

    xc, yc, zc = c['x'], c['y'], c['z']
    xs, xe = sorted([ sc['x'], sc['x'] + sc['w'], c['x'], c['x'] + c['w'] ])[1:3]
    ys, ye = sorted([ sc['y'], sc['y'] + sc['h'], c['y'], c['y'] + c['h'] ])[1:3]
    zs, ze = sorted([ sc['z'], sc['z'] + sc['d'], c['z'], c['z'] + c['d'] ])[1:3]
    sc_stack = image_stack[xs-xc:xe-xc, ys-yc:ye-yc, zs-zc:ze-zc]

    write_nrrd(f'{NRRD_OUTPUT}/{sc_id}.nrrd', sc_stack)
    print(f'generate nrrd {sc_id} {sc_stack.shape} ...')

# save relevant info and copy to client
meta = {}
meta['nrrd'] = SUBCLIP_LIST

with open(NRRD_INFO, "w") as outfile:
    json.dump(meta, outfile, indent=4)

with open(f'{NRRD_OUTPUT}/.gitkeep', 'w'): pass





