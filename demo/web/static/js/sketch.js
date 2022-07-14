const btnClearCanvas = document.getElementById('btn-clear-canvas');
const btnUndo = document.getElementById('btn-undo');
const btnRedo = document.getElementById('btn-redo');
let paths = [];

let canvas
let deletedPaths = []
let currentPath = [];

let mouseIsPressedOnCanvas = false

paths.push(currentPath); // init for the first path

let width, height

function setup() {
    canvas = createCanvas(512, 512)
    canvas.parent('sketch-canvas-container')
    
    canvas.mousePressed(()=>{ mouseIsPressedOnCanvas = true })
    canvas.mouseReleased(()=>{ mouseIsPressedOnCanvas = false })

    // canvas.(commitCurrentPath)
    
    background(0);
    adaptCanvasSize()

    stroke("#FFFFFF")
    strokeWeight(1)
}



function draw() {
    background("#333333")
    noFill();

    // if (mouseIsPressed && mouseIsPressedOnCanvas) {
    //     if (mouseX < width && mouseY < height){
    //         // const point = {
    //         //     x: mouseX,
    //         //     y: mouseY
    //         //     // color: colorInput.value,
    //         //     // weight: weight.value
    //         // };
    //         const point = [mouseX, mouseY]
            
    //         if (currentPath.length == 0 ||
    //             (mouseX != currentPath[currentPath.length - 1][0] && mouseY != currentPath[currentPath.length - 1][1])) {

    //             currentPath.push(point);
    //         }
    //     }
    // }

    paths.forEach(path => {
        beginShape();
        path.forEach(point => {
            // stroke(point.color);
            // strokeWeight(point.weight);
            vertex(point[0], point[1]);
        });
        endShape();
    });
}

function mouseDragged(){
    console.log("Dragged", mouseX, mouseY)
    if (mouseX < width && mouseY < height){
        // const point = {
        //     x: mouseX,
        //     y: mouseY
        //     // color: colorInput.value,
        //     // weight: weight.value
        // };
        const point = [mouseX, mouseY]
        
        if (currentPath.length == 0 ||
            (mouseX != currentPath[currentPath.length - 1][0] && mouseY != currentPath[currentPath.length - 1][1])) {

            currentPath.push(point);
        }
    }
}

function mouseReleased() {
    commitCurrentPath()
}

function commitCurrentPath() {
    if (currentPath.length == 0) {
        return
    }
    
    let data = JSON.stringify({path: currentPath})
    console.log(data)
    socket.emit('new_path', data);

    currentPath = [];
    paths.push(currentPath);

    // clean the stack for redo
    deletedPaths = []
}

function undo() {
    if(paths.length > 0){
        socket.emit('undo')
        poppedPath = paths.pop()
        if(poppedPath.length > 0){
            deletedPaths.push(poppedPath)
        } else {
            deletedPaths.push(paths.pop())
            currentPath = []
            paths.push(currentPath)
        }
    }
}

function redo() {
    if(deletedPaths.length > 0){
        socket.emit('redo')
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
    socket.emit('clear_canvas')
    
    paths = [];
    deletedPaths = []
    currentPath = [];
    paths.push(currentPath);

    background(255)
});

btnRedo.addEventListener('click', () => {
    redo()
});

btnUndo.addEventListener('click', () => {
    undo()
});

function adaptCanvasSize(){
    width = document.getElementById('sketch-canvas-container').clientWidth;
    height = document.getElementById('sketch-canvas-container').clientHeight;
    resizeCanvas(width, height);
}

function windowResized() {
    adaptCanvasSize()
}
