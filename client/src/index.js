import * as THREE from 'three'
import Loader from './Loader'
import ViewerCore from './core/ViewerCore'
import { ViewMaterial } from './ViewMaterial'
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min'

let viewer

// Sizes
const sizes = {
    width: window.innerWidth,
    height: window.innerHeight
}

window.addEventListener('resize', () =>
{
    // Save sizes
    sizes.width = window.innerWidth
    sizes.height = window.innerHeight

    // Update camera
    camera.aspect = sizes.width / sizes.height
    camera.updateProjectionMatrix()

    // Update renderer
    renderer.setSize(sizes.width, sizes.height)
})

// Scene
const scene = new THREE.Scene()

// Camera
const camera = new THREE.PerspectiveCamera(75, sizes.width / sizes.height, 0.1, 100)
camera.position.z = 0.67
scene.add(camera)

const r = sizes.width / sizes.height

// cube
const cube0 = new THREE.Mesh(new THREE.PlaneGeometry(r/2, 1), new THREE.MeshNormalMaterial())
cube0.position.set(-r/3.95, 0, 0)
scene.add(cube0)
const cube1 = new THREE.Mesh(new THREE.PlaneGeometry(r/2, 1), new THREE.MeshNormalMaterial())
cube1.position.set(r/3.95, 0, 0)
scene.add(cube1)

// Renderer
const canvas = document.querySelector('.webgl')
const renderer = new THREE.WebGLRenderer({ antialias: true, canvas })
renderer.setPixelRatio(window.devicePixelRatio)
renderer.setSize(sizes.width, sizes.height)
renderer.setClearColor(0, 0)
renderer.outputColorSpace = THREE.SRGBColorSpace

let mousePress = false
window.addEventListener('mousedown', (e) => {
  mousePress = true
})
window.addEventListener('mouseup', (e) => {
  mousePress = false
})
window.addEventListener('mousemove', (event) => {
  if (mousePress) { updateBuffer() }
  // if (mousePress) { tick() }
})

function tick() {
  renderer.setRenderTarget(null)
  renderer.render(scene, camera)
}
tick()

const buffer0 = new THREE.WebGLRenderTarget(sizes.width / 2, sizes.height)
const buffer1 = new THREE.WebGLRenderTarget(sizes.width / 2, sizes.height)
const bufferArray = [ buffer0, buffer1 ]

cube0.material = new ViewMaterial()
cube1.material = new ViewMaterial()
cube0.material.uniforms.uTexture.value = bufferArray[0].texture
cube1.material.uniforms.uTexture.value = bufferArray[1].texture

init()

async function init() {
  const volumeMeta = await Loader.getVolumeMeta()
  const segmentMeta = await Loader.getSegmentMeta()

  viewer = new ViewerCore({ volumeMeta, segmentMeta, renderer })

  update()
}

async function update() {
  await Promise.all([modeA(viewer), modeC(viewer)])

  updateBuffer()
  updateGUI()
}

function updateBuffer() {
  const modeOrigin = viewer.params.mode

  viewer.params.mode = 'segment'
  renderer.setRenderTarget(bufferArray[0])
  renderer.clear()
  viewer.render()
  viewer.params.mode = 'volume-segment'
  renderer.setRenderTarget(bufferArray[1])
  renderer.clear()
  viewer.render()
  renderer.setRenderTarget(null)

  viewer.params.mode = modeOrigin
  tick()
}

let gui

function updateGUI() {
  const { mode } = viewer.params

  if (gui) { gui.destroy() }
  gui = new GUI()
  gui.add(viewer.params, 'mode', ['segment', 'volume-segment']).onChange(update)
  gui.add(viewer.params.layers, 'select', viewer.params.layers.options).name('layers').onChange(update)

  if (mode === 'segment') { return }
  if (mode === 'volume') { return }
  if (mode === 'volume-segment') {
    gui.add(viewer.params, 'surface', 0.001, 0.5).onChange(updateBuffer)
  }
  if (mode === 'layer') {
    const id = viewer.params.layers.select
    const clip = viewer.volumeMeta.nrrd[id].clip

    viewer.params.layer = clip.z
    gui.add(viewer.params, 'inverse').onChange(updateBuffer)
    gui.add(viewer.params, 'surface', 0.001, 0.5).onChange(updateBuffer)
    gui.add(viewer.params, 'layer', clip.z, clip.z + clip.d, 1).onChange(updateBuffer)
  }
  if (mode === 'grid layer') {
    gui.add(viewer.params, 'inverse').onChange(updateBuffer)
    gui.add(viewer.params, 'surface', 0.001, 0.5).onChange(updateBuffer)
  }
}

// segment mode
async function modeA(viewer) {
  viewer.clear()
  const segment = viewer.updateSegment()

  await segment.then(() => { console.log(`segment ${viewer.params.layers.select} is loaded`) })
}

// volume-segment mode
async function modeC(viewer) {
  viewer.clear()
  const volume = viewer.updateVolume()
  const segment = viewer.updateSegment()

  await Promise.all([volume, segment])
    .then(() => viewer.clipSegment())
    .then(() => viewer.updateSegmentSDF())
    .then(() => { console.log(`volume-segment ${viewer.params.layers.select} is loaded`) })
}



