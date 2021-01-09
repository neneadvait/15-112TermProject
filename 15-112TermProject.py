#################################################
# Term Project
#
# Name: Advait Nene
# Andrew Id: anene
# Recitation Section: S0
#################################################

from cmu_112_graphics import *
import math
import copy

class Button(object):
    def __init__(self, x1, y1, x2, y2, text, font):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.text = text
        self.font = font
    
    def getHashables(self):
        return (self.x1, self.y1, self.x2, self.y2, self.text, self.font)

    def __eq__(self, other):
        if(isinstance(other, Button)):
            return getHashables(self) == getHashables(other)
        return False

    def coordIn(self, x, y):
        if(self.x1 < x < self.x2 and self.y1 < y < self.y2):
            return True
        return False
    
    def drawButton(self, app, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, width = 3)
        canvas.create_text((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2, text = self.text, font = self.font)

    def __repr__(self):
        return f"({self.x1}, {self.y1}, {self.x2}, {self.y2}, {repr(self.text)}, {repr(self.font)})"

# Creates x and y axes in viewing plane.
def makeViewingAxes(app):
    a, b, c, d = app.plane
    app.viewingY = [[a * c / d], [b * c / d], [1 + c ** 2 / d]]
    app.viewingY = scalarMultiply(app.viewingY, 400 / app.viewRadius)
    rVector = [[a], [b], [c]]
    rVector = scalarMultiply(rVector, 1 / math.sqrt(a ** 2 + b ** 2 + c ** 2))
    app.viewingX = cross(app.viewingY, rVector)

# Projects 3D points onto viewing plane.
def projectPoints(app, points):
    imagePoints = []
    for point in points:
        x = math.floor(app.width / 2 + dot(point, app.viewingX))
        y = math.floor(app.height / 2 - dot(point, app.viewingY))
        imagePoints.append((x, y))
    return imagePoints

# Makes tangent plane (ax+by+cz+d = 0) to current position on viewing sphere.
def createTangentPlane(app):
    a = app.viewRadius * math.sin(app.phi) * math.cos(app.theta)
    b = app.viewRadius * math.sin(app.phi) * math.sin(app.theta)
    c = app.viewRadius * math.cos(app.phi)
    d = -(a ** 2 + b ** 2 + c ** 2)
    app.plane = (a, b, c, d)

# Produces points for graphing.
def producePoints(app):
    app.points = []
    x = -app.viewRadius
    y = -app.viewRadius
    dx = app.viewRadius / 1000
    dy = app.viewRadius / 1000
    while x <= app.viewRadius:
        maxXDeriv = 0
        y = -app.viewRadius
        while y <= app.viewRadius:
            try:
                z = app.function(x, y)

                if(abs(z) <= 2 * app.viewRadius):
                    app.points.append([[x], [y], [z]])
                z1 = app.function(x + dx, y)
                z2 = app.function(x, y + dy)

                yDeriv = math.pow(abs((z2 - z) / dy) + 1, 1 / 4)
                maxXDeriv = max(maxXDeriv, abs((z1 - z) / dx))
            except:
                yDeriv = 1
            y += app.viewRadius / (50 * yDeriv)
        gradSize = math.pow(maxXDeriv + 1, 1 / 4)
        x += app.viewRadius / (15 * gradSize)
    x = -app.viewRadius
    y = -app.viewRadius
    while y <= app.viewRadius:
        maxYDeriv = 0
        x = -app.viewRadius
        while x <= app.viewRadius:
            try:
                z = app.function(x, y)

                if(abs(z) <= 2 * app.viewRadius):
                    app.points.append([[x], [y], [z]])
                z1 = app.function(x + dx, y)
                z2 = app.function(x, y + dy)
                
                xDeriv = math.pow(abs((z1 - z) / dx) + 1, 1 / 4)
                maxYDeriv = max(maxYDeriv, abs((z2 - z) / dy))
            except:
                xDeriv = 1
            x += app.viewRadius / (50 * xDeriv)
        gradSize = math.pow(maxYDeriv + 1, 1 / 4)
        y += app.viewRadius / (15 * gradSize)

# All rotation operations
def allRotationOperations(app):
    createTangentPlane(app)
    makeViewingAxes(app)
    app.imagePoints = projectPoints(app, app.points)
    app.imageXAxis = projectPoints(app, app.xAxis)
    app.imageYAxis = projectPoints(app, app.yAxis)
    app.imageZAxis = projectPoints(app, app.zAxis)
    app.imageScale = projectPoints(app, app.scalePoints)

# Increases or decreases the viewing radius to zoom.
def zoom(app, out):
    if (out):
        app.viewRadius /= 1.2
    else:
        app.viewRadius *= 1.2
    prepPoints(app)

# Makes points on three axes.
def makeAxes(app):
    xMax = yMax = zMax = 2 * app.viewRadius
    app.xAxis = [[[-xMax], [0], [0]], [[xMax], [0], [0]]]
    app.yAxis = [[[0], [-yMax], [0]], [[0], [yMax], [0]]]
    app.zAxis = [[[0], [0], [-zMax]], [[0], [0], [zMax]]]

# Makes points for scale.
def makeScale(app):
    app.scale = 2 * (10 ** (math.floor(math.log(app.viewRadius, 10))))
    app.scalePoints = []
    for i in range(1, int(2 * app.viewRadius // app.scale) + 1):
        app.scalePoints.append([[i * app.scale], [-app.scale / 10], [0]])
        app.scalePoints.append([[-i * app.scale], [-app.scale / 10], [0]])
        app.scalePoints.append([[-app.scale / 10], [i * app.scale], [0]])
        app.scalePoints.append([[-app.scale / 10], [-i * app.scale], [0]])
        app.scalePoints.append([[-app.scale / 10], [0], [i * app.scale]])
        app.scalePoints.append([[-app.scale / 10], [0], [-i * app.scale]])

# Makes points, axes, and scale points.
def prepPoints(app):
    producePoints(app)
    makeAxes(app)
    makeScale(app)

# Makes derivatives up to x(3) and y(3)
def makeAllDerivs(app):
    app.derivs = [([0] * 4) for i in range(4)]
    app.derivs[0][0] = app.elements
    for i in range(4):
        if(i == 0):
            app.derivs[i][0] = app.elements
        else:
            app.derivs[i][0] = removeUselessPars(deriv(app.derivs[i - 1][0], "x"))
        for j in range(1, 4):
            app.derivs[i][j] = removeUselessPars(deriv(app.derivs[i][j - 1], "y"))

# Runs initial operations, asks user for function to graph.
def appStarted(app):
    app.timerDelay = 500
    app.margin = app.width / 40
    app.graph = False
    makeButtons(app)
    app.help = False
    app.space = "|"
    app.derivative = [0, 0]
    app.viewRadius = 2
    app.theta = -math.pi / 4
    app.phi = math.pi / 4
    app.function = ""
    app.pointer = 0

# Controls when rotations, zooms, and restarts happen.
def keyPressed(app, event):
    if(not app.graph):
        if(event.key == "Enter"):
            try:
                app.graph = True
                app.timerDelay = 100
                app.function = clearLaTeXCommands(app.function)
                # NEW
                app.elements = betterSplit(app.function)
                makeAllDerivs(app)
                app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
                app.function = replaceVariables(app.function)
                app.function = evalLambda(app.function)
                # NEW
                prepPoints(app)
                allRotationOperations(app)
            except:
                appStarted(app)
        elif(event.key == "Delete"):
            app.function = app.function[:app.pointer - 1] + app.function[app.pointer:]
            app.pointer -= 1
        elif(event.key == "Left"):
            app.pointer = max(0, app.pointer - 1)
        elif(event.key == "Right"):
            app.pointer = min(len(app.function), app.pointer + 1)
        elif(event.key not in ["Up", "Down", "Space"]):
            app.function = app.function[:app.pointer] + event.key + app.function[app.pointer:]
            app.pointer += 1

# Draws all points on function.
def drawPoints(app, canvas):
    for point in app.imagePoints:
        x, y = point
        r = 1
        canvas.create_oval(x - r, y - r, x + r, y + r, fill = "magenta",\
                           outline = "magenta")

# Draws all three axes.
def drawAxes(app, canvas):
    canvas.create_line(app.imageXAxis[0][0], app.imageXAxis[0][1],\
                       app.imageXAxis[1][0], app.imageXAxis[1][1],\
                       fill = "red", width = 2)
    canvas.create_line(app.imageYAxis[0][0], app.imageYAxis[0][1],\
                       app.imageYAxis[1][0], app.imageYAxis[1][1],\
                       fill = "green", width = 2)
    canvas.create_line(app.imageZAxis[0][0], app.imageZAxis[0][1],\
                       app.imageZAxis[1][0], app.imageZAxis[1][1],\
                       fill = "blue", width = 2)

# Draws scale on all axes.
def drawScale(app, canvas):
    for i in range(len(app.scalePoints)):
        point = app.scalePoints[i]
        tickMark = str(round(app.scale / 10 + point[0][0] + point[1][0]\
                       + point[2][0], int(-math.log(app.scale, 10) + 1)))
        imageX, imageY = app.imageScale[i]
        canvas.create_text(imageX, imageY, text = f"{tickMark}", \
                           font = "Arial 9")

# Makes all buttons for menu, help section, and grapher.
def makeButtons(app):
    app.menuButtons = []
    buttonText = [["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "(", ")", "."],\
                  ["x", "y", "+", "-", "*", "e", "\\pi"],\
                  ["/", "^{}", "\\sqrt{}", "\\sqrt[]{}", "\\frac{}{}"],\
                  ["\\sin{}", "\\cos{}", "\\tan{}", "\\ln{}", "\\log_{}{}"]]
    for i in range(13):
        app.menuButtons.append(Button(app.margin + i * (app.width - 2 * app.margin) // 13,\
                                  9 * (app.height - 2 * app.margin) // 16,\
                                  app.margin + (i + 1) * (app.width - 2 * app.margin) // 13,\
                                  5 * (app.height - 2 * app.margin) // 8,
                                  buttonText[0][i], "Arial 36"))
    for i in range(7):
        app.menuButtons.append(Button(app.margin + i * (app.width - 2 * app.margin) // 7,\
                                  5 * (app.height - 2 * app.margin) // 8,\
                                  app.margin + (i + 1) * (app.width - 2 * app.margin) // 7,\
                                  3 * (app.height - 2 * app.margin) // 4,
                                  buttonText[1][i], "Arial 36"))
    for i in range(1, 3):
        for j in range(5):
            app.menuButtons.append(Button(app.margin + j * (app.width - 2 * app.margin) // 5,\
                                      5 * (app.height - 2 * app.margin) // 8 + i * (app.height - 2 * app.margin) // 8,\
                                      app.margin + (j + 1) * (app.width - 2 * app.margin) // 5,\
                                      3 * (app.height - 2 * app.margin) // 4 + i * (app.height - 2 * app.margin) // 8,\
                                      buttonText[i + 1][j], "Arial 36"))
    app.menuButtons.append(Button(app.margin + 15 * (app.width - 2 * app.margin) // 16,\
                              7 * app.height // 16 - app.margin, app.width - app.margin,\
                              app.height // 2 - app.margin, ">", "Arial 32"))
    app.menuButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                       7 * app.height // 16 - app.margin, app.margin + 15 * (app.width - 2 * app.margin) // 16,\
                       app.height // 2 - app.margin, "<", "Arial 32"))
    app.menuButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                              3 * app.height // 8 - app.margin, app.width - app.margin,\
                              7 * app.height // 16 - app.margin, "Graph", "Arial 32"))
    app.menuButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                              app.height // 2 - app.margin, app.width - app.margin,\
                              9 * (app.height - 2 * app.margin) // 16, "Back", "Arial 32"))
    app.menuButtons.append(Button(app.margin, app.margin, app.margin + (app.width - 2 * app.margin) // 8,\
                                  (app.width - 2 * app.margin) // 8, "Help", "Arial 36"))
    app.graphButtons = []
    app.graphButtons.append(Button(app.margin + 13 * (app.width - 2 * app.margin) // 16,\
                                   7 * (app.height - 2 * app.margin) // 8,\
                                   app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                                   15 * (app.height - 2 * app.margin) // 16,\
                                   "<", "Arial 36"))
    app.graphButtons.append(Button(app.margin + 15 * (app.width - 2 * app.margin) // 16,\
                                   7 * (app.height - 2 * app.margin) // 8,\
                                   app.width - app.margin,\
                                   15 * (app.height - 2 * app.margin) // 16,\
                                   ">", "Arial 36"))
    app.graphButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                                   13 * (app.height - 2 * app.margin) // 16,\
                                   app.margin + 15 * (app.width - 2 * app.margin) // 16,\
                                   7 * (app.height - 2 * app.margin) // 8,\
                                   "^", "Arial 36"))
    app.graphButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8,\
                                   15 * (app.height - 2 * app.margin) // 16,\
                                   app.margin + 15 * (app.width - 2 * app.margin) // 16,\
                                   app.height - 2 * app.margin,\
                                   "v", "Arial 36"))
    graphText = [["d/dx", "Undo\nd/dx"], ["d/dy", "Undo\nd/dy"], ["+", "-"]]
    for i in range(2):
        for j in range(2):
            app.graphButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8 + j * (app.width - 2 * app.margin) // 16,\
                                           app.height // 2 + i * (app.height - 2 * app.margin) // 16 + i * (app.height - 2 * app.margin) // 32,\
                                           app.margin + 7 * (app.width - 2 * app.margin) // 8 + (j + 1) * (app.width - 2 * app.margin) // 16,\
                                           app.height // 2 + (i + 1) * (app.height - 2 * app.margin) // 16 + i * (app.height - 2 * app.margin) // 32,\
                                           graphText[i][j], "Arial 18"))
    for i in range(2):
        app.graphButtons.append(Button(app.margin + 7 * (app.width - 2 * app.margin) // 8 + i * (app.width - 2 * app.margin) // 16,\
                                           app.height // 2 + 2 * (app.height - 2 * app.margin) // 16 + 2 * (app.height - 2 * app.margin) // 32,\
                                           app.margin + 7 * (app.width - 2 * app.margin) // 8 + (i + 1) * (app.width - 2 * app.margin) // 16,\
                                           app.height // 2 + 3 * (app.height - 2 * app.margin) // 16 + 2 * (app.height - 2 * app.margin) // 32,\
                                           graphText[2][i], "Arial 36"))
    app.graphButtons.append(Button(app.margin, 15 * (app.height - 2 * app.margin) // 16,\
                                   app.margin + (app.width - 2 * app.margin) // 8,\
                                   app.height - 2 * app.margin, "Restart", "Arial 18"))
    app.helpBackButton = Button(app.margin, 15 * (app.height - 2 * app.margin) // 16,\
                                app.margin + (app.width - 2 * app.margin) // 8,\
                                app.height - 2 * app.margin, "Back", "Arial 36")

# Draws the starting menu.
def drawMenu(app, canvas):
    canvas.create_text(app.width // 2, app.height // 16, text = "3D Graphing Calculator", font = "Arial 48")
    canvas.create_text(app.width // 2, 3 * app.height // 16, text = "Enter a function of x and y!", font = "Arial 36")
    canvas.create_text(app.width // 2, 5 * app.height // 16, text = "f(x,y) = " + app.function[:app.pointer] + app.space + app.function[app.pointer:], font = "Arial 36")
    for button in app.menuButtons:
        button.drawButton(app, canvas)

# Determines which button was pressed.
def getButton(app, x, y):
    text = None
    if(app.help):
        return "Back"
    elif(not app.graph):
        for button in app.menuButtons:
            if(button.coordIn(x, y)):
                text = button.text
                break
        if(text == "<"):
            app.pointer = max(0, app.pointer - 1)
            return None
        elif(text == ">"):
            app.pointer = min(len(app.function), app.pointer + 1)
            return None
        elif(text == "Graph"):
            app.graph = True
    else:
        for button in app.graphButtons:
            if(button.coordIn(x, y)):
                return button.text
    return text

# Acts on button presses.
def mousePressed(app, event):
    button = getButton(app, event.x, event.y)
    if(button == "Back"):
        if(app.help):
            app.help = False
        else:
            app.function = app.function[:app.pointer - 1] + app.function[app.pointer:]
            app.pointer -= 1
    elif(button == "Graph"):
        try:
            app.timerDelay = 100
            app.function = clearLaTeXCommands(app.function)
            # NEW
            app.elements = betterSplit(app.function)
            makeAllDerivs(app)
            app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
            app.function = replaceVariables(app.function)
            app.function = evalLambda(app.function)
            # NEW
            prepPoints(app)
            allRotationOperations(app)
        except:
            appStarted(app)
    elif(button == "Help"):
        app.help = True
    elif(button is not None and not app.graph):
        app.function = app.function[:app.pointer] + button + app.function[app.pointer:]
        app.pointer += len(button)
    if(app.graph):
        if(button == "<"):
            app.theta -= math.pi / 36
        elif(button == ">"):
            app.theta += math.pi / 36
        elif(button == "^"):
            app.phi = max(math.pi / 5, app.phi - math.pi / 36)
        elif(button == "v"):
            app.phi = min(math.pi * 4 / 5, app.phi + math.pi / 36)
        elif(button == "+"):
            zoom(app, True)
        elif(button == "-"):
            zoom(app, False)
        elif(button == "d/dx"):
            app.derivative[0] = min(3, app.derivative[0] + 1)
            app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
            app.function = replaceVariables(app.function)
            app.function = evalLambda(app.function)
            prepPoints(app)
        elif(button == "Undo\nd/dx"):
            app.derivative[0] = max(0, app.derivative[0] - 1)
            app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
            app.function = replaceVariables(app.function)
            app.function = evalLambda(app.function)
            prepPoints(app)
        elif(button == "d/dy"):
            app.derivative[1] = min(3, app.derivative[0] + 1)
            app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
            app.function = replaceVariables(app.function)
            app.function = evalLambda(app.function)
            prepPoints(app)
        elif(button == "Undo\nd/dy"):
            app.derivative[1] = max(0, app.derivative[0] - 1)
            app.function = copy.deepcopy(app.derivs[app.derivative[0]][app.derivative[1]])
            app.function = replaceVariables(app.function)
            app.function = evalLambda(app.function)
            prepPoints(app)
        elif(button == "Restart"):
            appStarted(app)
        allRotationOperations(app)

# Only used to make the cursor blink while typing.
def timerFired(app):
    if(app.space == "|"):
        app.space = " "
    else:
        app.space = "|"

# Draws LaTeX Command Help section.
def drawHelp(app, canvas):
    canvas.create_text(app.width // 2, (app.height - 2 * app.margin) // 10, text = "LaTeX Command Help", font = "Arial 36")
    canvas.create_text(app.width // 2, (app.height - 2 * app.margin) // 5, text = "Fractions: \\frac{numerator}{denominator}", font = "Arial 28")
    canvas.create_text(app.width // 2, 3 * (app.height - 2 * app.margin) // 10, text = "Sine: \\sin{argument}", font = "Arial 28")
    canvas.create_text(app.width // 2, 2 * (app.height - 2 * app.margin) // 5, text = "Cosine: \\cos{argument}", font = "Arial 28")
    canvas.create_text(app.width // 2, (app.height - 2 * app.margin) // 2, text = "Tangent: \\tan{argument}", font = "Arial 28")
    canvas.create_text(app.width // 2, 3 * (app.height - 2 * app.margin) // 5, text = "Logarithms: \\log_{base}{argument} or \\ln{argument}", font = "Arial 28")
    canvas.create_text(app.width // 2, 7 * (app.height - 2 * app.margin) // 10, text = "Exponents: base^{exponent} or (base)^{exponent}", font = "Arial 28")
    canvas.create_text(app.width // 2, 4 * (app.height - 2 * app.margin) // 5, text = "Square Root: \\sqrt{argument}", font = "Arial 28")
    canvas.create_text(app.width // 2, 9 * (app.height - 2 * app.margin) // 10, text = "Nth Root: \\sqrt[n]{argument}", font = "Arial 28")
    app.helpBackButton.drawButton(app, canvas)

# Calls all drawing methods
def redrawAll(app, canvas):
    if(app.graph):
        drawPoints(app, canvas)
        drawAxes(app, canvas)
        drawScale(app, canvas)
        for button in app.graphButtons:
            button.drawButton(app, canvas)
    elif(app.help):
        drawHelp(app, canvas)
    else:
        drawMenu(app, canvas)

# Makes an empty matrix.
def newMatrix(rows, cols):
    return [([0] * cols) for row in range(rows)]

# Multiplies a matrix m1 by a scalar r.
def scalarMultiply(m1, r):
    rows = len(m1)
    cols = len(m1[0])
    result = newMatrix(rows, cols)
    for row in range(rows):
        for col in range(cols):
            result[row][col] = r * m1[row][col]
    return result

# Computes dot product of two vectors.
def dot(v1, v2):
    assert(len(v1) == len(v2))
    assert(len(v1[0]) == len(v2[0]) == 1)
    total = 0
    for i in range(len(v1)):
        total += v1[i][0] * v2[i][0]
    return total

# Computes cross product of two vectors.
def cross(v1, v2):
    assert(len(v1) == len(v2))
    assert(len(v1[0]) == len(v2[0]) == 1)
    resultX = v1[1][0] * v2[2][0] - v1[2][0] * v2[1][0]
    resultY = v1[2][0] * v2[0][0] - v1[0][0] * v2[2][0]
    resultZ = v1[0][0] * v2[1][0] - v1[1][0] * v2[0][0]
    return [[resultX], [resultY], [resultZ]]

# Returns start and end indices of outermost parentheses.
# If no parentheses, returns (-1,-1).
def findParentheses(expression, startIndex):
    total = None
    leftPars = "([{"
    rightPars = ")]}"
    firstParenthesis = None
    secondParenthesis = None
    for i in range(startIndex, len(expression)):
        if(isinstance(expression[i], str) and expression[i] in leftPars):
            if(firstParenthesis is None):
                firstParenthesis = i
                total = 0
            total += 1
        elif(isinstance(expression[i], str) and expression[i] in rightPars):
            total -= 1
        if (total == 0):
            secondParenthesis = i
            break
    if (firstParenthesis is secondParenthesis is None):
        return (-1, -1)
    leftPar = expression[firstParenthesis]
    rightPar = expression[secondParenthesis]
    return (firstParenthesis, secondParenthesis)

# Clears \frac{a}{b} and replaces with (a)/(b).
def clearFrac(expression):
    while "\\frac" in expression:
        fracIndex = expression.find("\\frac")
        firstPar, secondPar = findParentheses(expression, fracIndex)
        thirdPar, fourthPar = findParentheses(expression, secondPar + 1)
        numerator = expression[firstPar + 1:secondPar]
        denominator = expression[thirdPar + 1:fourthPar]
        expression = expression[:fracIndex] + "(" + numerator + ")/(" +\
                     denominator + ")" + expression[fourthPar + 1:]
    return expression

# Replaces \sqrt{n} with (n)^{1/2} and \sqrt[n]{a} with (a)^{1/(n)}.
def clearSqrt(expression):
    while "\\sqrt" in expression:
        sqrtIndex = expression.find("\\sqrt")
        firstPar, secondPar = findParentheses(expression, sqrtIndex)
        if(expression[firstPar] == "["):
            thirdPar, fourthPar = findParentheses(expression, secondPar + 1)
            exponent = "1/(" + expression[firstPar + 1:secondPar] + ")"
        else:
            thirdPar, fourthPar = firstPar, secondPar
            exponent = "1/2"
        base = expression[thirdPar + 1:fourthPar]
        expression = expression[:sqrtIndex] + "(" + base + ")^{" +\
                     exponent + "}" + expression[fourthPar + 1:]
    return expression

# Replaces \sin(x) with s(x).
def clearSine(expression):
    while "\\sin" in expression:
        sinIndex = expression.find("\\sin")
        firstPar, secondPar = findParentheses(expression, sinIndex)
        argument = expression[firstPar + 1:secondPar]
        expression = expression[:sinIndex] + "s(" + argument + ")"\
                     + expression[secondPar + 1:]
    return expression

# Replaces \cos(x) with c(x).
def clearCosine(expression):
    while "\\cos" in expression:
        cosIndex = expression.find("\\cos")
        firstPar, secondPar = findParentheses(expression, cosIndex)
        argument = expression[firstPar + 1:secondPar]
        expression = expression[:cosIndex] + "c(" + argument + ")"\
                     + expression[secondPar + 1:]
    return expression

# Replaces \tan(x) with t(x).
def clearTangent(expression):
    while "\\tan" in expression:
        tanIndex = expression.find("\\tan")
        firstPar, secondPar = findParentheses(expression, tanIndex)
        argument = expression[firstPar + 1:secondPar]
        expression = expression[:tanIndex] + "t(" + argument + ")"\
                     + expression[secondPar + 1:]
    return expression

# Replaces \pi with p.
def clearPi(expression):
    while "\\pi" in expression:
        piIndex = expression.find("\\pi")
        expression = expression[:piIndex] + "p" + expression[piIndex + 3:]
    return expression

# Replaces \log_{b}{a} with (a)_(b) and \ln{a} with (a)_(e).
def clearLog(expression):
    while "\\log" in expression:
        logIndex = expression.find("\\log")
        firstPar, secondPar = findParentheses(expression, logIndex)
        thirdPar, fourthPar = findParentheses(expression, secondPar + 1)
        base = expression[firstPar + 1:secondPar]
        argument = expression[thirdPar + 1:fourthPar]
        expression = expression[:logIndex] + "l(" + argument + ")_(" +\
                     base + ")" + expression[fourthPar + 1:]
    while "\\ln" in expression:
        lnIndex = expression.find("\\ln")
        firstPar, secondPar = findParentheses(expression, lnIndex)
        base = "e"
        argument = expression[firstPar + 1:secondPar]
        expression = expression[:lnIndex] + "l(" + argument + ")_(" +\
                     base + ")" + expression[secondPar + 1:]
    return expression

# Replaces \frac{a}{b}, \sqrt[n]{a}, \sin{a}, \cos{a}, \pi.
def clearLaTeXCommands(expression):
    expression = clearFrac(expression)
    expression = clearSqrt(expression)
    expression = clearSine(expression)
    expression = clearCosine(expression)
    expression = clearTangent(expression)
    expression = clearPi(expression)
    expression = clearLog(expression)
    return expression

# NEW STUFF
# Better version of splitExpression.
def betterSplit(expression):
    elements = [""] * 2 * len(expression)
    elemIndex = 0
    for i in range(len(expression)):
        char = expression[i]
        if(char not in " \t\n"):
            elements[elemIndex] += char
            if(i == len(expression) - 1):
                break
            nextChar = expression[i + 1]
            if(not sameType(char, nextChar)):
                elemIndex += 1
    elements = elements[:elemIndex + 1]
    elements = replaceMinus(elements)
    elements = insertMult(elements)
    return elements

# Organizes characters into types and returns type of given character.
def charType(char):
    types = {"number":"1234567890.",
             "minus":"-",
             "varConst":"xyep",
             "operator":"sctlr",
             "binaryOp":"+*/^",
             "multiArgSplit":"_",
             "lpar":"{([",
             "rpar":"})]"}
    for kind in types:
        if char in types[kind]:
            return kind

# Replaces minus signs with ["-1", "*"].
def replaceMinus(elements):
    minusIndex = 0
    while "-" in elements:
        minusIndex = elements.index("-", minusIndex)
        if(minusIndex == 0 or charType(elements[minusIndex - 1][0]) == "lpar"):
            elements = elements[:minusIndex] + ["-1", "*"] + elements[minusIndex + 1:]
        else:
            elements = elements[:minusIndex] + ["+", "-1", "*"] + elements[minusIndex + 1:]
    return elements

# Checks if two characters are of the same character-type.
def sameType(char, nextChar):
    type1 = charType(char)
    type2 = charType(nextChar)
    if(type1 == type2):
        if(type1 == "varConst" or type1 == "lpar" or type1 == "rpar"):
            return False
        else:
            return True
    else:
        return False

# Checks if a multiplication sign is required between two characters.
# Something like (x+y)(x+3) requires a * between )(.
def multRequired(type1, type2):
    if((type1 == "varConst" and type2 == "varConst") or\
       (type1 == "number" and type2 == "varConst") or\
       (type1 == "number" and type2 == "lpar") or\
       (type1 == "varConst" and type2 == "lpar") or\
       (type1 == "rpar" and type2 == "varConst") or\
       (type1 == "rpar" and type2 == "lpar") or\
       (type1 == "rpar" and type2 == "operator") or\
       (type1 == "number" and type2 == "operator") or\
       (type1 == "varConst" and type2 == "operator")):
        return True
    return False

# Inserts multiplication signs in places where they are required.
# Something like (xy+y)(x+3) is turned into (x*y+y)*(x+3).
def insertMult(elements):
    types = [charType(elements[i][0])for i in range(len(elements))]
    elemIndex = 0
    for j in range(len(types) - 1):
        type1 = types[j]
        type2 = types[j + 1]
        if(multRequired(type1, type2)):
            elements = elements[:elemIndex + 1] + ["*"] + elements[elemIndex + 1:]
            elemIndex += 1
        elemIndex += 1
    return elements

# Replaces e and pi with their values.
def replaceEPi(elements):
    for i in range(len(elements)):
        if(elements[i] == "e"):
            elements[i] = str(math.e)
        elif(elements[i] == "p"):
            elements[i] = str(math.pi)
    return elements

# Final step of order of operations, only addition is remaining.
def addLambda(elements):
    if(elements == []):
        return lambda x, y: 0
    if(len(elements) == 1):
        if(isinstance(elements[0], float)):
            return lambda x, y: elements[0]
        return elements[0]
    f1 = elements[0]
    f2 = elements[2]
    f3 = addLambda(elements[4:])
    if(isinstance(f1, float)):
        if(isinstance(f2, float)):
            f = lambda x, y: f1 + f2 + f3(x, y)
        else:
            f = lambda x, y: f1 + f2(x, y) + f3(x, y)
    else:
        if(isinstance(f2, float)):
            f = lambda x, y: f1(x, y) + f2 + f3(x, y)
        else:
            f = lambda x, y: f1(x, y) + f2(x, y) + f3(x, y)
    return f

# Replaces variables with lambdas that output those variables
# Converts constants from strings to floats.
def replaceVariables(elements):
    elements = replaceEPi(elements)
    for i in range(len(elements)):
        if(elements[i] == "x"):
            elements[i] = lambda x, y: x
        elif(elements[i] == "y"):
            elements[i] = lambda x, y: y
        elif(charType(elements[i][0]) == "number" or charType(elements[i][0]) == "minus"):
            elements[i] = float(elements[i])
    return elements

# Computes multiplication and division lambdas.
def multDivLambda(elements):
    if("*" not in elements and "/" not in elements):
        return elements
    if("*" in elements):
        multIndex = elements.index("*")
    else:
        multIndex = len(elements)
    if("/" in elements):
        divIndex = elements.index("/")
    else:
        divIndex = len(elements)
    opIndex = min(multIndex, divIndex)
    f1 = elements[opIndex - 1]
    f2 = elements[opIndex + 1]
    if(opIndex == multIndex):
        if(isinstance(f1, float)):
            if(isinstance(f2, float)):
                f = lambda x, y: f1 * f2
            else:
                f = lambda x, y: f1 * f2(x, y)
        else:
            if(isinstance(f2, float)):
                f = lambda x, y: f1(x, y) * f2
            else:
                f = lambda x, y: f1(x, y) * f2(x, y)
    else:
        if(isinstance(f1, float)):
            if(isinstance(f2, float)):
                f = lambda x, y: f1 / f2
            else:
                f = lambda x, y: f1 / f2(x, y)
        else:
            if(isinstance(f2, float)):
                f = lambda x, y: f1(x, y) / f2
            else:
                f = lambda x, y: f1(x, y) / f2(x, y)
    return multDivLambda(elements[:opIndex - 1] + [f] + elements[opIndex + 2:])

# Computes exponent lambdas.
def expLambda(elements):
    if("^" not in elements and "r" not in elements):
        return elements
    if("^" in elements):
        expIndex = elements.index("^")
    else:
        expIndex = len(elements)
    if("r" in elements):
        rIndex = elements.index("r")
    else:
        rIndex = len(elements)
    opIndex = min(expIndex, rIndex)
    if(opIndex == expIndex):
        base = elements[opIndex - 1]
        exp = elements[opIndex + 1]
    else:
        base = elements[opIndex + 1]
        exp = elements[opIndex + 3] 
    if(isinstance(base, float)):
        if(isinstance(exp, float)):
            f = lambda x, y: math.pow(base, exp)
        else:
            f = lambda x, y: math.pow(base, exp(x, y))
    else:
        if(isinstance(exp, float)):
            f = lambda x, y: math.pow(base(x, y), exp)
        else:
            f = lambda x, y: math.pow(base(x, y), exp(x, y))
    if(opIndex == expIndex):
        return expLambda(elements[:opIndex - 1] + [f] + elements[opIndex + 2:])
    return expLambda(elements[:opIndex] + [f] + elements[opIndex + 4:])

# Computes sine lambdas.
def sinLambda(elements):
    if ("s" not in elements):
        return elements
    sinIndex = elements.index("s")
    f1 = elements[sinIndex + 1]
    if(isinstance(f1, float)):
        f = lambda x, y: math.sin(f1)
    else:
        f = lambda x, y: math.sin(f1(x, y))
    return sinLambda(elements[:sinIndex] + [f] + elements[sinIndex + 2:])

# Computes cosine lambdas.
def cosLambda(elements):
    if ("c" not in elements):
        return elements
    cosIndex = elements.index("c")
    f1 = elements[cosIndex + 1]
    if(isinstance(f1, float)):
        f = lambda x, y: math.cos(f1)
    else:
        f = lambda x, y: math.cos(f1(x, y))
    return cosLambda(elements[:cosIndex] + [f] + elements[cosIndex + 2:])

# Computes tangent lambdas.
def tanLambda(elements):
    if ("t" not in elements):
        return elements
    tanIndex = elements.index("t")
    f1 = elements[tanIndex + 1]
    if(isinstance(f1, float)):
        f = lambda x, y: math.tan(f1)
    else:
        f = lambda x, y: math.tan(f1(x, y))
    return tanLambda(elements[:tanIndex] + [f] + elements[tanIndex + 2:])

# Computes logarithm lambdas.
def logLambda(elements):
    if("l" not in elements):
        return elements
    logIndex = elements.index("l")
    arg = elements[logIndex + 1]
    base = elements[logIndex + 3]
    if(isinstance(arg, float)):
        if(isinstance(base, float)):
            return lambda x, y: math.log(arg, base)
        else:
            f = lambda x, y: math.log(arg, base(x, y))
    else:
        if(isinstance(base, float)):
            f = lambda x, y: math.log(arg(x, y), base)
        else:
            f = lambda x, y: math.log(arg(x, y), base(x, y))
    return logLambda(elements[:logIndex] + [f] + elements[logIndex + 4:])

# Computes lambda function for entire expression.
def evalLambda(elements):
    subStart, subEnd = findParentheses(elements, 0)
    if((subStart, subEnd) != (-1, -1)):
        replacement = evalLambda(elements[subStart + 1:subEnd])
        elements = elements[:subStart] + [replacement] + elements[subEnd + 1:]
        return evalLambda(elements)
    return evalLambdaNoPars(elements)

# Computes lambda function for expression without parentheses.
def evalLambdaNoPars(elements):
    elements = sinLambda(elements)
    elements = cosLambda(elements)
    elements = tanLambda(elements)
    elements = logLambda(elements)
    elements = expLambda(elements)
    elements = multDivLambda(elements)
    return addLambda(elements)

# Takes derivative.
def deriv(elements, dVar):
    if(dVar not in elements):
        return ["0"]
    elements = removeUselessPars(elements)
    if(elements == []):
        return ["0"]
    split = derivSplit(elements, "+")
    if(split[0] == elements):
        split = derivSplit(elements, "*/")
        if(split[0] == elements):
            split = derivSplit(elements, "^")
            if(split[0] == elements):
                return derivFunc(elements, dVar)
            return derivExp(elements, dVar)
        return derivMultDiv(elements, dVar)
    return derivAdd(split, dVar)

# Takes derivative of addition of functions.
def derivAdd(split, dVar):
    result = ["0"]
    if(split == []):
        return result
    result = result + ["+"]
    result = result + deriv(split[0], dVar) + ["+"]
    result = result + derivAdd(split[2:], dVar)
    return ["("] + result + [")"]

# Takes derivative of multiplication/division of functions.
def derivMultDiv(elements, dVar):
    split = derivSplit(elements, "*/")
    result = ["0"]
    if(split[0] == elements):
        return deriv(elements)
    firstPart = deriv(split[0], dVar) + ["*"] + elements[len(split[0]) + 1:]
    secondPart = split[0] + ["*"] + deriv(elements[len(split[0]) + 1:], dVar)
    if(split[1] == "*"):
        return firstPart + ["+"] + secondPart
    numerator = ["("] + firstPart + ["+", "-1", "*"] + secondPart + [")"]
    denominator = ["(", "("] + elements[len(split[0]) + 1:] + [")", "^", "2", ")"]
    return ["("] + numerator + ["/"] + denominator + [")"]

# Takes derivative of exponentials.
def derivExp(elements, dVar):
    split = derivSplit(elements, "^")
    result = ["0"]
    if(split[0] == elements):
        return deriv(elements)
    arg = removeUselessPars(split[0])
    exp = removeUselessPars(split[2])
    #if(len(arg) == 1):
    if(dVar not in exp):
        return ["(", "("] + exp + [")", "*", "("] + arg + [")", "^", "("] + exp + ["+", "-1", "*", "1", ")"] + ["*", "("] + deriv(arg, dVar) + [")", ")"]
    if(dVar not in arg):
        if(len(arg) == 1 and arg[0] == "e"):
            return ["(", "("] + arg + [")", "^", "("] + exp + [")", "*", "("] + deriv(exp, dVar) + [")", ")"]
        return ["(", "("] + arg + [")", "^", "("] + exp + [")", "*"] + deriv(exp, dVar) + ["*", "l", "("] + arg + [")", "_", "e", ")"]
    firstPart = ["("] + split[2] + [")"] + ["*"] + deriv(split[0], dVar) + ["/"] + ["("] + split[0] + [")"]
    secondPart = deriv(split[2], dVar) + ["*"] + ["l", "("] + split[0] + [")" ,"_", "(", "e", ")"]
    return ["("] + elements + ["*", "("] + firstPart + ["+"] + secondPart + [")", ")"]

# Takes derivative of remaining functions, like sine, cosine, tangent, and logs.
def derivFunc(elements, dVar):
    if(elements == [dVar]):
        return ["(", "1", ")"]
    elif(elements[0] == "s"):
        return ["(", "c"] + elements[1:] + [")", "*", "("] + deriv(elements[2:-1], dVar) + [")"]
    elif(elements[0] == "c"):
        return ["(", "-1", "*", "s"] + elements[1:] + [")", "*", "("] + deriv(elements[2:-1], dVar) + [")"]
    elif(elements[0] == "t"):
        denominator = ["(", "c"] + elements[1:] + [")"]
        return ["(", "1", "/", "(", "("] + denominator + [")", "^", "2", ")"] + ["*", "("] + deriv(elements[2:-1], dVar) + [")", ")"]
    elif(elements[0] == "l"):
        firstPar, secondPar = findParentheses(elements, 0)
        arg = removeUselessPars(elements[firstPar:secondPar + 1])
        base = removeUselessPars(elements[secondPar + 2:])
        if(base == ["e"]):
            return ["(", "(", "1", "/", "("] + arg + [")", ")", "*", "("] + deriv(arg, dVar) + [")", ")"]
        return ["("] + deriv(["(", "l", "("] + arg + [")", "_", "(", "e", ")", ")", "/", "(", "l", "("] + base + [")", "_", "(", "e", ")", ")"], dVar) + [")"]

# Determines the parentheses-depth of each element in the expression.
def levels(elements):
    levelList = [0] * len(elements)
    level = 0
    for i in range(len(elements)):
        if(elements[i] in "{[("):
            level += 1
            levelList[i] = level
        elif(elements[i] in "}])"):
            levelList[i] = level
            level -= 1
        else:
            levelList[i] = level
    return levelList

# Finds out where to split elements into subexpressions.
def splitLocations(elements):
    levelList = levels(elements)
    split = ["0"] * len(elements)
    for i in range(len(elements)):
        if(levelList[i] == 0):
            if(elements[i] == "+"):
                split[i] = "+"
            elif(elements[i] == "*"):
                split[i] = "*"
            elif(elements[i] == "/"):
                split[i] = "/"
            elif(elements[i] == "^"):
                split[i] = "^"
    return split

# Splits expression into subexpressions according to the split sign.
def derivSplit(elements, splitSigns):
    split = splitLocations(elements)
    first = 0
    second = 0
    splitElements = []
    for i in range(len(split)):
        if(split[i] in splitSigns):
            segment = elements[first:second]
            first = second + 1
            splitElements.append(segment)
            splitElements.append(split[i])
        second += 1
    splitElements.append(elements[first:])
    return splitElements

# Removes useless parentheses surrounding expression.
def removeUselessPars(elements):
    if(elements == []):
        return elements
    if(elements[0] in "{[("):
        firstPar, secondPar = findParentheses(elements, 0)
        if(secondPar == len(elements) - 1):
            return removeUselessPars(elements[1:-1])
    return elements

runApp(width = 800, height = 800)