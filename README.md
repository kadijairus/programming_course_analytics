# Student Progress Analytics for Python Course

This project analyzes student progress and feedback for a Python course by processing:
- weekly CSV reports (Moodle -> N nädal -> Iganädalane tagasiside - N. nädal -> Vastused -> Laadi alla)
- grades xlsx (Moodle -> Hinded -> Hindaja aruanne -> Ekspordi -> Exceli arvutustabel)
- log (Moodle -> Aruanded -> Logid ?)
- optional: list of microdegree students (micro.txt)
- optional: list of students without declaration (no_declaration.txt)
It calculates metrics such as median time spent each week, tracks student progress, gets days since last active, and provides automated feedback for students who may need additional support.

Google Colab link to run online and save output to shared drive:
https://colab.research.google.com/drive/1l0SJbQsNJPpndtR3hL40sO7Y9_uVJowa?usp=sharing
Colab notebook in GitHub:
https://github.com/kadijairus/programming_course_analytics

## Features

- Fetch Weekly CSVs: Automatically detects new weekly CSV files from a specified directory.
- Weekly Metrics Calculation: Processes feedback for each week to compute general metrics, such as the median time students spend on tasks, using the WeeklyMetrics class.
- Student Progress Tracking: Tracks and updates student data in an Excel file using the Student class. Calculates points without defence. Gets days since last active from logs. 
- Feedback Analyzer: Identifies students needing additional support based on feedback and time spent, adds specific labels.
- Export Reports: Generates CSV files with student feedback and support needs per week.

## Classes Overview

### WeeklyMetrics

Generates weekly feedback metrics, including the number of submissions and the median time spent by students.

Key Methods

    generate_weekly_df(): 
    Creates a Pandas DataFrame from the weekly CSV.

    calculate_median_time_spent(): 
    Calculates the median time spent on tasks by students.

    get_week(): 
    Extracts the week number from the CSV file name.

    get_num_students(): 
    Returns the total number of students who submitted feedback.

    get_median_time_spent(): 
    Returns the median time spent on tasks for the week.

    make_plots():
    Generates Matplotlib plots.

### Plot

Generates plots using weekly metrics and grades data.

Key methods:

    create_figure()
    Makes standard graph, sets figure size and title format.

    save_plot()
    Saves to filepath.

    make_labels():
    Adds formatted value to label

    plot_pie_chart():
    Generates pie chart of data specified in parameters. Saves as file, if path paramater added. 
    Used for categorical counts like 'self_perception'.

    plot_box_and_whisker_diagram():
    Generates diagram of median with 75% and 25% quantiles. 
    Used for continuous data like 'time-spent' in feedback.

    plot_histogram()
    Generates gradient-colored histogram. 
    Used for ordinal variables like "likability" 1...10 in feedback data.

    plot_stacked_bar_chart()
    Generates stacked bars of multiple columns of categorical variables.
    Used for EX progress data in grades data.

### Student

Manages and updates student information from Moodle in an Excel file.
    
Key Methods:

    generate_student_df(): 
    Reads and parses the student CSV file, creating a DataFrame of student data.

    remove_no_declaration_students()
    Removes from dataframe students listed in file 'no_declaration.txt'.

    add_column_weekly_points_without_defence()
    Gets the sum of range in column <week number>.

    label_ex_progress()
    Returns label based on EX points and defence. Needed for stacked bar chart.

    add_column_ex_progress()
    Uses label_ex_progress to create labels in column EX<week>

    add_column_student_activity()
    Calculates days since last active from logs.
    
    update_students_file(): 
    Creates an Excel file with all student data.
    
    get_all_students_names(): 
    Retrieves and returns a list of all student names.

    make_plots()
    Generates plots, which give overview of students's progress over several weeks.

    label_in_person_mode()
    Generates mode value from a range of columns.

    add_column_mode_in_person(range_first, range_last)
    Adds column "Mood_kohapeal_N<range>".
    First run feedback_analyser to fill columns with feedback data (if person took part of lessons in person).

### FeedbackAnalyzer

Analyzes weekly feedback and labels students who may need additional support.

Key Methods:
       
    label_low_self_perception(): 
    Labels students with neutral or negative self-perception.
    
    label_high_time_spent(): 
    Labels students who spent significantly more time on tasks compared to the median.

    add_labels(): 
    Adds auto-generated feedback labels based on students’ self-perception and time spent.

    add_to_student_file():
    Adds feedback to students row in students.xlsx
        
    create_csv_of_students_with_comments(): 
    Exports a CSV with student names and auto-generated comments for students needing support.

## Design

Colours of plots follow TalTech brand guidelines:
https://oigusaktid.taltech.ee/wp-content/uploads/2020/11/TT_TTU-CVI_A4_2022_lingitud.pdf
Colour palette:
Magneta (pink) : #e4067e
Burgundy (red) : #aa1352
Light blue : #4dbed2
Dark blue : #342b60
Black : #000000
Gray 1 (darker): #9396b0
Gray 2 (lighter): #dadae4


## How It Works

- Get files: Export files from Moodle to directory "input" (or in Colab: shared drive "tulemused")
- Run main.py to analyse input files. In Colab, files are saved to shared drive "tulemused".
- Generate file students.xlsx with personal progress and activity data.
- Fetch new files: Use get_weekly_csvs_from_dir() to retrieve newest weekly feedback CSV file from the specified directory.
- Generate Weekly Metrics: The generate_weekly_metrics() function processes feedback for each week and returns an instance of WeeklyMetrics containing the feedback data and key metrics.
- Analyze Feedback: FeedbackAnalyzer is used to analyze the feedback, label students, and generate comments based on their self-perception and time spent on tasks.
- Export Data to "output": The FeedbackAnalyzer.create_csv_of_students_with_comments() function generates a CSV file with the names and comments of students needing support; file "students.xlsx" contains all students personal progress data.
- In Colab: run code to copy output to "tulemused".

## Dependencies

    Python 3.x
    pandas
    os
    datetime
    re (regular expressions)
    matplotlib

Install dependencies using the following command:

bash

pip install pandas

## Files

    Input:
    Iganädalane tagasiside – <week>. nädal.csv - feedback
    ITI0102-<year> Hinded.xlsx - Excel file containing student data from Moodle.
    logs_ITI0102-2024_<time>.xlsx - logs
    optional: list of microdegree students (micro.txt)
    optional: list of students without declaration (no_declaration.txt)

    Output:
    file: students.xlsx: Excel file used to store and update student information.
    directory: <date>_Graafikud_EX_progress_<range> containing graphs <date>EX_<plot name><range>.png
    directory: <date>_Graafikud_tagasiside_nädalati containing directories N<week> containing graphs
    directory: <date>_Importimiseks_abi_vajavad_tudengid containing files <date>_N<week>... for export to Charon

