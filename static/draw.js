var canvas;
var context;
var paint = false;
var clickX = [];
var clickY = [];
var clickDrag = [];

/**
 * Prepare the canvas for drawing.
 */
function drawCanvas() {
    canvas = document.getElementById('canvas');
    context = canvas.getContext('2d');

    $('#canvas').mousedown(function (e) {
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;

        paint = true;
        addClick(mouseX, mouseY);
        redraw();
    });

    $('#canvas').mousemove(function (e) {
        if (paint) {
            addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
            redraw();
        }
    });

    $('#canvas').mouseup(function () {
        paint = false;
    });
}

/**
 * Add mouse clicks to the click array.
 */
function addClick(x, y, dragging) {
    clickX.push(x);
    clickY.push(y);
    clickDrag.push(dragging);
}

/**
 * Redraw the canvas based on user input.
 */
function redraw() {
    context.clearRect(0, 0, canvas.width, canvas.height); // Clears the canvas
    context.strokeStyle = '#FF5733'; // Drawing color
    context.lineJoin = 'round';
    context.lineWidth = 3;

    for (var i = 0; i < clickX.length; i++) {
        context.beginPath();
        if (clickDrag[i] && i) {
            context.moveTo(clickX[i - 1], clickY[i - 1]);
        } else {
            context.moveTo(clickX[i] - 1, clickY[i]);
        }
        context.lineTo(clickX[i], clickY[i]);
        context.closePath();
        context.stroke();
    }
}

/**
 * Process the drawing, convert it to grayscale, resize it to 28x28, and send it to the server.
 */
function save() {
    var hiddenCanvas = document.createElement('canvas');
    var hiddenContext = hiddenCanvas.getContext('2d');

    // Resize to 28x28
    hiddenCanvas.width = 28;
    hiddenCanvas.height = 28;
    hiddenContext.drawImage(canvas, 0, 0, 28, 28);

    // Convert to grayscale
    var imgData = hiddenContext.getImageData(0, 0, 28, 28);
    for (var i = 0; i < imgData.data.length; i += 4) {
        let avg = (imgData.data[i] + imgData.data[i + 1] + imgData.data[i + 2]) / 3;
        imgData.data[i] = avg;
        imgData.data[i + 1] = avg;
        imgData.data[i + 2] = avg;
    }
    hiddenContext.putImageData(imgData, 0, 0);

    // Convert to base64 and send to server
    var url = hiddenCanvas.toDataURL();
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: url }),
    })
        .then((response) => response.json())
        .then((result) => {
            alert(`Prediction: ${result.prediction}`);
        })
        .catch((error) => console.error('Error:', error));
}
