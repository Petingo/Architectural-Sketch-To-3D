import * as THREE from 'three'
import { OrbitControls } from 'OrbitControls';
import { OBJLoader } from 'OBJLoader'

let btnGen3d = document.getElementById('btn-gen-3d')
function gen3d(){
    console.log("gen3d")
    if(paths.length > 0){
        socket.emit("gen_3d")
    } else {
        alert("No image to generate 3d model")
    }
}
btnGen3d.onclick = gen3d

// Ref: https://stackoverflow.com/questions/18357529/threejs-remove-object-from-scene
// function removeObject3D(object3D) {
//     if (!(object3D instanceof THREE.Object3D)) return false;

//     // for better memory management and performance
//     object3D.geometry.dispose();
//     if (object3D.material instanceof Array) {
//         // for better memory management and performance
//         object3D.material.forEach(material => material.dispose());
//     } else {
//         // for better memory management and performance
//         object3D.material.dispose();
//     }
//     object3D.removeFromParent(); // the parent might be the scene or another Object3D, but it is sure to be removed this way
//     return true;
// }

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

// objLoder.load(
//     "objs/monkey.obj",
//     function(obj){
//         scene.add(obj)
//     },
//     function(xhr){
//         console.log((xhr.loaded / xhr.total * 100) + "% loaded")
//     },
//     function(err){
//         console.log("load error")
//     }
// )

// function animate() {
//     requestAnimationFrame(animate)
//     controls.update()
//     render()
//     // stats.update()
// }

// function render() {
//     renderer.render(scene, camera)
// }

// animate()

let prevObj

socket.on('update_3d', data => {
    sketchId = data.sketch_id
    console.log("loading ", `objs/${sketchId}.obj`)
    objLoder.load(
        `objs/${sketchId}.obj`,
        function(obj){
            console.log(obj)
            if(prevObj){
                scene.remove(prevObj)
            }
            prevObj = obj 
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
    }
    
    function render() {
        renderer.render(scene, camera)
    }
    
    animate()
})


