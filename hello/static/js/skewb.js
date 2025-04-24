const drawSkewb = (canvas_id, colors) => {
    const color_map = {
        'r': 'red',
        'b': 'blue',
        'g': 'green',
        'w': 'white',
        'y': 'yellow',
        'o': 'orange',
        'p': 'purple',
        ' ': 'gray',
    };

    const canvas = document.getElementById(canvas_id);
    const ctx = canvas.getContext("2d");

    const drawTriangle = (x1, y1, x2, y2, x3, y3, color) => {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x3, y3);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.stroke();
    };

    const drawSquare = (x1, y1, x2, y2, x3, y3, x4, y4, color) => {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x3, y3);
        ctx.lineTo(x4, y4);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.stroke();
    };

    const centerX = 150, centerY = 100;
    const size = 70;

    drawTriangle(centerX, centerY - size, centerX - size * 23 / 50, centerY - size * 35 / 50, centerX + size * 23 / 50, centerY - size * 35 / 50, color_map[colors[0]]);
    drawTriangle(centerX + size * 41 / 50, centerY - size * 23 / 50, centerX + size * 23 / 50, centerY - size * 35 / 50, centerX + size * 23 / 50, centerY - size * 12 / 50, color_map[colors[1]]);
    drawTriangle(centerX, centerY, centerX + size * 23 / 50, centerY - size * 12 / 50, centerX - size * 23 / 50, centerY - size * 12 / 50, color_map[colors[2]]);
    drawTriangle(centerX - size * 23 / 50, centerY - size * 12 / 50, centerX - size * 41 / 50, centerY - size * 23 / 50, centerX - size * 23 / 50, centerY - size * 35 / 50, color_map[colors[3]]);
    drawSquare(centerX - size * 23 / 50, centerY - size * 35 / 50, centerX + size * 23 / 50, centerY - size * 35 / 50, centerX + size * 23 / 50, centerY - size * 12 / 50, centerX - size * 23 / 50, centerY - size * 12 / 50, color_map[colors[4]]);

    drawTriangle(centerX - size * 82 / 50, centerY - size * 46 / 50, centerX - size * 61 / 50, centerY - size * 34 / 50, centerX - size * 82 / 50, centerY - size * 23 / 50, color_map[colors[5]]);
    drawTriangle(centerX - size * 61 / 50, centerY - size * 34 / 50, centerX - size * 41 / 50, centerY - size * 23 / 50, centerX - size * 41 / 50, centerY, color_map[colors[6]]);
    drawTriangle(centerX - size * 41 / 50, centerY, centerX - size * 41 / 50, centerY + size * 23 / 50, centerX - size * 61 / 50, centerY + size * 12 / 50, color_map[colors[7]]);
    drawTriangle(centerX - size * 61 / 50, centerY + size * 12 / 50, centerX - size * 82 / 50, centerY, centerX - size * 82 / 50, centerY - size * 23 / 50, color_map[colors[8]]);
    drawSquare(centerX - size * 61 / 50, centerY - size * 34 / 50, centerX - size * 41 / 50, centerY, centerX - size * 61 / 50, centerY + size * 12 / 50, centerX - size * 82 / 50, centerY - size * 23 / 50, color_map[colors[9]]);

    drawTriangle(centerX - size * 41 / 50, centerY - size * 23 / 50, centerX - size * 23 / 50, centerY - size * 12 / 50, centerX - size * 41 / 50, centerY, color_map[colors[10]]);
    drawTriangle(centerX - size * 23 / 50, centerY - size * 12 / 50, centerX, centerY, centerX, centerY + size * 23 / 50, color_map[colors[11]]);
    drawTriangle(centerX, centerY + size * 23 / 50, centerX, centerY + size * 46 / 50, centerX - size * 23 / 50, centerY + size * 34 / 50, color_map[colors[12]]);
    drawTriangle(centerX - size * 23 / 50, centerY + size * 34 / 50, centerX - size * 41 / 50, centerY + size * 23 / 50, centerX - size * 41 / 50, centerY, color_map[colors[13]]);
    drawSquare(centerX - size * 23 / 50, centerY - size * 12 / 50, centerX, centerY + size * 23 / 50, centerX - size * 23 / 50, centerY + size * 34 / 50, centerX - size * 41 / 50, centerY, color_map[colors[14]]);

    drawTriangle(centerX + size * 23 / 50, centerY - size * 12 / 50, centerX, centerY, centerX, centerY + size * 23 / 50, color_map[colors[15]]);
    drawTriangle(centerX + size * 41 / 50, centerY - size * 23 / 50, centerX + size * 23 / 50, centerY - size * 12 / 50, centerX + size * 41 / 50, centerY, color_map[colors[16]]);
    drawTriangle(centerX + size * 23 / 50, centerY + size * 34 / 50, centerX + size * 41 / 50, centerY + size * 23 / 50, centerX + size * 41 / 50, centerY, color_map[colors[17]]);
    drawTriangle(centerX, centerY + size * 23 / 50, centerX, centerY + size * 46 / 50, centerX + size * 23 / 50, centerY + size * 34 / 50, color_map[colors[18]]);
    drawSquare(centerX + size * 23 / 50, centerY - size * 12 / 50, centerX, centerY + size * 23 / 50, centerX + size * 23 / 50, centerY + size * 34 / 50, centerX + size * 41 / 50, centerY, color_map[colors[19]]);

    drawTriangle(centerX + size * 61 / 50, centerY - size * 34 / 50, centerX + size * 41 / 50, centerY - size * 23 / 50, centerX + size * 41 / 50, centerY, color_map[colors[20]]);
    drawTriangle(centerX + size * 82 / 50, centerY - size * 46 / 50, centerX + size * 61 / 50, centerY - size * 34 / 50, centerX + size * 82 / 50, centerY - size * 23 / 50, color_map[colors[21]]);
    drawTriangle(centerX + size * 61 / 50, centerY + size * 12 / 50, centerX + size * 82 / 50, centerY, centerX + size * 82 / 50, centerY - size * 23 / 50, color_map[colors[22]]);
    drawTriangle(centerX + size * 41 / 50, centerY, centerX + size * 41 / 50, centerY + size * 23 / 50, centerX + size * 61 / 50, centerY + size * 12 / 50, color_map[colors[23]]);
    drawSquare(centerX + size * 61 / 50, centerY - size * 34 / 50, centerX + size * 41 / 50, centerY, centerX + size * 61 / 50, centerY + size * 12 / 50, centerX + size * 82 / 50, centerY - size * 23 / 50, color_map[colors[24]]);
};
