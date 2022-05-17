const btnClearCanvas = document.getElementById('btn-clear-canvas');
const paths = [];
const socket = io();
let deletedPaths = []
let currentPath = [];

paths.push(currentPath); // init for the first path

let width, height

function setup() {
    let canvas = createCanvas(512, 512)
    canvas.parent('sketch-canvas-container')

    // canvas.(commitCurrentPath)
    
    background(0);
    adaptCanvasSize()

    stroke("#FFFFFF")
    strokeWeight(1)
}

function draw() {
    background("#333333")
    noFill();

    if (mouseIsPressed) {
        if (mouseX < width && mouseY < height){
            const point = {
                x: mouseX,
                y: mouseY
                // color: colorInput.value,
                // weight: weight.value
            };
            currentPath.push(point);
        }
    }

    paths.forEach(path => {
        beginShape();
        path.forEach(point => {
            // stroke(point.color);
            // strokeWeight(point.weight);
            vertex(point.x, point.y);
        });
        endShape();
    });
}

function mouseReleased() {
    commitCurrentPath()
}

function commitCurrentPath() {
    socket.emit('new_path', JSON.stringify(currentPath));

    currentPath = [];
    paths.push(currentPath);

    // clean the stack for redo
    deletedPaths = []
}

function undo() {
    if(paths.length > 0){
        deletedPaths.push(paths.pop())
    }
}

function redo() {
    if(deletedPaths.length > 0){
        paths.push(deletedPaths.pop())
    }
}

document.addEventListener('keyup', function (event) {
    if (event.key == "z" && event.ctrlKey){
        undo()
    }
    if (event.key == "y" && event.ctrlKey){
        redo()
    }
    if (event.key == "z" && event.ctrlKey && event.shiftKey){
        redo()
    }
})

btnClearCanvas.addEventListener('click', () => {
    paths.splice(0);
    background(255);
});

function adaptCanvasSize(){
    width = document.getElementById('sketch-canvas-container').clientWidth;
    height = document.getElementById('sketch-canvas-container').clientHeight;
    resizeCanvas(width, height);
}

function windowResized() {
    adaptCanvasSize()
}
