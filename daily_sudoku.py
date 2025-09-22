from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import os
from datetime import date
import time
import calendar

print("Starting browser...")
firefox_options = Options()
# firefox_options.add_argument('-headless')
# firefox_options.add_argument("--width=1500")
# firefox_options.add_argument("--height=800")
driver = webdriver.Firefox(options=firefox_options)

# Get today's date and format it for the URL
today = date.today()
day_of_month = str(today.day)
if len(str(today.day)) == 1:
    day_of_month = "0" + str(today.day)
formatted_date = str(today.month) + day_of_month

puzzle = []
stop_row = False
stop_column = False
stop_commeting = False
candidates = []

def solve_sudoku(difficulty_level, puzzle_date):
    """
    Solves a Sudoku puzzle from brainbashers.com based on the given difficulty and date
    difficulty_level: The difficulty level of the puzzle (1 for Very Easy, etc.)
    puzzle_date: The date of the puzzle in MMdd format
    """
    global puzzle
    global stop_row
    global stop_column
    global stop_commeting
    global candidates

    # Construct the URL for the Sudoku puzzle
    # url = "https://www.brainbashers.com/showsudoku.asp?date=" + str(puzzle_date) + "&diff=" + str(difficulty_level)
    url = "https://www.brainbashers.com/showsudoku.asp?date=1123&diff=1"

    # Load the page and enable dark mode
    driver.get(url)
    driver.add_cookie({"name": "DarkMode", "value": "DarkModeOn"})
    driver.get(url)

    # Scrape the puzzle grid from the website
    website_puzzle_grid = []
    current_row = []
    start_index = 0
    for i in range(82):
        if (i % 9) == 0:
            start_index += 1
            website_puzzle_grid.append(current_row)
            current_row = []
        if i != 81:
            # The IDs are in the format "BBsudokuinputA10", "BBsudokuinputA11", etc.
            element_id = "BBsudokuinputA" + str((10 + (i + start_index)))
            try:
                puzzle_cell = driver.find_element(By.ID, element_id)
                value = puzzle_cell.get_attribute("value")
                if value == "":
                    value = 0
                else:
                    value = int(value)
                current_row.append(value)
            except Exception as e:
                print(f"Error finding element with ID {element_id}: {e}")
                # Append a placeholder to avoid breaking the grid structure
                current_row.append(0)

    website_puzzle_grid.pop(0)  # Remove the empty list at the beginning
    print(website_puzzle_grid)

    puzzle = website_puzzle_grid

    def print_puzzle():
        # Prints the Sudoku puzzle in a human-readable format
        print()
        for i in range(9):
            for x in range(9):
                # Replace 0s with spaces for an empty look
                print(str(puzzle[i][x]).replace("0", " "), end="")
                if (x + 1) % 3 == 0:
                    print("|", end="")
            if (i + 1) % 3 == 0:
                print()
                print("------------", end="")
            print()
        print()

    def check_naked_singles_in_columns():
        row_failures = 0
        column_failures = 0
        parts = [1, 2, 3] # Represents the three big columns of 3 small columns each
        for part in parts:
            part_index = (part - 1)
            numbers_to_check = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for number in numbers_to_check:
                cells_in_column = []
                box_locations = []
                for row_index in range(len(puzzle)):
                    def get_box_row():
                        # Determines the row of the 3x3 box a cell belongs to
                        if row_index < 3:
                            box_locations.append(1)
                        elif row_index < 6:
                            box_locations.append(2)
                        else:
                            box_locations.append(3)

                    # Check cells in the first column of the current part
                    if (puzzle[row_index][0 + (3 * part_index)] == number):
                        cells_in_column.append(1)
                        get_box_row()
                    # Check cells in the second column of the current part
                    if (puzzle[row_index][1 + (3 * part_index)] == number):
                        cells_in_column.append(2)
                        get_box_row()
                    # Check cells in the third column of the current part
                    if (puzzle[row_index][2 + (3 * part_index)] == number):
                        cells_in_column.append(3)
                        get_box_row()

                if len(cells_in_column) == 2:
                    # find the missing box and column where it must go.
                    remaining_box = 6 - box_locations[0] - box_locations[1]
                    remaining_column = 6 - cells_in_column[0] - cells_in_column[1]
                    
                    possible_rows = []
                    # Check for empty cells in the determined row of the missing box and column
                    if puzzle[0 + ((remaining_box - 1) * 3)][(remaining_column - 1) + (3 * part_index)] == 0:
                        if number not in puzzle[0 + ((remaining_box - 1) * 3)]:
                            possible_rows.append(1 + ((remaining_box - 1) * 3))
                    if puzzle[1 + ((remaining_box - 1) * 3)][(remaining_column - 1) + (3 * part_index)] == 0:
                        if number not in puzzle[1 + ((remaining_box - 1) * 3)]:
                            possible_rows.append(2 + ((remaining_box - 1) * 3))
                    if puzzle[2 + ((remaining_box - 1) * 3)][(remaining_column - 1) + (3 * part_index)] == 0:
                        if number not in puzzle[2 + ((remaining_box - 1) * 3)]:
                            possible_rows.append(3 + ((remaining_box - 1) * 3))

                    # If there's only one possible place, fill it in.
                    if len(possible_rows) == 1:
                        print(f"Place {number}, at row {possible_rows[0]} and column {remaining_column + (3 * part_index)}")
                        puzzle[(possible_rows[0] - 1)][(remaining_column - 1) + (3 * part_index)] = number
                        print()
                        print_puzzle()
                    else:
                        row_failures += 1
                else:
                    column_failures += 1
        
        # Check to see if the function has stopped finding new numbers
        if len(cells_in_column) == 3:
            global stop_column
            stop_column = True

    def check_naked_singles_in_rows():
        all_columns = []
        for col_index in range(9):
            column_values = []
            for row_index in range(len(puzzle)):
                column_values.append(puzzle[row_index][col_index])
            all_columns.append(column_values)

        row_failures = 0
        column_failures = 0
        parts = [1, 2, 3] # Represents the three big rows of 3 small rows each
        for part in parts:
            part_index = (part - 1)
            numbers_to_check = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            for number in numbers_to_check:
                cells_in_row = []
                box_locations = []
                for row_sub_index in range(int(len(puzzle) / 3)):
                    for col_sub_index in range(len(puzzle[(row_sub_index + (3 * part_index))])):
                        def get_box_column():
                            # Determines the column of the 3x3 box a cell belongs to
                            if col_sub_index < 3:
                                box_locations.append(1)
                            elif col_sub_index < 6:
                                box_locations.append(2)
                            else:
                                box_locations.append(3)

                        if (puzzle[(row_sub_index + (3 * part_index))][col_sub_index] == number):
                            cells_in_row.append(row_sub_index + 1)
                            get_box_column()
                
                if len(cells_in_row) == 2:
                    # find the missing box and row where it must go.
                    remaining_box = 6 - box_locations[0] - box_locations[1]
                    remaining_row = 6 - cells_in_row[0] - cells_in_row[1]

                    possible_columns = []
                    # Check for empty cells in the determined column of the missing box and row
                    if puzzle[(remaining_row - 1) + (3 * part_index)][0 + ((remaining_box - 1) * 3)] == 0:
                        if number not in all_columns[(remaining_row - 1) + (3 * part_index)]:
                            possible_columns.append(1 + ((remaining_box - 1) * 3))
                    if puzzle[(remaining_row - 1) + (3 * part_index)][1 + ((remaining_box - 1) * 3)] == 0:
                        if number not in all_columns[(remaining_row - 1) + (3 * part_index)]:
                            possible_columns.append(2 + ((remaining_box - 1) * 3))
                    if puzzle[(remaining_row - 1) + (3 * part_index)][2 + ((remaining_box - 1) * 3)] == 0:
                        if number not in all_columns[(remaining_row - 1) + (3 * part_index)]:
                            possible_columns.append(3 + ((remaining_box - 1) * 3))

                    # If there's only one possible place, fill it in.
                    if len(possible_columns) == 1:
                        print(f"Place {number}, at row {remaining_row + (3 * part_index)} and column {possible_columns[0]}")
                        puzzle[(remaining_row - 1) + (3 * part_index)][(possible_columns[0] - 1)] = number
                        print()
                        print_puzzle()
                    else:
                        column_failures += 1
                else:
                    row_failures += 1
        
        # Check to see if the function has stopped finding new numbers
        if len(cells_in_row) == 3:
            global stop_row
            stop_row = True

    def apply_x_wing_strategy(first_unit, second_unit, candidate_list):
        """
        X-Wing strategy
        first_unit (list): A list of lists representing a group of cells (e.g., boxes)
        second_unit (list): A list of lists representing another group of cells (e.g., columns)
        candidate_list (list): The list of all candidates for each cell
        
        The updated list of candidates
        """
        for number_to_check in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            for i in range(len(first_unit)):
                for j in range(len(second_unit)):
                    # Combine the candidate positions from both units
                    combined_positions = first_unit[i] + second_unit[j]
                    
                    # Find candidates that appear in both units
                    common_candidates = []
                    positions_to_use_later = []
                    for y in range(len(combined_positions)):
                        current_pos = combined_positions[y]
                        if combined_positions.count(current_pos) == 2 and (candidate_list[current_pos] not in common_candidates):
                            common_candidates.append(candidate_list[current_pos])
                            positions_to_use_later.append(current_pos)

                    # Count how many of the `first_unit` cells have the number as a candidate
                    count_in_first = 0
                    for y in range(len(first_unit[i])):
                        current_pos = first_unit[i][y]
                        if number_to_check in candidate_list[current_pos]:
                            count_in_first += 1

                    # Count how many of the `combined_positions` have the number as a candidate
                    count_in_combined = 0
                    for y in range(len(common_candidates)):
                        if number_to_check in common_candidates[y]:
                            count_in_combined += 1

                    # If the number of candidates for `number_to_check` is the same in both sets
                    # and is greater than 1, it means the candidates are confined.
                    if count_in_combined == count_in_first and (count_in_first > 1):
                        # Eliminate the number from the `second_unit`'s candidates,
                        # but only if it's not one of the confined cells.
                        for y in range(len(second_unit[j])):
                            current_pos = second_unit[j][y]
                            if number_to_check in candidate_list[current_pos] and (current_pos not in positions_to_use_later):
                                candidate_list[current_pos].remove(number_to_check)
        return candidate_list

    def create_candidate_list():
        global puzzle
        global candidates

        # Re-organize the puzzle into rows, boxes, and columns for easy lookup
        rows = puzzle
        boxes = []
        columns = []
        for y in range(9):
            box = []
            column = []
            x_high = 3 * ((y % 3) + 1)
            x_low = (3 * ((y % 3) + 1)) - 3
            y_high = 3 * ((y // 3) + 1)
            y_low = (3 * ((y // 3) + 1)) - 3

            for row_index in range(len(puzzle)):
                column.append(puzzle[row_index][y])
                for col_index in range(len(puzzle)):
                    if x_low <= col_index < x_high and y_low <= row_index < y_high:
                        box.append(puzzle[row_index][col_index])
            boxes.append(box)
            columns.append(column)

        # Generate a list of numbers that are already in the row, column, or box
        excluded_numbers = []
        for row_index in range(len(puzzle)):
            for col_index in range(len(puzzle)):
                if puzzle[row_index][col_index] == 0:
                    excl_set = set()
                    excl_set.update(columns[col_index])
                    excl_set.update(rows[row_index])
                    box_set = ((row_index // 3) * 3) + (col_index // 3)
                    excl_set.update(boxes[box_set])
                    
                    comment = [num for num in excl_set if num != 0]
                    excluded_numbers.append(comment)
                else:
                    excluded_numbers.append([1, 2, 3, 4, 5, 6, 7, 8, 9]) # Placeholder for filled cells

        # Create the final list of candidates by excluding the numbers found above
        candidates = []
        for excl_list in excluded_numbers:
            candidate_list = [i for i in [1, 2, 3, 4, 5, 6, 7, 8, 9] if i not in excl_list]
            candidates.append(candidate_list)

    def update_and_solve_with_candidates():
        global puzzle
        global candidates
        
        # Re-generate the candidate list based on the current state of the puzzle
        comments = []
        rows = puzzle
        boxes = []
        columns = []
        for y in range(9):
            box = []
            column = []
            x_high = 3 * ((y % 3) + 1)
            x_low = (3 * ((y % 3) + 1)) - 3
            y_high = 3 * ((y // 3) + 1)
            y_low = (3 * ((y // 3) + 1)) - 3
            for i in range(len(puzzle)):
                column.append(puzzle[i][y])
                for x in range(len(puzzle)):
                    if x_low <= x < x_high and y_low <= i < y_high:
                        box.append(puzzle[i][x])
            boxes.append(box)
            columns.append(column)

        for i in range(len(puzzle)):
            for x in range(len(puzzle)):
                if puzzle[i][x] == 0:
                    comment = []
                    excl_set = set()
                    excl_set.update(columns[x])
                    excl_set.update(rows[i])
                    box_set = ((i // 3) * 3) + (x // 3)
                    excl_set.update(boxes[box_set])
                    comment = [num for num in excl_set if num != 0]
                    comments.append(comment)
                else:
                    comments.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        # Refine the candidates by removing newly-found numbers
        for i in range(len(candidates)):
            for x in range(len(comments[i])):
                if comments[i][x] in candidates[i]:
                    candidates[i].remove(comments[i][x])

        # Define the indices for rows, boxes, and columns for easy iteration
        rows_indices = [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12, 13, 14, 15, 16, 17], [18, 19, 20, 21, 22, 23, 24, 25, 26],
                        [27, 28, 29, 30, 31, 32, 33, 34, 35], [36, 37, 38, 39, 40, 41, 42, 43, 44], [45, 46, 47, 48, 49, 50, 51, 52, 53],
                        [54, 55, 56, 57, 58, 59, 60, 61, 62], [63, 64, 65, 66, 67, 68, 69, 70, 71], [72, 73, 74, 75, 76, 77, 78, 79, 80]]

        boxes_indices = [[0, 1, 2, 9, 10, 11, 18, 19, 20], [3, 4, 5, 12, 13, 14, 21, 22, 23], [6, 7, 8, 15, 16, 17, 24, 25, 26],
                         [27, 28, 29, 36, 37, 38, 45, 46, 47], [30, 31, 32, 39, 40, 41, 48, 49, 50], [33, 34, 35, 42, 43, 44, 51, 52, 53],
                         [54, 55, 56, 63, 64, 65, 72, 73, 74], [57, 58, 59, 66, 67, 68, 75, 76, 77], [60, 61, 62, 69, 70, 71, 78, 79, 80]]

        columns_indices = [[0, 9, 18, 27, 36, 45, 54, 63, 72], [1, 10, 19, 28, 37, 46, 55, 64, 73], [2, 11, 20, 29, 38, 47, 56, 65, 74],
                           [3, 12, 21, 30, 39, 48, 57, 66, 75], [4, 13, 22, 31, 40, 49, 58, 67, 76], [5, 14, 23, 32, 41, 50, 59, 68, 77],
                           [6, 15, 24, 33, 42, 51, 60, 69, 78], [7, 16, 25, 34, 43, 52, 61, 70, 79], [8, 17, 26, 35, 44, 53, 62, 71, 80]]
        
        # Apply Naked Pairs strategy (if a pair of candidates appear only in two cells in a row, box, or column, remove them from other cells in that unit)
        for unit in [rows_indices, columns_indices, boxes_indices]:
            for i in range(len(unit)):
                for j in range(len(unit[i])):
                    for x in range(len(unit[i])):
                        # Check for matching pairs of candidates
                        if (candidates[unit[i][j]] == candidates[unit[i][x]]) and (j != x) and (len(candidates[unit[i][j]]) == 2):
                            # If a naked pair is found, remove those candidates from other cells in the same unit
                            for y in range(len(unit[i])):
                                # Ensure we don't modify the pair itself
                                if candidates[unit[i][y]] != candidates[unit[i][j]]:
                                    for candidate in candidates[unit[i][j]][:]: # Iterate over a copy to avoid issues with modification
                                        if candidate in candidates[unit[i][y]]:
                                            candidates[unit[i][y]].remove(candidate)

        # Apply Hidden Singles strategy (if a candidate number exists in only one cell in a row, box, or column, it must be that number)
        for unit in [boxes_indices, rows_indices, columns_indices]:
            for number_to_find in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                candidate_position = -1
                count = 0
                for cell_index in unit[i]:
                    if number_to_find in candidates[cell_index]:
                        candidate_position = cell_index
                        count += 1
                if count == 1:
                    candidates[candidate_position] = [number_to_find]

        # Apply the more complex `apply_x_wing_strategy` to eliminate more candidates
        candidates = apply_x_wing_strategy(boxes_indices, columns_indices, candidates)
        candidates = apply_x_wing_strategy(boxes_indices, rows_indices, candidates)
        candidates = apply_x_wing_strategy(columns_indices, boxes_indices, candidates)
        candidates = apply_x_wing_strategy(rows_indices, boxes_indices, candidates)

        # Fill in cells where only one candidate remains
        for row_index in range(len(puzzle)):
            for col_index in range(len(puzzle)):
                linear_index = (row_index * 9) + col_index
                if (puzzle[row_index][col_index] == 0) and len(candidates[linear_index]) == 1:
                    puzzle[row_index][col_index] = candidates[linear_index][0]

        print("Updating candidates...")
        print_puzzle()
        print(candidates)

        # Check if the puzzle is solved by counting empty candidate lists
        solved_count = 0
        for i in range(len(candidates)):
            if len(candidates[i]) == 0:
                solved_count += 1
        if solved_count == 81:
            global stop_commeting
            stop_commeting = True
    
    # Start the solver loop
    print_puzzle()
    stop_column = False
    stop_row = False
    stop_commeting = False
    
    create_candidate_list()
    
    while not (stop_column and stop_row and stop_commeting):
        stop_column = False
        stop_row = False
        stop_commeting = False
        check_naked_singles_in_columns()
        check_naked_singles_in_rows()
        update_and_solve_with_candidates()
    
    # Update the website with the solved puzzle
    solved_puzzle = puzzle
    
    start_index = 0
    for i in range(82):
        if (i % 9) == 0:
            start_index += 1
        if i != 81:
            element_id = "BBsudokuinputA" + str((10 + (i + start_index)))
            puzzle_cell = driver.find_element(By.ID, element_id)
            value = puzzle_cell.get_attribute("value")
            if value == "":
                row_index = i // 9
                col_index = i % 9
                sending_value = solved_puzzle[row_index][col_index]
                puzzle_cell.send_keys(sending_value)

    # Save a screenshot of the solved puzzle
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "\\solved_puzzles\\sudoku\\"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = f"ss{difficulty_level}_{puzzle_date}.png"
    driver.save_screenshot(dir_path + file_name)

# Run the solver for different difficulty levels
solve_sudoku(1, formatted_date)
solve_sudoku(2, formatted_date)
solve_sudoku(3, formatted_date)

time.sleep(5)
driver.close()