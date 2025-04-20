// Start from left face, in row order then column order.
// Then bottom face, then right face.
// e.g. g,gbr,rbrbg;...
const renderPyraminx = (canvas_id, color_string) => {
    const canvas = document.getElementById(canvas_id);
    const ctx = canvas.getContext("2d");

    const side = 50; // Side length of the large triangle
    const levels = 3; // Divide each face into 3 layers (total of 9 small triangles per face)
    const smallSide = side / levels; // Side length of small equilateral triangles

    const centerX = canvas.width / 2;
    const centerY = canvas.height * 2 / 3;

    const colorMap = {
        'r': '#ff0000', // Red
        'b': '#0000ff', // Blue
        'g': '#00ff00', // Green
        'y': '#ffff00', // Yellow
        ' ': '#a9a9a9'  // Dark Grey
    };

    ctx.lineWidth = 1;
    ctx.strokeStyle = "#333";

    function parseColorString(color_string) {
        const colors = [];
        const rows = color_string.split(';');
        for (let f = 0; f < 3; f++) {
            const face = rows[f].split(',');
            const faceColors = [];
            for (let j = 0; j < 3; j++) {
                const rowColors = face[j].split('');
                faceColors.push(rowColors.reverse());
            }
            colors.push(faceColors);
        }
        // Reverse the order of the faces
        return [colors[2], colors[1], colors[0]];
    }

    // Utility function to draw a triangle given three points and color
    function drawTriangle(p1, p2, p3, color) {
        ctx.beginPath();
        ctx.moveTo(p1[0], p1[1]);
        ctx.lineTo(p2[0], p2[1]);
        ctx.lineTo(p3[0], p3[1]);
        ctx.closePath();
        ctx.fillStyle = colorMap[color];
        ctx.fill();
        ctx.stroke();
    }

    // Convert grid coordinates to canvas coordinates for small triangles
    function gridToCanvas(i, j) {
        const x = centerX + (j - i / 2) * smallSide * 3;
        const y = centerY - i * (Math.sqrt(3) / 2) * smallSide;
        return [x, y];
    }

    // Rotate points to fit the 120-degree triangle sections
    function rotatePoint([x, y], angle) {
        const dx = x - centerX;
        const dy = y - centerY;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const rx = dx * cos - dy * sin + centerX;
        const ry = dx * sin + dy * cos + centerY;
        return [rx, ry];
    }

    // Draw the entire Pyraminx structure
    function drawPyraminx(color_string) {
        const colors = parseColorString(color_string);
        // Angles for the 3 faces (120°, 240°, 360°) in a circular layout
        const angles = [0, Math.PI * 2 / 3, Math.PI * 4 / 3];

        // Draw each face (120° isosceles triangle)
        for (let face = 0; face < 3; face++) {
            const angle = angles[face] + Math.PI * 1 / 3;

            // Draw the 9 small triangles for each face (3 layers of triangles)
            for (let row = 0; row < levels; row++) {
                let color_index = 0;
                for (let col = 0; col <= row; col++) {
                    // Upward triangle
                    const p1 = rotatePoint(gridToCanvas(row, col), angle);
                    const p2 = rotatePoint(gridToCanvas(row + 1, col), angle);
                    const p3 = rotatePoint(gridToCanvas(row + 1, col + 1), angle);
                    drawTriangle(p1, p2, p3, colors[face][row][color_index]);
                    color_index++;

                    // Downward triangle (for the interior of the grid)
                    if (col < row) {
                        const q1 = rotatePoint(gridToCanvas(row, col), angle);
                        const q2 = rotatePoint(gridToCanvas(row + 1, col + 1), angle);
                        const q3 = rotatePoint(gridToCanvas(row, col + 1), angle);
                        drawTriangle(q1, q2, q3, colors[face][row][color_index]);
                        color_index++;
                    }
                }
            }
        }
    }

    // Call the function to draw the Pyraminx
    drawPyraminx(color_string);
};