// Given a string of 1 and 2, with sum of 12, draw the shape.
const drawSquareShape = (canvas_id, one_two_string, color_string = "", y_offset = 0) => {
    const canvas = document.getElementById(canvas_id);
    const ctx = canvas.getContext("2d");

    const drawEdge = (x1, y1, x2, y2, x3, y3, color) => {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x3, y3);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.stroke();
    };

    const drawCorner = (x1, y1, x2, y2, x3, y3, x4, y4, color) => {
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

    const centerX = 50, centerY = 50 + y_offset;
    const size = 30;
    const longSize = size * Math.cos(Math.PI / 12) / Math.cos(Math.PI / 4);

    const drawPiece = (start, type, color) => {
        if (type === '1') {
            drawEdge(
                centerX,
                centerY,
                centerX + size * Math.sin(start * Math.PI / 6),
                centerY - size * Math.cos(start * Math.PI / 6),
                centerX + size * Math.sin((start + 1) * Math.PI / 6),
                centerY - size * Math.cos((start + 1) * Math.PI / 6),
                color
            );
        } else {
            drawCorner(
                centerX,
                centerY,
                centerX + size * Math.sin(start * Math.PI / 6),
                centerY - size * Math.cos(start * Math.PI / 6),
                centerX + longSize * Math.sin((start + 1) * Math.PI / 6),
                centerY - longSize * Math.cos((start + 1) * Math.PI / 6),
                centerX + size * Math.sin((start + 2) * Math.PI / 6),
                centerY - size * Math.cos((start + 2) * Math.PI / 6),
                color
            );
        }
    };

    const colorMap = {
        w: "white",
        b: "black",
        y: "yellow"
    };

    let start = 0;
    for (let i = 0; i < one_two_string.length; i++) {
        const c = one_two_string.charAt(i);
        const color = color_string ? colorMap[color_string.charAt(i)] : "white";
        drawPiece(start, c, color);
        if (c === '1') {
            start += 1;
        } else {
            start += 2;
        }
    }
};

const drawTwoSquareShapes = (canvas_id, shape1_string, shape1_color, shape2_string, shape2_color) => {
    drawSquareShape(canvas_id, shape1_string, shape1_color, 0);
    drawSquareShape(canvas_id, shape2_string, shape2_color, 100);
};
