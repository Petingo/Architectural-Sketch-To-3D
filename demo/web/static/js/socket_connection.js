const socket = io()

let sketchId = undefined
let uid = undefined

let btnShowUid = document.getElementById('btn-show-uid')
btnShowUid.onclick = () => {
    alert(uid)
}


socket.on('assign_id', data => {
    sketchId = data.sketch_id
    uid = data.uid
})