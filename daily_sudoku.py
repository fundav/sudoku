from copy import deepcopy
from datetime import date
from itertools import combinations, product
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep
import os


print("Starting browser...")
firefox_options = Options()
#firefox_options.add_argument('-headless')
#firefox_options.add_argument("--width=1500")
#firefox_options.add_argument("--height=800")
driver = webdriver.Firefox(options=firefox_options) 

# Get today's date
today = date.today()
todayDate = f"{today.month:02d}{today.day:02d}"

def saveSolvedPuzzle(level, date):
    # Saves a screenshot of the solved puzzle
    dir_path = f"{os.path.dirname(os.path.realpath(__file__))}\\solved_puzzles\\sudoku\\"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    name = f"ss{level}_{date}.png"
    driver.save_screenshot(dir_path+name)

def sendSolvedOutput():
    # Updates the website with the solved puzzle
    start = 0
    for i in range(82):
        if (i % 9) == 0:
            start += 1
        if i != 81:
            string = f"BBsudokuinputA{(10+(i+start))}"
            id = driver.find_element(By.ID, string)
            value = id.get_attribute("value")
            if value == "":
                numToSend = puzzle[i//9][i%9]
                id.send_keys(numToSend)

def doLockedSetsPart(size):
    # *** Checks rows ***
    for r in range(9):
        # Imagine combinations([[4,7],[4,7],[2,4,8],[1,5,7]], 2)
        # That would give [([4, 7], [4, 7]), ([4, 7], [2, 4, 8]), ([4, 7], [1, 5, 7]), ([4, 7], [2, 4, 8]), ([4, 7], [1, 5, 7]), ([2, 4, 8], [1, 5, 7])]
        # The main idea being we will look for valid groups/pairs (in this case the 47 47) 
        # and once we've found one eliminate (4 and 7) from other comments/candidates
        possibleCombos = list(combinations(comments[r], size))
        for combo in possibleCombos:
            # combo could be ([4, 7], [4, 7])
            comboSet = set().union(*combo)
            # comboSet would give {4, 7} (if combo was ([4, 7], [1, 5, 7]) then comboSet would be {1, 4, 5, 7})
            if (([] not in combo) and (len(comboSet) == size)):
                for i in range(9):
                    # So don't touch the actual [4, 7]
                    if comments[r][i] not in combo:
                        # Remove as needed
                        for item in comboSet:
                            if item in comments[r][i]:
                                comments[r][i].remove(item)
                                print(comments)
    


    # *** Checks col ***
    tempComments = convertToCol(comments)
    for c in range(9):
        possibleCombos = list(combinations(tempComments[c], size))
        for combo in possibleCombos:
            comboSet = set().union(*combo)
            if (([] not in combo) and (len(comboSet) == size)):
                for i in range(9):
                    if comments[i][c] not in combo:
                        for item in comboSet:
                            if item in comments[i][c]:
                                comments[i][c].remove(item)
                                print(comments)


    
    # *** Checks box ***
    tempComments = convertToBox(comments)
    for b in range(9):
        possibleCombos = list(combinations(tempComments[b], size))
        for combo in possibleCombos:
            comboSet = set().union(*combo)
            if (([] not in combo) and (len(comboSet) == size)):
                for r,c in product(range(9), repeat=2):
                    if ((3*(r//3) + (c//3) == b) and (comments[r][c] not in combo)):
                        for item in comboSet:
                            if item in comments[r][c]:
                                comments[r][c].remove(item)
                                print(comments)

def doLockedSets():
    oldComments = deepcopy(comments)
    doLockedSetsPart(2)
    doLockedSetsPart(3)
    doLockedSetsPart(4)
    if (oldComments != comments):
        doLockedSets()

def doForcedMovesPart():
    # *** Checks rows ***
    for r in range(9):
        #Turns a row of comments into a string
        rowAsString = ""
        for i in range(9):
            rowAsString += "".join(list(map(str, comments[r][i])))
        
        #For every number from 1 to 9 checks if that number only appears once in the row
        for i in range(1, 10):
            if (rowAsString.count(str(i)) == 1):
                for x in range(9):
                    if i in comments[r][x]:
                        puzzle[r][x] = i
                        comments[r][x].clear()
                        correctComments()
                        printPuzzle()
                        print(comments)
    #Same logic applies below but for col and box
    


    # *** Checks col ***
    for c in range(9):
        colAsString = ""
        for i in range(9):
            colAsString += "".join(list(map(str, comments[i][c])))

        for i in range(1, 10):
            if (colAsString.count(str(i)) == 1):
                for x in range(9):
                    if i in comments[x][c]:
                        puzzle[x][c] = i
                        comments[x][c].clear()
                        correctComments()
                        printPuzzle()
                        print(comments)
    


    # *** Checks box ***
    for b in range(9):
        boxAsString = ""
        for r in range(9):
            for c in range(9):
                if (3*(r//3) + (c//3) == b):
                    boxAsString += "".join(list(map(str, comments[r][c])))

        for i in range(1, 10):
            if (boxAsString.count(str(i)) == 1):
                for r in range(9):
                    for c in range(9):
                        if ((3*(r//3) + (c//3) == b) and (i in comments[r][c])):
                            puzzle[r][c] = i
                            comments[r][c].clear()
                            correctComments()
                            printPuzzle()
                            print(comments)

def doForcedMoves():
    oldComments = deepcopy(comments)
    doForcedMovesPart()
    if (oldComments != comments):
        doForcedMoves()

def checkComplete():
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0:
                return False
    return True

#Makes the appropiate changes to comments after other changes have been made 
def correctComments():
    for r in range(9):
        for c in range(9):
            i = 0
            while (i < len(comments[r][c])):
                if (not validate(comments[r][c][i], r, c)):
                    comments[r][c].pop(i)
                    i -= 1
                i += 1

#Solves all comments that have only one possible answer
def doCommentSinglesPart():
    for r in range(9):
        for c in range(9):
            if len(comments[r][c]) == 1:
                puzzle[r][c] = comments[r][c].pop(0)
                correctComments()
                printPuzzle()
                print(comments)

def doCommentSingles():
    oldComments = deepcopy(comments)
    doCommentSinglesPart()
    if (oldComments != comments):
        doCommentSingles()

def convertToBox(temp):
    newTemp = [[] for i in range(9)]
    for r,c in product(range(9), repeat=2):
        b = 3*(r//3) + (c//3)
        newTemp[b].append(temp[r][c])
    return newTemp

def convertToCol(temp):
    return list(map(list, zip(*temp)))

#Checks if a number could be placed in a specific position according to sudoku rules
def validate(num, r, c):
    b = 3*(r//3) + (c//3)
    if num in puzzle[r]:
        return False
    elif num in convertToCol(puzzle)[c]:
        return False
    elif num in convertToBox(puzzle)[b]:
        return False
    return True

def createComments():
    orgComments = []
    for r in range(9):
        commentsPart = []
        for c in range(9):
            comment = []
            for i in range(1, 10):
                if (puzzle[r][c] == 0 and validate(i, r, c)):
                    comment.append(i)
            commentsPart.append(comment)
        orgComments.append(commentsPart)
    return orgComments

def printPuzzle():
    # Prints the Sudoku puzzle in a human-readable format
    print()
    for r in range(9):
        for c in range(9):
            # Replace 0s with spaces for an empty look
            print(str(puzzle[r][c]).replace("0", " "), end="")
            if (c+1) % 3 == 0:
                print("|", end="")
        if (r+1) % 3 == 0:
            print("\n------------", end="")
        print()
    print()

def getSudokuInput(level, date):
    # Construct the URL for the Sudoku puzzle
    url = "https://www.brainbashers.com/showsudoku.asp?date="+str(date)+"&diff="+str(level)
    driver.get(url)
    driver.add_cookie({"name" : "DarkMode", "value" : "DarkModeOn"})
    driver.get(url)

    # Scrape the puzzle grid from the website
    websitePuzzle = []

    web_puzz_part = [] #Each "row"
    start = 0
    for i in range(82):
        if (i % 9) == 0:
            start += 1
            websitePuzzle.append(web_puzz_part)
            web_puzz_part = []
        if i != 81:
            string = f"BBsudokuinputA{(10+(i+start))}"
            id = driver.find_element(By.ID, string)
            value = id.get_attribute("value")
            if value == "":
                value = 0
            value = int(value)
            web_puzz_part.append(value)
    websitePuzzle.pop(0) # Remove the empty list at the beginning
    return websitePuzzle

def solveSudoku(level, date):
    #Solves a Sudoku puzzle from brainbashers.com based on the given difficulty and date
    global puzzle
    global comments

    isComplete = False
    puzzle = getSudokuInput(level, date)
    comments = createComments()
    printPuzzle()
    print(comments)

    # Starts applying techniques and then stops once completed
    for i in range(100): #Placeholder
        if (isComplete):
            break
        doCommentSingles()
        doForcedMoves()
        doLockedSets()
        printPuzzle()
        isComplete = checkComplete()
    
    sendSolvedOutput()
    saveSolvedPuzzle(level, date)

# Runs the solver for different difficulty levels based on today's date.
solveSudoku(1, todayDate)
solveSudoku(2, todayDate)
solveSudoku(3, todayDate)
solveSudoku(4, todayDate)

sleep(5)
driver.close()