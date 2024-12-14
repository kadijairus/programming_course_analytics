"""Labels and creates plots from weekly student feedback."""


import os
from datetime import datetime
import pandas as pd
import re
from plot import Plot

weekly_feedback_dir = "input"

today = datetime.now().strftime("%Y-%m-%d_%H-%M")
all_students = 372

column_mapping = {
    "Kasutaja täisnimi": "full_name",
    "Rühmad": "groups",
    "Kasutajanimi": "username",
    "Meiliaadress": "email",
    "Kuupäev": "date",
    "Milline oli Su enesetunne seoses selle algkursuse teemaga?": "self_perception",
    "Kas selle teema raames õppisid programmeerimise kohta midagi kasulikku?": "usefulness",
    "Milline on aine tempo Sinu jaoks?": "tempo",
    "Kui kaua Sul selle teema ülesannete lahendamiseks aega läks (tundides)?": "time_spent",
    "Kuidas hindaksid selle teema ülesannet 10 palli skaalal? 10 - suurepärane ülesanne - selge, huvitav lahendada, annab ülevaate teemast  5 - enam-vähem okei ülesanne, oli nii positiivset kui negatiivset  1 - kehv ülesanne, ebahuvitav, ei tee teemat selgeks": "likability",
    "Positiivsed mõtted ja emotsioonid seoses selle teema ja ülesandega - Mis läks hästi? Mis meeldis? Mida uut ja huvitavat teada said?  Võimalusel täpsusta, miks just nii arvad ning mis oli Sinu meelest see, mis Sinu kogemuse heaks tegi.": "good_text",
    "Negatiivsed mõtted ja emotsioonid seoses selle teema ja ülesandega - Mis läks halvasti? Mis ei meeldinud? Kas midagi jäi arusaamatuks või ebaselgeks?  Võimalusel põhjenda ning täpsusta, mida peaks edaspidi teisiti tegema, et Sinu kogemust parandada?": "negative_text",
    "Kas käisid jooksval nädalal loengus või praktikumides kohal?": "in_person",
    "Tagasiside praktikumidele ja abistamisele. Kas said oma küsimustele vastused? Kuidas jäid rahule abiõppejõududega?": "teachers_text",
    "Siin saad soovi korral abiõppejõudusid nimeliselt kiita (vali kuni 3 nime).": "good_teachers"
}

color_map_self_perception = {
    "Väga positiivne": "#e4067e",
    "Pigem positiivne": "#aa1352",
    "Neutraalne": "#4dbed2",
    "Pigem negatiivne": "#342b60",
    "Väga negatiivne": "#000000"
}

color_map_usefulness = {
    "Ei õppinud üldse": "#e4067e",
    "Ei oska öelda": "#aa1352",
    "Õppisin väga palju": "#4dbed2",
    "Õppisin natuke": "#342b60"
}

color_map_tempo = {
    "Liiga rasked ülesanded": "#aa1352",
    "Liiga palju ülesandeid": "#e4067e",
    "Paras": "#4dbed2",
    "Pisut aeglane": "#342b60"
}

color_map_in_person = {
    "Jah": "#4dbed2",
    "Ei, sest ei leidnud aega": "#e4067e",
    "Ei, sest ei olnud vaja": "#342b60"
}

legend_likability = {
    "1": "kehv ülesanne",
    "5": "enam-vähem okei",
    "10": "suurepärane"
}

today = datetime.now().strftime("%Y-%m-%d_%H-%M")


class WeeklyMetrics:
    """
    WeeklyMetrics class for calculating median statistics of student data per week.
    """

    def __init__(self, csv_filepath: str):
        """
        Initializes the WeeklyMetrics with data from a CSV file.

        :param csv_filepath: The csv filepath containing weekly data.
        """
        self.csv_filepath = csv_filepath
        self.df = self.generate_weekly_df()
        self.week = self.extract_week_from_filename(self.csv_filepath)
        self.num_students = self.df.shape[0] # num rows
        self.median_time_spent = self.calculate_median_time_spent()

    def generate_weekly_df(self):
        """
        Generates Pandas dataframe with short column names

        :return: df
        """
        df_week = pd.read_csv(self.csv_filepath, sep=',')
        df_week.rename(columns=column_mapping, inplace=True)
        return df_week

    @staticmethod
    def get_weekly_csvs_from_dir(dirname):
        """
        Initialize WeeklyMetrics for whole feedback.

        :param dirname: location of csv-files
        :return:
        """
        new_csv_files = []
        for root, dirs, files in os.walk(dirname, topdown=False):
            for filepath in files:
                if filepath.endswith(".csv"):
                    fullpath = os.path.join(root, filepath)
                    new_csv_files.append(fullpath)
                    print(f"Found weekly report: {filepath}")
        if not new_csv_files:
            print("No new csv files found.")
        return new_csv_files

    @staticmethod
    def generate_weekly_metrics(csv_path: str):
        """
        Calculates general metrics for specific week.

        :param csv_path
        :return: WeeklyMetrics
        """
        weekly_metrics = WeeklyMetrics(csv_path)
        submissions = weekly_metrics.get_num_students()
        percentage = '{:.1f}%'.format(submissions / all_students * 100)
        print(f"\n---\nMetrics for week {weekly_metrics.get_week()}")
        print(f"Number of feedback submissions: {submissions}/{all_students} ({percentage})")
        print(f"Median time spent: {weekly_metrics.get_median_time_spent()} hours\n---\n")
        return weekly_metrics

    @staticmethod
    def extract_week_from_filename(csv_filepath: str):
        """
        Gets week number from csv filename.

        param: csv filepath
        :return: int
        """
        match = re.search(r'\d+', csv_filepath)
        if match:
            return int(match.group(0))
        else:
            raise ValueError("No number found in the filename")

    def calculate_median_time_spent(self) -> float:
        """
        Calculates the median time spent on tasks by all students.

        :return: float - The median number of hours spent.
        """
        return self.df['time_spent'].median()

    def get_week(self):
        return self.week

    def get_weekly_df(self):
        return self.df

    def get_num_students(self) -> int:
        return self.num_students

    def get_median_time_spent(self) -> float:
        return self.median_time_spent

    def make_plots(self, output_dir):
        """Make plots from feedback."""
        plotter = Plot()
        overlapping_path = f"{output_dir}/{today}_Graafikud_Tagasiside_n2dalati/N{self.week}"
        os.makedirs(overlapping_path, exist_ok=True)

        title = f"Enesetunne {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Enesetunne_N{self.week}.png"
        plotter.plot_pie_chart(self.df, 'self_perception', title, color_map_self_perception, full_path)

        title = f"Ajakulu {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Ajakulu_N{self.week}.png"
        plotter.plot_box_and_whisker_diagram(self.df, 'time_spent', title, full_path)

        title= f"Midagi kasulikku õpitud {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Kasulikkus_N{self.week}.png"
        plotter.plot_pie_chart(self.df, 'usefulness', title, color_map_usefulness, full_path)

        title= f"Aine tempo {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Tempo_N{self.week}.png"
        plotter.plot_pie_chart(self.df, 'tempo', title, color_map_tempo, full_path)

        title= f"Hinnang ülesandele {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Hinnang_ulesandele_N{self.week}.png"
        plotter.plot_histogram(self.df, 'likability', title, legend_likability, full_path)

        title = f"Loengus või praktikumis kohapeal käimine {self.week}. nädalal ({self.num_students})"
        full_path = f"{overlapping_path}/{today}_Kohapeal_kaimine_N{self.week}.png"
        plotter.plot_pie_chart(self.df, 'in_person', title, color_map_in_person, full_path)
