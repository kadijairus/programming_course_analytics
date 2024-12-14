"""Connects feedback to student. Labels student feedback."""


from datetime import datetime
import pandas as pd
import os
from weekly_metrics import WeeklyMetrics

today = datetime.now().strftime("%Y-%m-%d_%H-%M")
output_dir = "output"
students_file = f"{output_dir}/students.xlsx"


class FeedbackAnalyzer:
    """
    Analyzes student feedback to identify and label problematic students.

    :param feedback_data (pd.DataFrame): df containing student feedback.
    """

    def __init__(self, weekly_metrics: WeeklyMetrics):
        """
        Initializes the FeedbackAnalyzer with student feedback data.

        :param: weekly_metrics WeeklyMetrics.
        """
        self.weekly_metrics = weekly_metrics
        self.df = weekly_metrics.get_weekly_df()
        self.week = weekly_metrics.get_week()

    def label_low_self_perception(self, self_perception):
        """
        Helper function to check self_perception on each row.

        :param self_perception:
        :return: str
        """
        self_perception = self_perception.lower()
        if "neutraalne" in self_perception or "negatiivne" in self_perception:
            return f"{self_perception.title()} enesetunne."

    def label_high_time_spent(self, time_spent):
        """
        Helper function to check time_spent on each row.

        :param time_spent:
        :return: str
        """
        median_time = self.weekly_metrics.get_median_time_spent()
        if time_spent is not None:  # Ensure time_spent is valid
            extra_time = time_spent - median_time
            if extra_time >= 5:
                # Longer comment needed if used in Charon export
                # return f"Kulutas {round(extra_time, 1)} h kauem kui mediaan ({round(median_time, 1)}) {self.week}. nädalal."
                return f"{round(extra_time, 1)} h mediaanist rohkem."

    def label_auto_comment(self, low_self_perception, high_time_spent):
        """
        Helper function to concatenate all labels.

        :param low_self_perception, high_time_spent:
        :return: str
        """
        if low_self_perception and high_time_spent:
            # Longer version for Charon. Shorter version for students.xlsx
            # return f"N {self.week}. {high_time_spent} {low_self_perception}"
            return f"{high_time_spent} {low_self_perception}"

    def add_labels(self):
        """
        Adds auto comment labels only if criteria are met.

        :return: df with auto_comment column
        """
        self.df['low_self_perception'] = self.df['self_perception'].apply(self.label_low_self_perception)
        self.df['high_time_spent'] = self.df['time_spent'].apply(self.label_high_time_spent)
        self.df['auto_comment'] = self.df.apply(lambda row: self.label_auto_comment(row['low_self_perception'], row['high_time_spent']), axis=1)
        return self.df

    def add_to_student_file(self):
        """Adds feedback to students.xlsx"""
        df_students = pd.read_excel(students_file)

        # Merge time_spent with custom suffixes to avoid conflicts
        df_students = pd.merge(df_students, self.df[['full_name', 'time_spent']], on='full_name', how='left')
        df_students.rename(columns={"time_spent": f"{self.week}_ajakulu"}, inplace=True)

        # Merge in_person with custom suffixes
        df_students = pd.merge(df_students, self.df[['full_name', 'in_person']], on='full_name', how='left')
        df_students.rename(columns={"in_person": f"{self.week}_kohal"}, inplace=True)

        # Merge auto_comment with custom suffixes
        df_students = pd.merge(df_students, self.df[['full_name', 'auto_comment']], on='full_name', how='left')
        df_students.rename(columns={"auto_comment": f"{self.week}_probleemid"}, inplace=True)

        df_students.to_excel(students_file, index=False)

    def create_csv_of_students_with_comments(self):
        """
        Generates csv of students with comments.

        :return: csv to export comments to Charon
        """
        num_students = self.df.shape[0]
        self.add_labels()
        df_students_with_comments = self.df.copy()
        df_students_with_comments.dropna(subset=['auto_comment'], inplace=True)
        df_students_with_comments = df_students_with_comments[['full_name', 'username', 'auto_comment']]
        names = df_students_with_comments['full_name'].tolist()
        print(f"Student summary for week {self.week}"
              f"\nNeed support: {df_students_with_comments.shape[0]}/{num_students}\n"
              f"Students: {', '.join(names)}\n---")
        path_to_output = f"{output_dir}/{today}_Importimiseks_abi_vajavad_tudengid"
        os.makedirs(path_to_output, exist_ok=True)
        filepath = f"{path_to_output}/{today}_N{self.week}_Abi_vajavad_tudengid.csv"
        # Encoding specified to enable opening in Excel
        df_students_with_comments.to_csv(filepath, index=False, encoding='utf-8-sig')
        print("Generated file \"{filepath}\"".format(filepath=filepath))
