"""Combines student progress from grades and weekly feedback."""


from datetime import datetime

from openpyxl.utils.exceptions import IllegalCharacterError

from plot import Plot
import pandas as pd
import os

# Export these files from Moodle

# !!! Use csv in the future.
# activity_log = "input/logs_dummy.xlsx"
activity_log = "input/logs_ITI0102-2024_20241210-0926.xlsx"
no_declaration_filepath = "input/no_declaration.txt"

today = datetime.now().strftime("%Y-%m-%d_%H-%M")

# Output goes here
checked_log = "output/log_checked_weekly_data.log"

# !!! Get automatically from grades in the future.
all_students = 366

activity_log_column_mapping = {
    "Kasutaja täisnimi":"full_name",
    "Aeg":"time"
}

grades_column_mapping = {
    "Rühmad":"groups",
    "Kasutajanimi": "username",
    "Meiliaadress": "email"
}

color_map_progress = {
    "alustamata": "#e4067e",
    "alustatud, <10 p": "#aa1352",
    "alustatud, >10 p": "#9396b0",
    "kaitsmata, tehtud": "#342b60",
    "kaitstud": "#4dbed2"
}

legend_last_active = {
    "0": "täna külastatud",
    "5": "5 päeva tagasi",
    "10": "10 päeva tagasi"
}


class Student:
    """
    Finds students from Moodle csv file. -> To be replaced with xlsx!!!

    :param grades_filepath: The filename containing students grades data.
    """
    def __init__(self, grades_filepath, log_filepath: str = activity_log):
        self.df = None
        self.generate_student_df(grades_filepath)
        self.remove_no_declaration_students()
        self.add_column_student_activity(log_filepath)
        self.num_students = 0

    def generate_student_df(self, grades_filepath: str):
        """
        Generates dataframe with student data.

        :param grades_filepath: grades file
        :return: DataFrame containing student data.
        """
        self.update_df_from_students_file(grades_filepath)
        self.df.rename(columns=grades_column_mapping, inplace=True)
        self.df['full_name'] = self.df['Eesnimi'] + ' ' + self.df['Perekonnanimi']

    def remove_no_declaration_students(self, custom_no_declaration_filepath=no_declaration_filepath):
        students_before = len(self.df)
        with open(custom_no_declaration_filepath, 'r') as file:
            no_declaration_students = file.read().splitlines()
        # Remove rows where student is in no_declaration_students
        self.df = self.df[~self.df['full_name'].isin(no_declaration_students)]
        students_after = len(self.df)
        self.num_students = students_after
        print(f"Removed {students_before - students_after} students without declaration from dataframe. {students_after} students.")

    def add_column_micro(self, micro_filepath):
        """
        Reads a file containing microdegree student identifiers and adds a 'micro' column to the DataFrame
        with True/False values depending on whether the students full name is in the microdegree list.
        """
        with open(micro_filepath, 'r') as file:
            micro_students = file.read().splitlines()
        print(f"{len(micro_students)} microdegree students")
        self.df['micro'] = self.df['full_name'].isin(micro_students)

    def add_column_weekly_points_without_defence(self, first_index: int, last_index: int, col_name_week: int):
        selected_columns = self.df.iloc[:, first_index:last_index]
        selected_columns = selected_columns.apply(pd.to_numeric, errors='coerce')
        print("I summed these columns:")
        for col in self.df.columns[first_index:last_index]:
            print(col)
        self.df[col_name_week] = selected_columns.sum(axis=1)

    def label_ex_progress(self, points_without_defence, defence, full_points=15):
        """
        Helper function to label student progress based on EX points.

        :param full_points: default 15 for EX, 20 if project
        :param points_without_defence: previously created column
        :param defence: column of defence points, value 0 or 1
        :return: label in students file, which is used to generate stacked box chart
        """
        try:
            points_without_defence = float(points_without_defence)
            defence = float(defence)
        except ValueError:
            return "alustamata"
        # Now proceed with the logic
        if points_without_defence == 0:
            return "alustamata"
        if defence == 1:
            return "kaitstud"
        if points_without_defence == full_points:
            if defence == 0:
                return "kaitsmata, tehtud"
        if points_without_defence > 10:
            return "alustatud, >10 p"
        if points_without_defence > 0:
            return "alustatud, <10 p"
        return "alustamata"

    def add_column_ex_progress(self, points_without_defence, defence, col_name_week, full_points=15):
        self.df[points_without_defence] = pd.to_numeric(self.df[points_without_defence], errors='coerce')
        self.df[defence] = pd.to_numeric(self.df[defence], errors='coerce')

        self.df[f"EX{col_name_week}"] = self.df.apply(lambda row: self.label_ex_progress(row[points_without_defence], row[defence], full_points), axis=1)
        # Add placeholder for feedback
        # self.df[f"{col_name_week}_feedback"] = "ei_vastanud" - did not work

    def add_column_student_activity(self, log_filepath: str):
        """
        Generates dataframe with student data.

        :param log_filepath:
        :return: DataFrame containing activity column.
        """
        df_students = pd.read_excel(log_filepath)
        df_students.rename(columns=activity_log_column_mapping, inplace=True)
        df_students['full_name'].dropna(inplace=True)
        df_students['last_active'] = datetime.today() - pd.to_datetime(df_students['time'],
                                                                       format='%d/%m/%y, %H:%M:%S')        # df_students['last_active'] = datetime.today() - pd.to_datetime(df_students['time'])        #df_students['full_name'] = df_students['Eesnimi'] + " " + df_students['Perekonnanimi']
        df_students['last_active'] = df_students['last_active'].dt.days
        idx = df_students.groupby('full_name')['last_active'].idxmin()
        df_students = df_students.loc[idx].reset_index(drop=True)
        df_students = df_students[['full_name', 'last_active']]
        df_students.sort_values(by='last_active', ascending=False)
        # The resulting df_unique_students will contain unique 'full_name' with the smallest 'last_active' (most recent)
        self.df = self.df.join(df_students.set_index('full_name'), on='full_name', how='left')

    def update_students_file(self, excel_filename):
        """
        Updates the Excel file with the new week's data. If the file does not exist, it creates one.

        :param excel_filename: The filename of the Excel file to update. Defaults to 'students.xlsx'.
        """
        self.df.to_excel(excel_filename, index=False)
        print("Created new file {excel_filename}".format(excel_filename=excel_filename))

    def get_all_students_names(self):
        """
        Retrieves the list of student names from the DataFrame.

        :return: List of student names.
        """
        return self.df['full_name'].tolist()

    def label_in_person_mode(self, row):
        row = row.fillna("")
        value_counts = row.value_counts(dropna=False)
        total_count = len(row)
        empty_count = value_counts.get("", 0)
        if empty_count > total_count / 2 + 1:
            return 'Ei vastanud'
        value_counts = value_counts[value_counts.index != ""]
        max_count = value_counts.max()
        tied_values = value_counts[value_counts == max_count]

        # If there's a tie and "Jah" is one of the tied values, return "Pooltel kordadel"
        if len(tied_values) > 1 and "Jah" in tied_values.index:
            return 'Pooltel kordadel'

        # Otherwise, return the most frequent non-empty value
        most_frequent_value = value_counts.idxmax()
        return most_frequent_value

    def label_time_spent(self, row):
        non_empty_values = row.dropna()
        if non_empty_values.empty:
            return None
        return non_empty_values.mean()

    def update_df_from_students_file(self, students_file):
        self.df = pd.read_excel(students_file)

    def get_range_of_columns(self, range_first, range_last, keyword):
        number_range = range(range_first, range_last + 1)
        subset_of_columns = [
            col for col in self.df.columns
            if keyword in str(col) and any(str(i) in str(col) for i in number_range)
        ]
        if not subset_of_columns:
            print(f"Ei leidnud {range_first}-{range_last} nädala tagasisidet märksõnaga {keyword}. Käivita esmalt tagasiside analüüs.")
            raise ValueError
        return subset_of_columns

    def add_column_mean_time_spent(self, range_first, range_last, students_file):
        self.update_df_from_students_file(students_file)

        subset_of_columns = self.get_range_of_columns(range_first, range_last, "ajakulu")
        df_subset = self.df[subset_of_columns]

        # Apply the label function to each row in the subset
        time_spent = df_subset.apply(self.label_time_spent, axis=1)

        # Add the result to the original DataFrame
        self.df[f'Ajakulu_N{range_first}-{range_last}_ar_keskm'] = time_spent
        self.update_students_file(students_file)

    def add_column_mode_in_person(self, range_first, range_last, students_file):
        self.update_df_from_students_file(students_file)

        subset_of_columns = self.get_range_of_columns(range_first, range_last, "kohal")
        df_subset = self.df[subset_of_columns]

        # Apply the label function to each row in the subset
        modes = df_subset.apply(self.label_in_person_mode, axis=1)

        # Add the result to the original DataFrame
        self.df[f'Mood_kohapeal_N{range_first}-{range_last}'] = modes
        self.update_students_file(students_file)

    def make_plots(self, list_of_columns, output_dir):
        plotter = Plot()
        interval = f"{list_of_columns[0]}-{list_of_columns[-1]}"
        overlapping_path = f"{output_dir}/{today}_Graafikud_EX_progress_{interval}"
        os.makedirs(overlapping_path, exist_ok=True)
        title = f"Iganädalaste EX ülesannete lahendamine ({len(self.df)})"
        full_path = f"{overlapping_path}/{today}_EX_k6ik_tudengid_{interval}.png"
        ex_df = self.df[list_of_columns]
        plotter.plot_stacked_bar_chart(ex_df, title, color_map_progress, full_path)

        micro_students_df = self.df[self.df['micro'] == True]
        title = f"EX ülesannete lahendamine. Mikrokraad ({len(micro_students_df)})"
        full_path = f"{overlapping_path}/{today}_EX_mikro_{interval}.png"
        ex_df = micro_students_df[list_of_columns]
        plotter.plot_stacked_bar_chart(ex_df, title, color_map_progress, full_path)

        not_micro_students_df = self.df[self.df['micro'] == False]
        title = f"EX ülesannete lahendamine. Mitte-mikrokraad ({len(not_micro_students_df)})"
        full_path = f"{overlapping_path}/{today}_EX_mitte_mikro_{interval}.png"
        ex_df = not_micro_students_df[list_of_columns]
        plotter.plot_stacked_bar_chart(ex_df, title, color_map_progress, full_path)

        title = f"Päevi viimasest kursuse külastamisest ({len(self.df)})"
        full_path = f"{overlapping_path}/{today}_Paevi_kursuse_kulastamisest.png"
        plotter.plot_histogram(self.df, 'last_active', title, legend_last_active, full_path)
