"""Python translation of https://github.com/qqwref/sq1opt/blob/master/README.md.

Guidance for developers:
For the first time, the solver will cold start and compute some intermediate tables and materialize to dat files. But starting from the first time, the solver will
warm start and load information from those dat files directly to save computation. So you should expect some delay when you run this program for the first time. On your hosted server, these dat table should be uploaded so the computation is faster.
Another optimization is PositionSolver needs to be initialized once which takes a long time, but it can take subsequent calls quickly.
Even with those optimizations, solving a single case takes more than 10 seconds when it involves parity. So I recommend not to host a synchronous solver with this program, but rather use it to batch generate
algorithms for many cases as an async process without strict SLO requirement, e.g. when you build a trainer of algorithm set, you may use this solver to generate scrambles for those cases.
You may also serve this as a SQ-1 explorer online, but warn the users on the potential slowness.

Guidance for users:
Usage:
python jaap.py A1B2C3D45E6F7G8H-

A1B2C3D45E6F7G8H- is the solved position. Letters represent corners, numbers the edges, starting from the front seam clockwise around the top layer and
then clockwise around the bottom layer. Optionally, the middle layer is denoted by a - for a square and / for kite shape.

So the solved state looks like:
Top Layer
--------------
| \       /  |
|B \  2  / C |
|___\   /____|
| 1        3 |
|___/   \____|
|A /  4  \ D |
| /       \  |
--------------
Bottom Layer
--------------
| \       /  |
|H \  5  / E |
|___\   /____|
| 8        6 |
|___/   \____|
|G /  7  \ F |
| /       \  |
--------------

e.g.
python jaap.py A1B2C4D38E6F7G5H-
Solves the parity:
python jaap.py A1B2C4D35E6F7G8H/

Ideal for Apps using Python web frameworks (e.g. Django/Flask) and trying to build a SQ-1 solver.

Credits to ChatGPT which did all the translation work.

Unfinished part: In the main function, didn't handle the flag parsing. Partial solution not copied. But these two are easy to add.
"""
import sys
import time
import os
import struct
import random

NUMHALVES = 13
NUMLAYERS = 158
NUMSHAPES = 7356
FILESTT = "sq1stt.dat"
FILESCTE = "sq1scte.dat"
FILESCTC = "sq1sctc.dat"
FILEP1U = "sq1p1u.dat"
FILEP2U = "sq1p2u.dat"
FILEP1W = "sq1p1w.dat"
FILEP2W = "sq1p2w.dat"
FILEP1A = "sq1p1a.dat"
FILEP2A = "sq1p2a.dat"

TURN_METRIC = 0
TWIST_METRIC = 1
ANGLE_METRIC = 2

errors = [
    "Unrecognised command line switch.",       # 1
    "Too many command line arguments.",
    "Input file not found.",                     # 3
    "Bracket ) expected.",                       # 4
    "Bottom layer turn expected.",              # 5
    "Comma expected.",                           # 6
    "Top layer turn expected.",                  # 7
    "Bracket ( expected.",                       # 8
    "Position should be 16 or 17 characters.",  # 9
    "Expected A-H or 1-8.",                      # 10
    "Expected - or /.",                          # 11
    "Twist is blocked by corner.",               # 12
    "Can't parse input as position string or movelist.",  # 13
    "Unexpected bracket (.",                      # 14
    "Number expected.",                           # 15
    "Twist / expected.",                          # 16
    "Position string has too many copies of a piece.",   # 17
    "Can't stay in cube shape and also use 2gen.",       # 18
    "Position can't be solved with these constraints",   # 19
]

KARNOTATION_LEN = 109
KARNOTATION = [
    ["U", "3,0"],
    ["U'", "9,0"],
    ["U2", "6,0"],
    ["D", "0,3"],
    ["D'", "0,9"],
    ["D2", "0,6"],
    ["u", "2,&"],
    ["u'", "^,1"],
    ["d", "&,2"],
    ["d'", "1,^"],
    ["E", "3,9"],
    ["E'", "9,3"],
    ["e", "3,3"],
    ["e'", "9,9"],
    ["F", "4,1"],
    ["F'", "8,&"],
    ["f", "1,4"],
    ["f'", "&,8"],
    ["M", "1,1"],
    ["M'", "&,&"],
    ["m", "2,2"],
    ["m'", "^,^"],
    ["u2", "5,&"],
    ["u2'", "7,1"],
    ["d2", "&,5"],
    ["d2'", "1,7"],
    ["T", "2,8"],
    ["T'", "^,4"],
    ["t", "4,^"],
    ["t'", "8,2"],
    ["W ", "3,0/9,0/"],
    ["W' ", "9,0/3,0/"],
    ["B ", "0,3/0,9/"],
    ["B' ", "0,9/0,3/"],
    ["w ", "2,&/^,1/"],
    ["w' ", "^,1/2,&/"],
    ["b ", "&,2/1,^/"],
    ["b' ", "1,^/&,2/"],
    ["E\\ ", "3,0/0,9/"],
    ["E\\' ", "9,0/0,3/"],
    ["e\\ ", "3,0/0,3/"],
    ["e\\' ", "9,0/0,9/"],
    ["F2 ", "4,1/8,&/"],
    ["F2' ", "8,&/4,1/"],
    ["f2 ", "1,4/&,8/"],
    ["f2' ", "&,8/1,4/"],
    ["U3 ", "3,0/9,0/3,0/"],
    ["U3' ", "9,0/3,0/9,0/"],
    ["D3 ", "0,3/0,9/0,3/"],
    ["D3' ", "0,9/0,3/0,9/"],
    ["u3 ", "2,&/^,1/2,&/"],
    ["u3' ", "^,1/2,&/^,1/"],
    ["u4 ", "2,&/^,1/2,&/^,1/"],
    ["u4' ", "^,1/2,&/^,1/2,&/"],
    ["d3 ", "&,2/1,^/&,2/"],
    ["d3' ", "1,^/&,2/1,^/"],
    ["d4", "&,2/1,^/&,2/&,2"],
    ["d4' ", "1,^/&,2/1,^/&,2/"],
    ["UU", "1,0/5,&/9,0/1,1/9,0/&,0"],
    ["UU'", "1,0/2,&/1,1/2,&/7,1/&,0"],
    ["FV", "0,&/1,^/&,2/1,^/&,2/0,1"],
    ["VF", "1,0/2,&/^,1/2,&/^,1/&,0"],
    [" JJ ", "/0,9/3,3/9,0/"],
    [" jJ ", "/0,9/3,3/9,0/"],
    [" Jj ", "/0,9/3,3/9,0/"],
    [" jj ", "/0,9/3,3/9,0/"],
    [" bJJ ", "/9,0/3,3/0,9/"],
    [" bjJ ", "/9,0/3,3/0,9/"],
    [" bJj ", "/9,0/3,3/0,9/"],
    [" bjj ", "/9,0/3,3/0,9/"],
    [" JN ", "/0,9/0,3/0,9/0,3/"],
    [" jN ", "/0,9/0,3/0,9/0,3/"],
    [" Jn ", "/0,9/0,3/0,9/0,3/"],
    [" jn ", "/0,9/0,3/0,9/0,3/"],
    [" NN ", "/9,3/3,9/"],
    [" Nn ", "/9,3/3,9/"],
    [" nN ", "/9,3/3,9/"],
    [" nn ", "/9,3/3,9/"],
    [" NJ ", "/3,0/9,0/3,0/9,0/"],
    [" nJ ", "/3,0/9,0/3,0/9,0/"],
    [" Nj ", "/3,0/9,0/3,0/9,0/"],
    [" nj ", "/3,0/9,0/3,0/9,0/"],
    [" 3Adj ", "/3,0/&,&/^,1/"],
    [" 03Adj ", "/0,3/&,&/1,^/"],
    [" JR ", "/9,9/2,&/^,1/3,3/"],
    [" jR ", "/9,9/2,&/^,1/3,3/"],
    [" Jr ", "/9,9/1,^/&,2/3,3/"],
    [" jr ", "/9,9/1,^/&,2/3,3/"],
    [" RJ ", "/3,3/1,^/&,2/9,9/"],
    [" rJ ", "/3,3/2,&/^,1/9,9/"],
    [" Rj ", "/3,3/1,^/&,2/9,9/"],
    [" rj ", "/3,3/2,&/^,1/9,9/"],
    [" bRJ ", "/9,9/^,1/2,&/3,3/"],
    ["brJ ", "1,0/9,9/&,2/1,^/3,3/&,0/"],
    ["bRj ", "0,&/9,9/^,1/2,&/3,3/0,1/"],
    ["brj ", "1,&/9,9/&,2/1,^/3,3/&,1/"],
    ["RR ", "1,0/2,&/^,4/5,&/^,1/&,0/"],
    ["rr ", "0,&/^,1/5,&/^,4/2,&/0,1/"],
    ["pJ", "0&/^,1/2,2/0,9/0,1"],
    ["pj", "0,&/1,^/2,2/9,0/0,1"],
    ["pN", "1,0/2,8/^,4/&,0"],
    ["fpJ", "1,0/2,&/^,^/0,3/&,0"],
    ["AA ", "1,0/0,9/2,2/0,9/^,4/&,0/"],
    ["aa", "0&/1,^/2,2/1,^/8,2/0,1"],
    ["TT", "1,0/5,&/9,0/^,^/0,3/&,0"],    
    ["OppOpp", "1,0/&,&/6,0/1,1/&,0"],
    ["FF", "1,0/0,9/2,2/0,9/1,1/9,3/&,0"],
    ["M2", "1,0/&,&/0,1"],
    ["m2", "1,0/5,&/7,1/&,0"]
]

verbosity = 6
generator = False
usenegative = True
usebrackets = False
karnotation = False
metric = TURN_METRIC
maxX = 6
maxY = 6
maxTotal = 12

class HalfLayer:
    def __init__(self, p, t):
        self.pieces = p
        nEdges = 0
        m = 1
        for i in range(6):
            if (self.pieces & m) != 0:
                nEdges += 1
            m <<= 1
        self.nPieces = 3 + nEdges // 2
        self.turn = t


class Layer:
    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2
        self.pieces = (h1.pieces << 6) + h2.pieces
        self.nPieces = h1.nPieces + h2.nPieces

        m = 1
        self.turnt = 1
        while self.turnt < 6:
            if (h1.turn & h2.turn & m) != 0:
                break
            self.turnt += 1
            m <<= 1

        if self.turnt == 6:
            self.turnb = 6
        else:
            m = 1 << 4
            self.turnb = 1
            while self.turnb < 5:
                if (h1.turn & h2.turn & m) != 0:
                    break
                self.turnb += 1
                m >>= 1

        self.tpieces = self.pieces
        nEdges = 0
        for _ in range(self.turnt):
            if (self.tpieces & 1) != 0:
                self.tpieces += (1 << 12)
                nEdges += 1
            self.tpieces >>= 1

        self.turnParityOdd = ((self.nPieces & 1) == 0) and (((self.turnt + nEdges) & 2) != 0)

        self.bpieces = self.pieces
        nEdges = 0
        for _ in range(self.turnb):
            self.bpieces <<= 1
            if (self.bpieces & (1 << 12)) != 0:
                self.bpieces -= (1 << 12) - 1
                nEdges += 1

        self.turnParityOddb = ((self.nPieces & 1) == 0) and (((self.turnb + nEdges) & 2) != 0)

class Sq1Shape:
    def __init__(self, l1, l2, p):
        self.topl = l1       # reference to Layer object
        self.botl = l2       # reference to Layer object
        self.parityOdd = p
        self.pieces = (l1.pieces << 12) + l2.pieces

        self.tpieces = [0]*4
        self.tpieces[0] = (l1.tpieces << 12) + l2.pieces
        self.tpieces[1] = (l1.pieces << 12) + l2.bpieces
        self.tpieces[2] = (l1.h1.pieces << 18) + (l2.h1.pieces << 12) + (l1.h2.pieces << 6) + l2.h2.pieces

        # calculate mirrored shape (bit-reverse 24 bits)
        self.tpieces[3] = 0
        m = 1
        for i in range(24):
            self.tpieces[3] <<= 1
            if (self.pieces & m) != 0:
                self.tpieces[3] += 1
            m <<= 1

        self.tparity = [False]*4
        self.tparity[0] = self.parityOdd ^ l1.turnParityOdd
        self.tparity[1] = self.parityOdd ^ l2.turnParityOddb
        self.tparity[2] = self.parityOdd ^ ((l1.h2.nPieces & 1) != 0 and (l2.h1.nPieces & 1) != 0)
        self.tparity[3] = self.parityOdd

class ChoiceTable:
    def __init__(self):
        self.choice2Idx = [255] * 256  # Initialize all to 255
        self.idx2Choice = [0] * 70     # Will hold the valid combinations
        nc = 0
        for i in [1 << a for a in range(8) if (1 << a) < 255]:
            for j in [1 << b for b in range(8) if (1 << b) < 255 and (1 << b) > i]:
                for k in [1 << c for c in range(8) if (1 << c) < 255 and (1 << c) > j]:
                    for l in [1 << d for d in range(8) if (1 << d) < 255 and (1 << d) > k]:
                        total = i + j + k + l
                        self.choice2Idx[total] = nc
                        self.idx2Choice[nc] = total
                        nc += 1


class ShapeTranTable:
    def __init__(self):
        # attributes
        self.nShape = 0
        self.shapeList = [None] * NUMSHAPES  # will fill list of Sq1Shape
        # tranTable: a list-of-lists, dimension [NUMSHAPES][4]
        self.tranTable = [[0] * 4 for _ in range(NUMSHAPES)]
        self.hl = [None] * NUMHALVES   # HalfLayer list
        self.ll = [None] * NUMLAYERS   # Layer list

        # First, build list of possible halflayers
        hi = [0, 3, 12, 48, 9, 36, 33, 15, 39, 51, 57, 60, 63]
        ht = [42, 43, 46, 58, 45, 54, 53, 47, 55, 59, 61, 62, 63]
        for i in range(NUMHALVES):
            self.hl[i] = HalfLayer(hi[i], ht[i])

        # Build list of possible Layers
        lll = 0
        for i in range(NUMHALVES):
            for j in range(NUMHALVES):
                if (self.hl[i].nPieces + self.hl[j].nPieces) <= 10:
                    self.ll[lll] = Layer(self.hl[i], self.hl[j])
                    lll += 1

        # Build list of all possible shapes
        self.nShape = 0
        for i in range(lll):
            for j in range(lll):
                if self.ll[i].nPieces + self.ll[j].nPieces == 16:
                    self.shapeList[self.nShape] = Sq1Shape(self.ll[i], self.ll[j], True)
                    self.nShape += 1
                    self.shapeList[self.nShape] = Sq1Shape(self.ll[i], self.ll[j], False)
                    self.nShape += 1

        # Prepare transition table; attempt to read from file
        # We'll use Python file I/O and struct for binary read/write
        if not os.path.exists(FILESTT):
            # No file, compute table
            for i in range(self.nShape):
                for m in range(4):
                    for j in range(self.nShape):
                        if (self.shapeList[i].tpieces[m] == self.shapeList[j].pieces and
                            self.shapeList[i].tparity[m] == self.shapeList[j].parityOdd):
                            self.tranTable[i][m] = j
                            break
            # Save to file
            with open(FILESTT, "wb") as osf:
                for i in range(self.nShape):
                    for m in range(4):
                        # write as 32-bit integer little endian
                        osf.write(struct.pack("<i", self.tranTable[i][m]))
        else:
            # File exists, read it
            with open(FILESTT, "rb") as isf:
                # assume full table
                self.nShape = NUMSHAPES
                for i in range(self.nShape):
                    for m in range(4):
                        data = isf.read(4)
                        if not data:
                            raise IOError("Unexpected end of file reading tranTable")
                        (val,) = struct.unpack("<i", data)
                        self.tranTable[i][m] = val

    def __del__(self):
        # Python handles object deletion automatically; explicit cleanup not needed
        pass

    def getShape(self, s: int, p: bool) -> int:
        for i in range(self.nShape):
            if (self.shapeList[i].pieces == s and
                    self.shapeList[i].parityOdd == p):
                return i
        return -1

    def getTopTurn(self, s: int) -> int:
        return self.shapeList[s].topl.turnt

    def getBotTurn(self, s: int) -> int:
        return self.shapeList[s].botl.turnb

class ShapeColPos:
    def __init__(self, stt: ShapeTranTable, ct: ChoiceTable):
        self.stt = stt  # ShapeTranTable reference
        self.ct = ct    # ChoiceTable reference
        self.shapeIx = 0
        self.colouring = 0  # 24-bit int
        self.edgesFlag = False

    def set(self, shp: int, col: int, edges: bool):
        """
        col is 8-bit colouring of one type of piece.
        If edges is True, use edge colouring, else corner colouring.
        """
        c = self.ct.idx2Choice[col]
        self.shapeIx = shp
        self.edgesFlag = edges
        self.colouring = 0
        s = self.stt.shapeList[self.shapeIx].pieces

        if edges:
            m = 1
            n = 1
            for i in range(24):
                if s & m:
                    if c & n:
                        self.colouring |= m
                    n <<= 1
                m <<= 1
        else:
            m = 3
            n = 1
            i = 0
            while i < 24:
                if (s & m) == 0:
                    if c & n:
                        self.colouring |= m
                    n <<= 1
                    m <<= 1
                    i += 1
                m <<= 1
                i += 1

    def domove(self, m: int):
        botmask = (1 << 12) - 1
        topmask = (1 << 24) - (1 << 12)
        botrmask = (1 << 12) - (1 << 6)
        toprmask = (1 << 18) - (1 << 12)
        leftmask = botmask + topmask - botrmask - toprmask

        if m == 0:
            tn = self.stt.getTopTurn(self.shapeIx)
            b = self.colouring & botmask
            t = self.colouring & topmask
            t = (t + (t >> 12)) << (12 - tn)
            self.colouring = b + (t & topmask)

        elif m == 1:
            tn = self.stt.getBotTurn(self.shapeIx)
            b = self.colouring & botmask
            t = self.colouring & topmask
            b = (b + (b << 12)) >> (12 - tn)
            self.colouring = t + (b & botmask)

        elif m == 2:
            b = self.colouring & botrmask
            t = self.colouring & toprmask
            self.colouring = (self.colouring & leftmask) + (t >> 6) + (b << 6)

        self.shapeIx = self.stt.tranTable[self.shapeIx][m]

    def getColIdx(self) -> int:
        c = 0
        n = 1
        s = self.stt.shapeList[self.shapeIx].pieces

        if self.edgesFlag:
            m = 1
            for i in range(24):
                if s & m:
                    if self.colouring & m:
                        c |= n
                    n <<= 1
                m <<= 1
        else:
            m = 3
            i = 0
            while i < 24:
                if (s & m) == 0:
                    if self.colouring & m:
                        c |= n
                    n <<= 1
                    m <<= 1
                    i += 1
                m <<= 1
                i += 1

        return self.ct.choice2Idx[c]

class ShpColTranTable:
    def __init__(self, stt: ShapeTranTable, ct: ChoiceTable, edges: bool):
        self.stt = stt
        self.ct = ct
        self.edges = edges

        # Initialize a 3D list: [NUMSHAPES][70][3] filled with zeros
        self.tranTable = [[[0 for _ in range(3)] for _ in range(70)] for _ in range(NUMSHAPES)]

        filename = FILESCTE if edges else FILESCTC
        p = ShapeColPos(stt, ct)

        if not os.path.isfile(filename):
            # File doesn't exist, compute it
            for m in range(3):
                for i in range(NUMSHAPES):
                    for j in range(70):
                        p.set(i, j, edges)
                        p.domove(m)
                        col_idx = p.getColIdx()
                        self.tranTable[i][j][m] = col_idx
                        if col_idx == 255:
                            raise SystemExit("Col idx 255: error in getColIdx")
            # Save to file as binary
            with open(filename, "wb") as f:
                for i in range(NUMSHAPES):
                    for j in range(70):
                        f.write(bytes(self.tranTable[i][j]))
        else:
            # Load from file
            with open(filename, "rb") as f:
                raw = f.read(NUMSHAPES * 70 * 3)
                idx = 0
                for i in range(NUMSHAPES):
                    for j in range(70):
                        for m in range(3):
                            self.tranTable[i][j][m] = raw[idx]
                            idx += 1

class FullPosition:
    def __init__(self):
        self.pos = [0] * 24
        self.middle = 1
        self.reset()

    def reset(self):
        self.middle = 1
        s = "AAIBBJCCKDDLMEENFFOGGPHH"
        for i in range(24):
            self.pos[i] = ord(s[i]) - ord('A')

    def print(self):
        for i in range(24):
            if self.pos[i] < 0:
                print("UWV"[(-self.pos[i]) % 3], end="")
            elif self.pos[i] > 15:
                print("XYZ"[self.pos[i] % 3], end="")
            else:
                print("ABCDEFGH12345678"[self.pos[i]], end="")
            if self.pos[i] < 8:
                i += 1
        print("/ -"[self.middle + 1], end="")

    def random(self, twoGen, keepCubeShape):
        self.middle = -1 if (random.randint(0, 1) & 1) != 0 else 1
        while True:
            tmp = [0] * 16
            for i in range(8):
                tmp[2 * i + (1 if i > 3 else 0)] = i
                tmp[2 * i + (0 if i > 3 else 1)] = 8 + i

            if keepCubeShape:
                parity = False
                cornersToMix = 6 if twoGen == 1 else 8
                edgesToMix = 7 if twoGen == 1 else 8

                for i in range(cornersToMix):
                    j = i + random.randint(0, cornersToMix - i - 1)
                    a = 2 * i + (1 if i > 3 else 0)
                    b = 2 * j + (1 if j > 3 else 0)
                    tmp[a], tmp[b] = tmp[b], tmp[a]
                    if i != j:
                        parity ^= True

                for i in range(edgesToMix):
                    j = i + random.randint(0, edgesToMix - i - 1)
                    a = 2 * i + (0 if i > 3 else 1)
                    b = 2 * j + (0 if j > 3 else 1)
                    tmp[a], tmp[b] = tmp[b], tmp[a]
                    if i != j:
                        parity ^= True

                if parity:
                    tmp[0], tmp[2] = tmp[2], tmp[0]

            else:
                nToMix = 12 if twoGen == 2 else (13 if twoGen == 1 else 16)
                for i in range(nToMix):
                    j = random.randint(0, nToMix - i - 1)
                    tmp[i], tmp[i + j] = tmp[i + j], tmp[i]

            j = 0
            for i in range(16):
                self.pos[j] = tmp[i]
                j += 1
                if tmp[i] < 8:
                    self.pos[j] = tmp[i]
                    j += 1

            if twoGen == 1 and keepCubeShape:
                if not self.has2GenCorners():
                    self.pos[6] = self.pos[5]
                    continue

            if keepCubeShape:
                if (random.randint(0, 1) & 1) != 0:
                    tmp0 = self.pos[11]
                    for i in range(10, -1, -1):
                        self.pos[i + 1] = self.pos[i]
                    self.pos[0] = tmp0

                if (random.randint(0, 1) & 1) != 0:
                    tmp0 = self.pos[12]
                    for i in range(12, 23):
                        self.pos[i] = self.pos[i + 1]
                    self.pos[23] = tmp0

            elif twoGen == 1 and (random.randint(0, 1) & 1) != 0 and self.pos[11] != self.pos[12]:
                tmp0 = self.pos[12]
                for i in range(12, 23):
                    self.pos[i] = self.pos[i + 1]
                self.pos[23] = tmp0

            if self.pos[5] != self.pos[6] and self.pos[11] != self.pos[12] and self.pos[17] != self.pos[18] and self.pos[12] != self.pos[23]:
                break

    def set(self, p, m):
        for i in range(24):
            self.pos[i] = p[i]
        self.middle = m

    def doTop(self, m):
        m %= 12
        if m < 0:
            m += 12
        while m > 0:
            c = self.pos[11]
            for i in range(11, 0, -1):
                self.pos[i] = self.pos[i - 1]
            self.pos[0] = c
            m -= 1

    def doBot(self, m):
        m %= 12
        if m < 0:
            m += 12
        while m > 0:
            c = self.pos[23]
            for i in range(23, 12, -1):
                self.pos[i] = self.pos[i - 1]
            self.pos[12] = c
            m -= 1

    def doTwist(self):
        if not self.isTwistable():
            return False
        for i in range(6, 12):
            c = self.pos[i]
            self.pos[i] = self.pos[i + 6]
            self.pos[i + 6] = c
        self.middle = -self.middle
        return True

    def isTwistable(self):
        return (
            self.pos[0] != self.pos[11] and
            self.pos[5] != self.pos[6] and
            self.pos[12] != self.pos[23] and
            self.pos[17] != self.pos[18]
        )

    def getShape(self):
        s = 0
        m = 1 << 23
        for i in range(24):
            if self.pos[i] >= 8:
                s |= m
            m >>= 1
        return s
    
    def getParityOdd(self):
        p = False
        i = 0
        while i < 24:
            j = i
            while j < 24:
                if self.pos[j] < self.pos[i]:
                    p = not p
                if self.pos[j] < 8:
                    j += 1
                j += 1
            if self.pos[i] < 8:
                i += 1
            i += 1
        return p
    
    def getEdgeColouring(self, cl):
        clp = [
            [8, 9, 10, 11],
            [8, 9, 13, 14],
            [15, 14, 10, 9]
        ]
        c = 0
        cnt = 0
        m = (1 << 7) if cl != 2 else 1
        for i in range(24):
            if self.pos[i] >= 8:
                for j in range(4):
                    if self.pos[i] == clp[cl][j] or (self.pos[i] > 15 and self.pos[i] % 3 == 0 and cl == 0):
                        c |= m
                        cnt += 1
                        break
                if cl != 2:
                    m >>= 1
                else:
                    m <<= 1
        if cnt == 4:
            return c
        else:
            return -1

    def getCornerColouring(self, cl):
        clp = [
            [0, 1, 2, 3],
            [0, 1, 5, 6],
            [7, 6, 2, 1]
        ]
        c = 0
        cnt = 0
        m = (1 << 7) if cl != 2 else 1
        i = 0
        while i < 24:
            if self.pos[i] < 8:
                for j in range(4):
                    if self.pos[i] == clp[cl][j] or (self.pos[i] < 0 and self.pos[i] % 3 == 0 and cl == 0):
                        c |= m
                        cnt += 1
                        break
                if cl != 2:
                    m >>= 1
                else:
                    m <<= 1
                i += 2  # increment by 2 for corners since they appear twice in a row
            else:
                i += 1
        if cnt == 4:
            return c
        else:
            return -1
 
    def parseNumberForward(inp: str, ix: list[int], num: list[int]) -> bool:
        # ix and num are lists so we can modify them by reference
        min_flag = False
        num[0] = 0
        while ix[0] < len(inp) and inp[ix[0]] == ' ':
            ix[0] += 1
        if ix[0] < len(inp) and inp[ix[0]] == '-':
            min_flag = True
            ix[0] += 1
        if ix[0] >= len(inp) or not ('0' <= inp[ix[0]] <= '9'):
            return True
        while ix[0] < len(inp) and '0' <= inp[ix[0]] <= '9':
            num[0] = num[0] * 10 + (ord(inp[ix[0]]) - ord('0'))
            ix[0] += 1
        if min_flag:
            num[0] = -num[0]
        while ix[0] < len(inp) and inp[ix[0]] == ' ':
            ix[0] += 1
        return False
    
    
    def parseNumberBackward(inp: str, ix: list[int], num: list[int]) -> bool:
        digvalue = 1
        num[0] = 0
        while ix[0] >= 0 and inp[ix[0]] == ' ':
            ix[0] -= 1
        if ix[0] < 0:
            return True
        if not ('0' <= inp[ix[0]] <= '9'):
            return True
        while ix[0] >= 0 and '0' <= inp[ix[0]] <= '9':
            num[0] += digvalue * (ord(inp[ix[0]]) - ord('0'))
            digvalue *= 10
            ix[0] -= 1
        if ix[0] >= 0 and inp[ix[0]] == '-':
            num[0] = -num[0]
            ix[0] -= 1
        while ix[0] >= 0 and inp[ix[0]] == ' ':
            ix[0] -= 1
        return False
    

    def parseInput(self, inp: str) -> int:
        # scan characters
        f = 0
        for ch in inp:
            if ch in {',', '(', ')', '9', '0'}:
                f |= 1  # cannot be position string, but may be movelist
            elif ('a' <= ch <= 'h') or ('A' <= ch <= 'H') or ('u' <= ch <= 'z') or ('U' <= ch <= 'Z'):
                f |= 2  # cannot be movelist, but may be position string
            elif ch != '/' and ch != '-' and (ch < '1' or ch > '8'):
                f |= 3  # cannot be either
    
        if f == 3 or f == 0:
            return 13
    
        self.reset()
        lw, lu = 0, 0
    
        if f == 1 and not generator:
            # solution move sequence. start parsing from end
            md = 0
            i = len(inp) - 1
            while i >= 0:
                while i >= 0 and inp[i] == ' ':
                    i -= 1
                if i < 0:
                    break
                if md == 0:  # parsing any move
                    if inp[i] == '/':
                        md = 1
                    else:
                        md = 2
                elif md == 1:
                    if i < 0 or inp[i] != '/':
                        return 16
                    i -= 1
                    if not self.doTwist():
                        return 12
                    lu += 1
                    lw += 1
                    md = 2
                elif md == 2:
                    m = 0
                    br = False
                    if inp[i] == ')':
                        i -= 1
                        br = True
                    if self.parseNumberBackward(inp, [i], [m]):
                        return 5
                    m %= 12
                    self.doBot(-m)
                    if m != 0:
                        lu += 1
                    if i < 0 or inp[i] != ',':
                        return 6
                    i -= 1
                    if self.parseNumberBackward(inp, [i], [m]):
                        return 7
                    m %= 12
                    self.doTop(-m)
                    if m != 0:
                        lu += 1
                    if br:
                        if i < 0 or inp[i] != '(':
                            return 8
                        i -= 1
                    md -= 1
                else:
                    # Safety break to avoid infinite loop if unexpected md value
                    break
            if not self.isTwistable():
                return 12
            if verbosity >= 2:
                print(f"Input: {inp} [{lw}|{lu}]")
    
        elif f == 1:
            # generating move sequence. start parsing from beginning
            md = 0
            i = 0
            n = len(inp)
            while i < n:
                while i < n and inp[i] == ' ':
                    i += 1
                if i >= n:
                    break
                if md == 0:  # parsing any move
                    if inp[i] == '/':
                        md = 1
                    else:
                        md = 2
                elif md == 1:
                    if i >= n or inp[i] != '/':
                        return 16
                    i += 1
                    if not self.doTwist():
                        return 12
                    lu += 1
                    lw += 1
                    md = 2
                elif md == 2:
                    m = 0
                    br = False
                    if i < n and inp[i] == '(':
                        i += 1
                        br = True
                    if self.parseNumberForward(inp, [i], [m]):
                        return 7
                    m %= 12
                    self.doTop(m)
                    if m != 0:
                        lu += 1
                    if i >= n or inp[i] != ',':
                        return 6
                    i += 1
                    if self.parseNumberForward(inp, [i], [m]):
                        return 5
                    m %= 12
                    self.doBot(m)
                    if m != 0:
                        lu += 1
                    if br:
                        if i >= n or inp[i] != ')':
                            return 4
                        i += 1
                    md -= 1
                else:
                    # Safety break to avoid infinite loop if unexpected md value
                    break
            if not self.isTwistable():
                return 12
            if verbosity >= 2:
                print(f"Input: {inp} [{lw}|{lu}]")
    
        else:
            # position
            if len(inp) != 16 and len(inp) != 17:
                return 9
            pieceCount = [0] * 16
            cecount = [0] * 6
            j = 0
            pi = [0] * 24
            nextPartialCorner = -3
            nextPartialEdge = 18
    
            for i in range(16):
                k = inp[i]
                if 'a' <= k <= 'z':
                    k = chr(ord(k) - (ord('a') - ord('A')))
                if 'A' <= k <= 'H':
                    k = ord(k) - ord('A')
                elif '1' <= k <= '8':
                    k = ord(k) - ord('1') + 8
                elif 'U' <= k <= 'W':
                    k = ord(k) + (nextPartialCorner - ord('U'))
                    nextPartialCorner -= 3
                elif 'X' <= k <= 'Z':
                    k = ord(k) + (nextPartialEdge - ord('X'))
                    nextPartialEdge += 3
                else:
                    return 10
                pi[j] = k
                j += 1
                if 0 <= k <= 15:
                    pieceCount[k] += 1
                if k < 8:
                    pi[j] = k
                    j += 1
                    cecount[2] += 1
                    if (k < 0 and k % 3 == 0) or (0 <= k <= 3):
                        cecount[0] += 1  # corner up
                    if (k < 0 and k % 3 == -2) or (4 <= k <= 7):
                        cecount[1] += 1  # corner down
                else:
                    cecount[5] += 1
                    if (k > 15 and k % 3 == 0) or (8 <= k <= 11):
                        cecount[3] += 1  # edge up
                    if (k > 15 and k % 3 == 1) or (12 <= k <= 15):
                        cecount[4] += 1  # edge down
    
            for i in range(16):
                if pieceCount[i] > 1:
                    return 17
            if cecount[0] > 4 or cecount[1] > 4 or cecount[2] > 8 or cecount[3] > 4 or cecount[4] > 4 or cecount[5] > 8:
                return 17
    
            midLayer = 0
            if len(inp) == 17:
                k = inp[16]
                if k not in ('-', '/'):
                    return 11
                midLayer = 1 if k == '-' else -1
    
            self.set(pi, midLayer)
    
        return 0

    def has2GenCorners(self) -> bool:
        # get corners (assuming square/square shape)
        tmp = [0] * 6
        j = 0
        for i in range(18):
            if self.pos[i] < 8:
                if j % 2 == 0:
                    tmp[j // 2] = self.pos[i]
                j += 1
    
        # place D corners - if we find a D corner on U, AUF and then insert
        found_d = -1
        for i in range(4):
            if tmp[i] > 3:
                found_d = i
        if found_d > -1:
            tmp2 = tmp[:4]
            for i in range(4):
                tmp[i] = tmp2[(i + found_d) % 4]
            tmp[0], tmp[4] = tmp[4], tmp[0]
            tmp[2], tmp[3] = tmp[3], tmp[2]
    
        found_d = -1
        for i in range(4):
            if tmp[i] > 3:
                found_d = i
        if found_d > -1:
            tmp2 = tmp[:4]
            for i in range(4):
                tmp[i] = tmp2[(i + found_d) % 4]
            tmp[0], tmp[5] = tmp[5], tmp[0]
            tmp[1], tmp[2] = tmp[2], tmp[1]
    
        # adjust if D corners are swapped, then AUF
        if tmp[4] == 5 and tmp[5] == 4:
            tmp[4], tmp[5] = 4, 5
            tmp[0], tmp[2] = tmp[2], tmp[0]
    
        found_u = -1
        for i in range(4):
            if tmp[i] == 0:
                found_u = i
        if found_u > -1:
            tmp2 = tmp[:4]
            for i in range(4):
                tmp[i] = tmp2[(i + found_u) % 4]
    
        return tmp[0] == 0 and tmp[1] == 1 and tmp[2] == 2 and tmp[3] == 3 and tmp[4] == 4 and tmp[5] == 5
    
    
    def singleMatch(self, posI: int, solvedI: int) -> bool:
        if posI == solvedI:
            return True
        if posI > 15 and posI % 3 == 0 and 8 <= solvedI <= 11:
            return True  # edge up
        if posI > 15 and posI % 3 == 1 and 12 <= solvedI <= 15:
            return True  # edge down
        if posI < 0 and posI % 3 == 0 and 0 <= solvedI <= 3:
            return True  # corner up
        if posI < 0 and posI % 3 == -2 and 4 <= solvedI <= 7:
            return True  # corner down
        if posI > 15 and posI % 3 == 2 and 8 <= solvedI <= 15:
            return True  # edge any
        if posI < 0 and posI % 3 == -1 and 0 <= solvedI <= 7:
            return True  # corner any
        return False
    
    
    def matchesSolved(self) -> bool:
        solved = [0, 0, 8, 1, 1, 9, 2, 2, 10, 3, 3, 11, 12, 4, 4, 13, 5, 5, 14, 6, 6, 15, 7, 7]
        for i in range(24):
            if not self.singleMatch(self.pos[i], solved[i]):
                return False
        return True
    
    
    def isPartial(self) -> bool:
        for i in range(24):
            if self.pos[i] < 0 or self.pos[i] > 15:
                return True
        return False


class PrunTable:
    def __init__(self, p0, cl, stt, scte, sctc):
        self.stt = stt
        self.scte = scte
        self.sctc = sctc

        # Allocate table: NUMSHAPES x 70 x 70
        self.table = [[[0 for _ in range(70)] for _ in range(70)] for _ in range(NUMSHAPES)]

        if metric == TURN_METRIC:
            fname = FILEP1U if cl == 0 else FILEP2U
        elif metric == ANGLE_METRIC:
            fname = FILEP1A if cl == 0 else FILEP2A
        else:
            fname = FILEP1W if cl == 0 else FILEP2W

        try:
            with open(fname, "rb") as f:
                raw = f.read(NUMSHAPES * 70 * 70)
                for i0 in range(NUMSHAPES):
                    for i1 in range(70):
                        for i2 in range(70):
                            index = i0 * 70 * 70 + i1 * 70 + i2
                            self.table[i0][i1][i2] = raw[index]
        except FileNotFoundError:
            # no file - calculate table
            for i0 in range(NUMSHAPES):
                for i1 in range(70):
                    for i2 in range(70):
                        self.table[i0][i1][i2] = 0

            s0 = stt.getShape(p0.getShape(), p0.getParityOdd())
            e0 = p0.getEdgeColouring(cl)
            c0 = p0.getCornerColouring(cl)
            e0 = scte.ct.choice2Idx[e0]
            c0 = sctc.ct.choice2Idx[c0]

            if metric == TURN_METRIC or metric == ANGLE_METRIC:
                self.table[s0][e0][c0] = 1
            else:
                self.setAll(s0, e0, c0, 1)

            l = 1
            n = 1
            last_nonzero = -1

            while l - last_nonzero < 10:
                if verbosity >= 6:
                    print(f" l={l-1}  n={n}")

                n = 0
                if metric == TURN_METRIC:
                    for i0 in range(NUMSHAPES):
                        for i1 in range(70):
                            for i2 in range(70):
                                if self.table[i0][i1][i2] == l:
                                    for m in range(3):
                                        j0, j1, j2 = i0, i1, i2
                                        w = 0
                                        while True:
                                            j2 = sctc.tranTable[j0][j2][m]
                                            j1 = scte.tranTable[j0][j1][m]
                                            j0 = stt.tranTable[j0][m]
                                            if self.table[j0][j1][j2] == 0:
                                                self.table[j0][j1][j2] = l + 1
                                                n += 1
                                            w += 1
                                            if w > 12:
                                                sys.exit(0)
                                            if j0 == i0 and j1 == i1 and j2 == i2:
                                                break
                elif metric == ANGLE_METRIC:
                    for i0 in range(NUMSHAPES):
                        for i1 in range(70):
                            for i2 in range(70):
                                if self.table[i0][i1][i2] == l:
                                    for m in range(3):
                                        j0, j1, j2 = i0, i1, i2
                                        w = 0
                                        newcnt = 0
                                        while True:
                                            if m == 0:
                                                w += stt.getTopTurn(j0)
                                            elif m == 1:
                                                w += stt.getBotTurn(j0)
                                            else:
                                                w += 1
                                            j2 = sctc.tranTable[j0][j2][m]
                                            j1 = scte.tranTable[j0][j1][m]
                                            j0 = stt.tranTable[j0][m]
                                            if m == 2:
                                                newcnt = l + 1
                                            else:
                                                newcnt = l + (12 - w if w > 6 else w)
                                            if self.table[j0][j1][j2] == 0 or self.table[j0][j1][j2] > newcnt:
                                                self.table[j0][j1][j2] = newcnt
                                                n += 1
                                            if w > 12:
                                                sys.exit(0)
                                            if j0 == i0 and j1 == i1 and j2 == i2:
                                                break
                else:
                    for i0 in range(NUMSHAPES):
                        for i1 in range(70):
                            for i2 in range(70):
                                if self.table[i0][i1][i2] == l:
                                    j0 = stt.tranTable[i0][2]
                                    j1 = scte.tranTable[i0][i1][2]
                                    j2 = sctc.tranTable[i0][i2][2]
                                    if self.table[j0][j1][j2] == 0:
                                        n += self.setAll(j0, j1, j2, l + 1)

                l += 1
                if n != 0:
                    last_nonzero = l

            if verbosity >= 6:
                print()

            with open(fname, "wb") as f:
                f.write(bytearray(
                    self.table[i0][i1][i2]
                    for i0 in range(NUMSHAPES)
                    for i1 in range(70)
                    for i2 in range(70)
                ))

    def setAll(self, i0, i1, i2, l):
        n = 0
        j0, j1, j2 = i0, i1, i2
        while True:
            k0, k1, k2 = j0, j1, j2
            while True:
                if self.table[k0][k1][k2] == 0:
                    self.table[k0][k1][k2] = l
                    n += 1
                k2 = self.sctc.tranTable[k0][k2][0]
                k1 = self.scte.tranTable[k0][k1][0]
                k0 = self.stt.tranTable[k0][0]
                if (k0 == j0 and k1 == j1 and k2 == j2):
                    break
            j2 = self.sctc.tranTable[j0][j2][1]
            j1 = self.scte.tranTable[j0][j1][1]
            j0 = self.stt.tranTable[j0][1]
            if (j0 == i0 and j1 == i1 and j2 == i2):
                break
        return n

class PositionSolver:
    def __init__(self, stt, scte, sctc, pr1, pr2):
        self.ans = None
        
        # ShapeTranTable, ShpColTranTable, PrunTable references
        self.stt = stt
        self.scte = scte
        self.sctc = sctc
        self.pr1 = pr1
        self.pr2 = pr2

        # Encoded states
        self.e0 = -1
        self.e1 = -1
        self.e2 = -1
        self.c0 = -1
        self.c1 = -1
        self.c2 = -1

        self.shp = -1
        self.shp2 = -1
        self.middle = 0
        self.fp = None

        self.moveList = [0]*50
        self.moveLen = 0
        self.lastTurns = [0]*6
        self.findAll = False
        self.ignoreTrans = False

    def set(self, p, findAll0, ignoreTrans0):
        cc0 = p.getCornerColouring(0)
        cc1 = p.getCornerColouring(1)
        cc2 = p.getCornerColouring(2)

        self.c0 = -1 if cc0 == -1 else self.sctc.ct.choice2Idx[cc0]
        self.c1 = -1 if cc1 == -1 else self.sctc.ct.choice2Idx[cc1]
        self.c2 = -1 if cc2 == -1 else self.sctc.ct.choice2Idx[cc2]

        ec0 = p.getEdgeColouring(0)
        ec1 = p.getEdgeColouring(1)
        ec2 = p.getEdgeColouring(2)

        self.e0 = -1 if ec0 == -1 else self.scte.ct.choice2Idx[ec0]
        self.e1 = -1 if ec1 == -1 else self.scte.ct.choice2Idx[ec1]
        self.e2 = -1 if ec2 == -1 else self.scte.ct.choice2Idx[ec2]

        self.shp = self.stt.getShape(p.getShape(), p.getParityOdd())
        self.shp2 = self.stt.tranTable[self.shp][3]
        self.middle = p.middle

        self.findAll = findAll0
        self.ignoreTrans = ignoreTrans0

        self.fp = p

    def doMove(self, m):
        mirrmv = [1, 0, 2]
        r = 0
        if m == 0:
            r = self.stt.getTopTurn(self.shp)
        elif m == 1:
            r = self.stt.getBotTurn(self.shp)
        else:
            self.middle = -self.middle
    
        self.c0 = self.sctc.tranTable[self.shp][self.c0][m]
        self.c1 = self.sctc.tranTable[self.shp][self.c1][m]
        self.e0 = self.scte.tranTable[self.shp][self.e0][m]
        self.e1 = self.scte.tranTable[self.shp][self.e1][m]
        self.shp = self.stt.tranTable[self.shp][m]
    
        self.c2 = self.sctc.tranTable[self.shp2][self.c2][mirrmv[m]]
        self.e2 = self.scte.tranTable[self.shp2][self.e2][mirrmv[m]]
        self.shp2 = self.stt.tranTable[self.shp2][mirrmv[m]]
    
        return r

    def solve(self, twoGen: int, extraMoves: int, keepCubeShape: bool) -> int:
        # Check if the given position is solvable under the constraints
        if twoGen == 2:
            # Check if 7G8H pieces are solved
            if (self.fp.pos[18] != 14 or self.fp.pos[19] != 6 or self.fp.pos[20] != 6 or
                self.fp.pos[21] != 15 or self.fp.pos[22] != 7 or self.fp.pos[23] != 7):
                return 19
        elif twoGen == 1:
            # Check if G8H are solved, or solved-and-ADF
            g8h_ok_1 = (self.fp.pos[19] == 6 and self.fp.pos[20] == 6 and 
                        self.fp.pos[21] == 15 and self.fp.pos[22] == 7 and self.fp.pos[23] == 7)
            g8h_ok_2 = (self.fp.pos[18] == 6 and self.fp.pos[19] == 6 and 
                        self.fp.pos[20] == 15 and self.fp.pos[21] == 7 and self.fp.pos[22] == 7)
            if not (g8h_ok_1 or g8h_ok_2):
                return 19
    
        if keepCubeShape:
            # Check shape and parity for cube
            valid_shapes = {5052, 4148, 5039, 4163}
            if not (self.shp in valid_shapes and self.shp2 in valid_shapes):
                return 19
            if twoGen == 1 and not self.fp.has2GenCorners():
                return 19
    
        # Begin solving
        self.moveLen = 0
        nodes = [0]
    
        # For twist metric, only even lengths if middle is a square
        l = -1
        if metric == TWIST_METRIC and self.middle == 1:
            l = -2
    
        optimalMoves = -1
    
        while True:
            l += 1
            if metric == TWIST_METRIC and self.middle != 0:
                l += 1
    
            if verbosity >= 5:
                print(f"searching depth {l}", flush=True)
    
            for i in range(6):
                self.lastTurns[i] = 0
    
            searchResult = self.search(l, 3, nodes, twoGen, keepCubeShape)
    
            if searchResult != 0:
                if optimalMoves == -1:
                    optimalMoves = l
    
                limit = optimalMoves + extraMoves
                if l >= limit or (metric == TWIST_METRIC and self.middle != 0 and l + 1 >= limit):
                    break
    
        return 0

    def isSolved(self) -> bool:
        return (
            self.shp == 4163 and
            self.e0 == 69 and self.e1 == 44 and self.e2 == 44 and
            self.c0 == 69 and self.c1 == 44 and self.c2 == 44 and
            self.middle >= 0
        )
    
    def prunedOut(self, l: int) -> bool:
        # Prune if heuristic estimate from pruning tables is greater than current depth
        if self.pr1.table[self.shp][self.e0][self.c0] > l + 1:
            return True
        if self.pr2.table[self.shp][self.e1][self.c1] > l + 1:
            return True
        if self.pr2.table[self.shp2][self.e2][self.c2] > l + 1:
            return True
        return False

    def search(self, l: int, lm: int, nodes: list, twoGen: int, keepCubeShape: bool) -> int:
        r = 0
    
        # increase node counter
        nodes[0] += 1
        if l < 0:
            return 0
    
        # --- Prune based on transformation symmetry ---
        if metric == TURN_METRIC and not self.ignoreTrans and twoGen == 0:
            i = 0
            if self.lastTurns[0] == 0: i += 1
            elif self.lastTurns[0] == 6: i -= 1
            if self.lastTurns[1] == 0: i += 1
            elif self.lastTurns[1] == 6: i -= 1
            if self.lastTurns[4] == 0: i += 1
            elif self.lastTurns[4] == 6: i -= 1
            if self.lastTurns[5] == 0: i += 1
            elif self.lastTurns[5] == 6: i -= 1
    
            absTopMove = 12 - self.lastTurns[0] if self.lastTurns[0] > 6 else self.lastTurns[0]
            absBottomMove = 12 - self.lastTurns[1] if self.lastTurns[1] > 6 else self.lastTurns[1]
    
            if i < 0 or (i == 0 and (absTopMove + absBottomMove > 6 or 
                (absTopMove + absBottomMove == 6 and absTopMove < absBottomMove))):
                return 0
    
        # --- Check if position is solved ---
        if l == 0:
            if self.isSolved():
                self.ans = self.printsol()
                if verbosity >= 6:
                    print(f"Nodes={nodes[0]}")
                return 1
            elif metric != TWIST_METRIC:
                return 0
    
        # --- Prune based on lookup tables ---
        if self.prunedOut(l):
            return 0
    
        # --- Try top layer moves ---
        if lm >= 2:
            i = self.doMove(0)
            while i < 12:
                absTopMove = 12 - i if i > 6 else i
                if absTopMove <= maxX and absTopMove <= maxTotal:
                    self.moveList[self.moveLen] = i
                    self.moveLen += 1
                    self.lastTurns[4] = i
                    cost = 1 if metric == TURN_METRIC else absTopMove if metric == ANGLE_METRIC else 1
                    r += self.search(l - cost, 0, nodes, twoGen, keepCubeShape)
                    self.moveLen -= 1
                    if r != 0 and not self.findAll:
                        return r
                i += self.doMove(0)
            self.lastTurns[4] = 0
    
        # --- Try bottom layer moves ---
        if lm != 1 and twoGen != 2:
            i = self.doMove(1)
            while i < 12:
                topMove = self.lastTurns[4]
                absTopMove = 12 - topMove if topMove > 6 else topMove
                absBottomMove = 12 - i if i > 6 else i
                if (absBottomMove <= maxY and 
                    absBottomMove + absTopMove <= maxTotal and
                    (metric == TURN_METRIC or self.ignoreTrans or twoGen != 0 or l < 2 or
                     absTopMove + absBottomMove < 6 or 
                     (absTopMove + absBottomMove == 6 and absTopMove >= absBottomMove))):
                    self.moveList[self.moveLen] = i + 12
                    self.moveLen += 1
                    self.lastTurns[5] = i
                    if twoGen != 1 or i in (1, 11):
                        cost = 1 if metric == TURN_METRIC else absBottomMove if metric == ANGLE_METRIC else 1
                        r += self.search(l - cost, 1, nodes, twoGen, keepCubeShape)
                    self.moveLen -= 1
                    if r != 0 and not self.findAll:
                        return r
                i += self.doMove(1)
            self.lastTurns[5] = 0
    
        # --- Try twist move ---
        if lm != 2 and l > 0:
            lt0, lt1 = self.lastTurns[0], self.lastTurns[1]
            self.lastTurns[0] = self.lastTurns[2]
            self.lastTurns[1] = self.lastTurns[3]
            self.lastTurns[2] = self.lastTurns[4]
            self.lastTurns[3] = self.lastTurns[5]
            self.lastTurns[4] = 0
            self.lastTurns[5] = 0
    
            self.doMove(2)
            if (not keepCubeShape or 
                (self.shp in {5052, 4148, 5039, 4163} and self.shp2 in {5052, 4148, 5039, 4163})):
                self.moveList[self.moveLen] = 0
                self.moveLen += 1
                r += self.search(l - 1, 2, nodes, twoGen, keepCubeShape)
                self.moveLen -= 1
                if r != 0 and not self.findAll:
                    return r
            self.doMove(2)  # Undo twist
    
            self.lastTurns[5] = self.lastTurns[3]
            self.lastTurns[4] = self.lastTurns[2]
            self.lastTurns[3] = self.lastTurns[1]
            self.lastTurns[2] = self.lastTurns[0]
            self.lastTurns[1] = lt1
            self.lastTurns[0] = lt0
    
        return r

    def normalise_move(self, m: int) -> int:
        while m < 0:
            m += 12
        while m >= 12:
            m -= 12
        if usenegative and m > 6:
            m -= 12
        return m
    
    def print_move(self, mu: int, md: int, removeAUF: bool) -> str:
        out = ""
        if removeAUF:
            mu = (mu + 13) % 3 - 1
            md = (md + 13) % 3 - 1
        if mu != 0 or md != 0:
            if usebrackets and not karnotation:
                out += "("
            out += f"{mu},{md}"
            if usebrackets and not karnotation:
                out += ")"
        return out
    
    def replace_all(self, string: str, old: str, new: str) -> str:
        return string.replace(old, new)

    def printsol(self):
        out = ""
        tw = tu = 0
        mu = md = 0
        angle = 0
    
        if generator:
            # reverse iteration
            for i in range(self.moveLen - 1, -1, -1):
                move = self.moveList[i]
                if move == 0:
                    out += self.print_move(mu, md, tw == 0 and karnotation)
                    mu = md = 0
                    out += "/"
                    tu += 1
                    tw += 1
                    angle += 1
                elif move < 12:
                    mu = self.normalise_move(mu - move)
                    tu += 1
                    angle += abs(mu)
                else:
                    md = self.normalise_move(md + move)
                    tu += 1
                    angle += abs(md)
        else:
            for i in range(self.moveLen):
                move = self.moveList[i]
                if move == 0:
                    out += self.print_move(mu, md, tw == 0 and karnotation)
                    mu = md = 0
                    out += "/"
                    tu += 1
                    tw += 1
                    angle += 1
                elif move < 12:
                    mu = self.normalise_move(mu + move)
                    tu += 1
                    angle += abs(mu)
                else:
                    md = self.normalise_move(md - move)
                    tu += 1
                    angle += abs(md)
    
        out += self.print_move(mu, md, karnotation)
    
        if karnotation:
            # Remove all whitespace
            out = self.replace_all(out, " ", "")
    
            # Replace negative numbers to avoid issues in notation
            out = self.replace_all(out, "-1", "&")
            out = self.replace_all(out, "-2", "^")
            out = self.replace_all(out, "-3", "9")
            out = self.replace_all(out, "-4", "8")
            out = self.replace_all(out, "-5", "7")
    
            # Apply KARNOTATION replacements
            for i in range(len(KARNOTATION) - 1, -1, -1):
                out = self.replace_all(out, KARNOTATION[i][1], KARNOTATION[i][0])
    
            out = self.replace_all(out, "/", " ")
            out = self.replace_all(out, "\\", "/")
            out = self.replace_all(out, ",", "")
    
            # Undo previous number replacement
            out = self.replace_all(out, "&", "-1")
            out = self.replace_all(out, "^", "-2")
            out = self.replace_all(out, "9", "-3")
            out = self.replace_all(out, "8", "-4")
            out = self.replace_all(out, "7", "-5")
    
        print(out, end='')
        print(f"  [{tw}|{tu}", end='')
        if metric == ANGLE_METRIC:
            print(f"|{angle}", end='')
        print("]")
        return out + f"  [{tw}|{tu}" + (f"|{angle}]" if metric == ANGLE_METRIC else "]")


def show(e):
    print(errors[e - 1], file=sys.stderr)
    return e


def parse_integer(s):
    if not s.isdigit():
        return -1
    return int(s)


def solve(case):
    # === 1. Set up flags manually or from a UI/wrapper ===
    ignoreMid = False
    ignoreTrans = False
    findAll = False
    twoGen = 0  # 0 = normal, 1 = pseudo 2gen, 2 = strict 2gen
    extraMoves = 0
    keepCubeShape = False
    if not hasattr(solve, "ps"):
        if verbosity >= 3:
            print("Initialising...")
        
        # calculate transition tables
        ct = ChoiceTable()
        
        if verbosity >= 4:
            print("  5. Shape transition table")
        st = ShapeTranTable()
        
        if verbosity >= 4:
            print("  4. Colouring 1 transition table")
        scte = ShpColTranTable(st, ct, True)
        
        if verbosity >= 4:
            print("  3. Colouring 2 transition table")
        sctc = ShpColTranTable(st, ct, False)
        
        # calculate pruning tables for two colourings
        q = FullPosition()
        
        if verbosity >= 4:
            print("  2. Colouring 1 pruning table")
        pr1 = PrunTable(q, 0, st, scte, sctc)
        
        if verbosity >= 4:
            print("  1. Colouring 2 pruning table")
        pr2 = PrunTable(q, 1, st, scte, sctc)
        
        if verbosity >= 4:
            print("  0. Finished.")
        
        solve.ps = PositionSolver(st, scte, sctc, pr1, pr2)

    ps = solve.ps
    p = FullPosition()

    if verbosity >= 2:
        print("Flags: ", end="")
        print("Turn" if metric == TURN_METRIC else "Twist", end="")
        print(" Metric, ", end="")
        print("Find ", end="")
        print("every " if findAll else "first ", end="")
        print("generator" if generator else "solution", end="")
    
        if twoGen == 1:
            print(", Pseudo 2gen", end="")
        elif twoGen == 2:
            print(", 2gen", end="")
    
        if keepCubeShape:
            print(", Keep Cube Shape", end="")
    
        print()

    random.seed(time.time())

    buffer = ""
    
    now = time.time()
    
    if ignoreMid:
        p.middle = 0

    if verbosity >= 1:
        print("Position: ", end="")
        p.print()
        print()

    r = p.parseInput(case)
    if r:
        show(r)
        return

    # convert position to colour encoding
    ps.set(p, findAll, ignoreTrans)
    # solve position
    r = ps.solve(twoGen, extraMoves, keepCubeShape)
    if r:
        show(r)

    if verbosity >= 6:
        elapsed = time.time() - now
        print(f"Time: {elapsed:.2f}")
    else:
        print()
    return ps.ans


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sq1.py <input_string>")
        sys.exit(1)
    
    input_case = sys.argv[1]
    solve(input_case)

