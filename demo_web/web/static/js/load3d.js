import * as THREE from 'three'
import { OrbitControls } from 'OrbitControls';
import { OBJLoader } from 'OBJLoader'

console.log(THREE)
console.log(OBJLoader)

function getContainerWH(){
    let width = document.getElementById('model-container').clientWidth;
    let height = document.getElementById('model-container').clientHeight;
    return [width, height]
}

function adaptRendererSize(){
    let [width, height] = getContainerWH()
    
    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)
}

function windowResized() {
    adaptRendererSize()
}

const modelContainer = document.getElementById("model-container")

const scene = new THREE.Scene();
// scene.add(new THREE.AxesHelper(5))

let [width, height] = getContainerWH()
const camera = new THREE.PerspectiveCamera( 75, width / height, 0.1, 1000 );
camera.position.z = 5;

let lightList = [[0, 0, 50], [0, 0, -50], [0, 50, 0], [50, 0, 0], [-50, 0, 0]]
for (let lightPosition of lightList) {
    console.log(lightPosition)
    let light = new THREE.PointLight(0xffffff, 0.5)
    light.position.set(lightPosition[0], lightPosition[1], lightPosition[2])
    scene.add(light)
}

const renderer = new THREE.WebGLRenderer();
renderer.setClearColor( 0x333333, 0);
adaptRendererSize()
modelContainer.appendChild( renderer.domElement );

const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true

const objLoder = new OBJLoader();

objLoder.load(
    "models/monkey.obj",
    function(obj){
        scene.add(obj)
    },
    function(xhr){
        console.log((xhr.loaded / xhr.total * 100) + "% loaded")
    },
    function(err){
        console.log("load error")
    }
)

function animate() {
    requestAnimationFrame(animate)
    controls.update()
    render()
    stats.update()
}

function render() {
    renderer.render(scene, camera)
}

animate()