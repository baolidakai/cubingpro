const render = (clocks, flip, adjuster_id, canvas_id, text_matrix = null, change_pin = null) => {
    const elmAdjuster = document.getElementById(adjuster_id);
    const elmCanvas = document.getElementById(canvas_id);
    const ctx = elmCanvas.getContext("2d");

    const width = elmAdjuster.clientWidth;
    const height = width / 2;

    const dpr = window.devicePixelRatio;
    if (elmCanvas.width != "" + width * dpr) {
        elmCanvas.width = "" + width * dpr;
    }
    if (elmCanvas.height != "" + height * dpr) {
        elmCanvas.height = "" + height * dpr;
    }
    ctx.save();
    ctx.scale(dpr, dpr);
    elmCanvas.style.width = `${width}px`;
    elmCanvas.style.height = `${height}px`;

    ctx.clearRect(0, 0, width, height);

    for (let f = 0; f < 2; f++) {
        ctx.save();
        ctx.scale(height, height);
        ctx.translate(f, 0);

        // 52 mm
        ctx.translate(.05, .05);
        ctx.scale(.9, .9);

        ctx.beginPath();
        ctx.arc(.5, .5, .5, 0, 2 * Math.PI);
        if (f == 0) {
            ctx.fillStyle = "#444";
            ctx.fill();
        } else {
            ctx.lineWidth = 1 / height / .9;
            ctx.strokeStyle = "#aaa";
            ctx.stroke();
        }

        for (let y = 0; y < 2; y++) {
            for (let x = 0; x < 2; x++) {
                ctx.beginPath();
                // 30 mm, 3.35 mm
                ctx.arc(x * .29 + .355, y * .29 + .355, .032, 0, 2 * Math.PI);
                if (change_pin) {
                    ctx.fillStyle = (f == 0) ^ change_pin[f > 0 ? 1 - y : y][x] ? "#fff" : "#111";
                } else {
                    ctx.fillStyle = f == 0 ? "#fff" : "#111";
                }
                ctx.fill();
            }
        }

        for (let y = 0; y < 3; y++) {
            for (let x = 0; x < 3; x++) {
                ctx.save();

                // 30 mm, 14.5 mm
                ctx.translate(x * .29 + .065 + .005, y * .29 + .065 + .005);
                ctx.scale(.28, .28);

                ctx.beginPath();
                ctx.arc(.5, .5, .5, 0, 2 * Math.PI);
                ctx.fillStyle = f == 0 ? "#111" : "#fff";
                ctx.fill();

                if (f == 1) {
                    ctx.beginPath();
                    ctx.arc(.5, .5, .5, 0, 2 * Math.PI);
                    ctx.lineWidth = 1 / height / .9 / .28;
                    ctx.strokeStyle = "#ccc";
                    ctx.stroke();
                }

                for (let i = 0; i < 12; i++) {
                    ctx.save();
                    ctx.translate(.5, .5);
                    ctx.rotate(i / 12 * 2 * Math.PI);

                    if (
                        flip == "y2" && i == 0 ||
                        flip == "x2" && f == 0 && i == 0 ||
                        flip == "x2" && f == 1 && i == 6
                    ) {
                        ctx.fillStyle = "#c22";
                        ctx.fillRect(-.045, -.46, .03, .08);
                        ctx.fillRect(.015, -.46, .03, .08);
                    }
                    else if (i % 3 == 0) {
                        ctx.fillStyle = f == 0 ? "#fff" : "#111";
                        ctx.fillRect(-.015, -.46, .03, .08);
                    } else {
                        ctx.beginPath();
                        // 11.3 mm, 0.62 mm
                        ctx.arc(.0, -.40, .015, 0, 2 * Math.PI);
                        ctx.fillStyle = f == 0 ? "#fff" : "#111";
                        ctx.fill();
                    }

                    ctx.restore();
                }

                ctx.beginPath();
                // 10 mm
                ctx.arc(.5, .5, .34, 0, 2 * Math.PI);
                ctx.fillStyle = f == 0 ? "#fff" : "#111";
                ctx.fill();

                // Optionally, add a text.
                if (text_matrix && text_matrix.length > 0) {
                    ctx.translate(.1, .1);
                    ctx.font = "0.5px Arial";
                    ctx.fillStyle = "#c22";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(`${text_matrix[f][x][y]}`, 0.5, 0.5);
                    ctx.translate(-.1, -.1);
                }

                ctx.save();
                ctx.translate(.5, .5);
                let angle;
                if (f == 0) {
                    angle = clocks[0][y][x];
                } else {
                    if (flip == "y2") {
                        angle = clocks[1][y][x];
                    } else {
                        angle = clocks[1][2 - y][2 - x] + 6;
                    }
                }
                ctx.rotate(angle / 12 * 2 * Math.PI);

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-.05, -.13);
                ctx.lineTo(0, -.31);
                ctx.lineTo(.05, -.13);
                ctx.fillStyle = f == 0 ? "#111" : "#fff";
                ctx.fill();

                ctx.beginPath();
                ctx.arc(0, 0, .05, 0, 2 * Math.PI);
                ctx.fillStyle = f == 0 ? "#111" : "#fff";
                ctx.fill();

                ctx.restore();

                ctx.restore();
            }
        }

        ctx.restore();
    }
    ctx.restore();
};
const makeClocks = (scramble, operations) => {
    // [f, x, y]
    const T = [
        [[0, 1, 0], [0, 2, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0]], // UR
        [[0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 0, 2]], // DR
        [[0, 0, 1], [0, 1, 1], [0, 0, 2], [0, 1, 2], [1, 2, 2]], // DL
        [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [1, 2, 0]], // UL
        [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 0, 1], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 2, 0]], // U
        [[0, 1, 0], [0, 2, 0], [0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 0, 0], [1, 0, 2]], // R
        [[0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 0, 2], [0, 1, 2], [0, 2, 2], [1, 0, 2], [1, 2, 2]], // D
        [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [0, 0, 2], [0, 1, 2], [1, 2, 0], [1, 2, 2]], // L
        [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 0, 2], [0, 1, 2], [0, 2, 2], [1, 0, 0], [1, 2, 0], [1, 0, 2], [1, 2, 2]], // ALL
    ];

    const clocks = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]];

    for (let i = 0; i < 14; i++) {
        for (const t of T[i < 9 ? i : i - 9 + 4]) {
            let [f, x, y] = t;
            let angle = scramble[i];
            if (i < 9) {
                f = 1 - f;
                angle = -angle;
            }
            if (f == 1) {
                angle = -angle;
            }
            clocks[f][y][x] += angle;
        }
    }

    // [f, x, y]
    if (operations.length === 14) {
        const T_op = [
            // ur
            [[0, 2, 0], [0, 0, 2], [0, 2, 2], [1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1], [1, 2, 1], [1, 0, 2], [1, 1, 2], [1, 2, 2]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [1, 2, 0]],
            // L
            [[0, 2, 0], [0, 2, 2], [1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1], [1, 0, 2], [1, 1, 2]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [0, 0, 2], [0, 1, 2], [1, 2, 0], [1, 2, 2]],
            // UL
            [[0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 0, 2], [0, 1, 2], [0, 2, 2], [1, 2, 0], [1, 0, 2], [1, 2, 2]],
            // x2
            // ur
            [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 0, 0], [1, 2, 0], [1, 0, 2]],
            [[0, 0, 2], [1, 1, 1], [1, 2, 1], [1, 1, 2], [1, 2, 2]],
            // L
            [[0, 1, 0], [0, 2, 0], [0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 0, 0], [1, 0, 2]],
            [[0, 0, 0], [0, 0, 2], [1, 1, 0], [1, 2, 0], [1, 1, 1], [1, 2, 1], [1, 1, 2], [1, 2, 2]],
            // UL
            [[0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 0, 2]],
            [[0, 0, 0], [0, 2, 0], [0, 0, 2], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 0, 1], [1, 1, 1], [1, 2, 1], [1, 1, 2], [1, 2, 2]],
            // \
            [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 1, 2], [0, 2, 2], [1, 2, 0], [1, 0, 2]],
            [[0, 2, 0], [0, 0, 2], [1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1], [1, 2, 1], [1, 1, 2], [1, 2, 2]],
        ];
        for (let i = 0; i < 14; i++) {
            for (const t of T_op[i]) {
                let [f, x, y] = t;
                let angle = operations[i];
                f = 1 - f;
                if (i >= 6) {
                    angle = -angle;
                }
                if (f == 1) {
                    angle = -angle;
                }
                clocks[f][y][x] += angle;
            }
        }
    }

    for (let f = 0; f < 2; f++) {
        for (let y = 0; y < 3; y++) {
            for (let x = 0; x < 3; x++) {
                clocks[f][y][x] = (clocks[f][y][x] % 12 + 12) % 12;
            }
        }
    }

    return clocks;
};

const convert_to_matrix = (str) => {
    if (!str) {
        return null;
    }
    const flatArray = str.split(',');
    const matrix = [[], []];
    for (let f = 0; f < 2; f++) {
        for (let i = 0; i < 3; i++) {
            matrix[f].push(flatArray.slice(f * 9 + i * 3, f * 9 + i * 3 + 3));
        }
    }
    return matrix;
};

const convert_to_change_pin_matrix = (str) => {
    if (!str) {
        return null;
    }
    const flatArray = str.split(',');
    const matrix = [];
    for (let i = 0; i < 2; i++) {
        matrix.push(flatArray.slice(i * 2, i * 2 + 2));
    }
    return matrix;
};
