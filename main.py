"""Generates weekly progress statistics and labels below-median students based on feedback and grades"""


from datetime import datetime
import os

from weekly_metrics import WeeklyMetrics
from student import Student
from feedback_analyzer import FeedbackAnalyzer

grades = "input/ITI0102-2024 Hinded.xlsx"
micro_filepath = "input/micro.txt"
no_declaration_filepath = "input/no_declaration.txt"
input_dir = "input"

# Output goes here
today = datetime.now().strftime("%Y-%m-%d_%H-%M")
#checked_log = "output/checked_weekly_data.log"
output_dir = "output"
students_file = f"{output_dir}/students.xlsx"
# !!! Get automatically from grades in the future.
all_students = 366

if __name__ == "__main__":
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    students = Student(grades)
    students.add_column_micro(micro_filepath)

    students.add_column_weekly_points_without_defence(14, 19, 1)
    students.add_column_ex_progress(1,'Charon:EX/ex01_beginning - Defense (Tegelik)',1)

    students.add_column_weekly_points_without_defence(29, 34, 2)
    students.add_column_ex_progress(2, 'Charon:EX/ex02_loops - Defense (Tegelik)', 2)

    students.add_column_weekly_points_without_defence(42, 44, 3)
    students.add_column_ex_progress(3, 'Charon:EX/ex03_validation - Defense (Tegelik)', 3)

    students.add_column_weekly_points_without_defence(52, 53, 4)
    students.add_column_ex_progress(4, 'Charon:EX/ex04_lists - Defense (Tegelik)', 4)

    students.add_column_weekly_points_without_defence(170, 171, 5)
    students.add_column_ex_progress(5, 'Charon:PROJECT/project1 - Defense (Tegelik)', 5, 20)

    students.add_column_weekly_points_without_defence(65, 66, 6)
    students.add_column_ex_progress(6, 'Charon:EX/ex06_airport - Defense (Tegelik)', 6)

    students.add_column_weekly_points_without_defence(78, 80, 7)
    students.add_column_ex_progress(7, 'Charon:EX/ex07_regex - Defense (Tegelik)', 7)

    students.add_column_weekly_points_without_defence(90, 91, 8)
    students.add_column_ex_progress(8, 'Charon:EX/ex08_recursion - Defense (Tegelik)', 8)

    students.add_column_weekly_points_without_defence(103, 104, 9)
    students.add_column_ex_progress(9, 'Charon:EX/ex09_file_handling - Defense (Tegelik)', 9)

    students.add_column_weekly_points_without_defence(176, 177, 10)
    students.add_column_ex_progress(10, 'Charon:PROJECT/project2 - Defense (Tegelik)', 10, 30)

    students.add_column_weekly_points_without_defence(114, 115, 11)
    students.add_column_ex_progress(11, 'Charon:EX/ex09_file_handling - Defense (Tegelik)', 11, 15)

    students.add_column_weekly_points_without_defence(125, 126, 12)
    students.add_column_ex_progress(12, 'Charon:EX/ex12_router - Defense (Tegelik)', 12, 15)

    students.add_column_weekly_points_without_defence(137, 138, 13)
    students.add_column_ex_progress(13, 'Charon:OP/op13_football - Defense (Tegelik)', 13, 15)

    students.add_column_weekly_points_without_defence(148, 149, 14)
    students.add_column_ex_progress(14, 'Charon:OP/op14_spaceship - Defense (Tegelik)', 14, 15)

    students.add_column_weekly_points_without_defence(182, 183, 15)
    students.add_column_ex_progress(15, 'Charon:PROJECT/project3 - Defense (Tegelik)', 15, 40)

    students.update_students_file(students_file)

    students.make_plots(['EX11', 'EX12','EX13','EX14','EX15'], output_dir)

    new_csvs = WeeklyMetrics.get_weekly_csvs_from_dir(input_dir)
    for new_csv in new_csvs:
        metrics = WeeklyMetrics.generate_weekly_metrics(new_csv)
        week = metrics.get_week()
        metrics.make_plots(output_dir)
        analyzer = FeedbackAnalyzer(metrics)
        analyzer.create_csv_of_students_with_comments()
        analyzer.add_to_student_file()
    students.add_column_mode_in_person(7,15, students_file)
    students.add_column_mean_time_spent(7, 15, students_file)