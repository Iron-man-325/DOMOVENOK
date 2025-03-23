let frame = document.getElementById('img_preview');

function preview(input) {
    frame.src = URL.createObjectURL(input.files[0]);
}

function clearImage() {
    document.getElementById('formFile').value = null;
    frame.src = "";
}