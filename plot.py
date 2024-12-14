"""Generates plots in TalTech colors."""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


class Plot:
    def __init__(self, font_family='Verdana', font_size=14, fig_size=(13, 8)):
        self.font_family = font_family
        self.font_size = font_size
        self.fig_size = fig_size
        self.title_padding = 30

        plt.rcParams['font.family'] = self.font_family
        plt.rcParams['font.size'] = self.font_size

    def create_figure(self, title):
        """Create a figure with a title."""
        plt.figure(figsize=self.fig_size)
        plt.title(title, fontsize=self.font_size + 2, pad=self.title_padding, fontweight='bold')

    def save_plot(self, file_path):
        """Save the plot if a file path is provided."""
        if file_path:
            plt.savefig(file_path, bbox_inches='tight')
            print(f"Plot saved to: {file_path}")

    def make_labels(self, category_counts):
        """Generate labels with percentages for the pie chart."""
        total = sum(category_counts)
        return [f'{label} ({value / total * 100:.1f}%)' for label, value in zip(category_counts.index, category_counts)]

    def plot_pie_chart(self, data, column, title, color_map, file_path=None):
        """Plot a pie chart using instance settings."""
        category_counts = data[column].value_counts().sort_index()
        # Change for "Tempo"
        category_counts.index = category_counts.index.str.replace('Liiga kiire – liiga rasked ülesanded', 'Liiga rasked ülesanded')
        category_counts.index = category_counts.index.str.replace('Liiga kiire – liiga suur ülesannete hulk', 'Liiga palju ülesandeid')

        # Get colors for categories, default to black if not found
        category_colors = [color_map.get(category, "#000000") for category in category_counts.index]

        # Create figure and set title
        self.create_figure(title)

        plt.pie(
            category_counts,
            labels=self.make_labels(category_counts),
            startangle=140,
            colors=category_colors,
            radius=0.6
        )
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is drawn as a circle.
        self.save_plot(file_path)
        # plt.show()

    def plot_box_and_whisker_diagram(self, data, column, title, file_path=None):
        """Plot a vertical box plot with default whiskers, but no outliers, and ensure lower whisker is not below min."""
        # Create figure and set title
        self.create_figure(title)

        # Calculate statistical values
        median = data[column].median()
        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)
        min_value = max(data[column].min(), 0)  # Ensure the minimum is not below 0
        max_value = data[column].max()

        # Calculate default whiskers
        iqr = q3 - q1
        lower_whisker = max(min_value, q1 - 1.5 * iqr)  # Lower whisker can't go below min_value
        upper_whisker = min(max_value, q3 + 1.5 * iqr)  # Upper whisker

        # Create vertical boxplot without showing outliers and ensuring custom whiskers
        plt.boxplot(data[column], vert=True, patch_artist=True,
                    boxprops=dict(facecolor='#4dbed2'),
                    whiskerprops=dict(color='black', linewidth=1),  # Whisker style
                    flierprops=dict(visible=False),  # Hide outliers
                    showcaps=True),  # Show caps on whiskers

        # Get the current axis
        ax = plt.gca()

        # Set vertical axis ticks manually
        tick_interval = 5
        vertical_ticks = list(range(int(min_value), int(max_value) + 1, tick_interval))
        ax.set_yticks(vertical_ticks)  # Set vertical ticks
        ax.set_xticks([])  # No ticks on the horizontal axis

        # Add median line inside the box and annotate median value
        ax.hlines(median, xmin=0.85, xmax=1.15, color='black', linewidth=3)
        ax.text(1.2, median, f'Mediaan {median:.0f} h', fontsize=self.font_size + 2,
                va='center')  # Median value next to the line
        ax.text(1.2, median - 1, f'({min_value:.0f} - {max_value:.0f} h)', fontsize=self.font_size -2, va='center', color='black')

        # Label Q1 and Q3
        ax.text(0.8, q1, f'25% < {q1:.0f} h', fontsize=self.font_size, ha='center', color='black')
        ax.text(0.8, q3, f'75% < {q3:.0f} h', fontsize=self.font_size, ha='center', color='black')

        # Add whisker labels
        ax.text(0.8, lower_whisker, f'{lower_whisker:.0f} h', fontsize=self.font_size, ha='center',
                color='black')
        ax.text(0.8, upper_whisker, f'{upper_whisker:.0f} h', fontsize=self.font_size, ha='center',
                color='black')

        # Set y-axis limit to match the min and max of the data
        ax.set_ylim(0, upper_whisker + 2)  # Adding a small margin after the max value

        # Remove the top and right spines (axes)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.save_plot(file_path)
        # plt.show()

    def plot_histogram(self, data, column, title, legend, file_path=None):
        """Plot a bar chart to show the distribution on 1-10 scale."""

        rating_counts = data[column].value_counts().sort_index()

        # Create figure and set title
        self.create_figure(title)

        # Define the two colors for the gradient
        color1 = "#342b60"  # First color
        color2 = "#4dbed2"  # Second color
        gradient = LinearSegmentedColormap.from_list("custom_gradient", [color1, color2])

        # Generate color values for each bar based on the rating
        bar_colors = gradient(np.linspace(0, 1, len(rating_counts)))

        # Plot the bar chart
        bars = plt.bar(rating_counts.index, rating_counts.values, color=bar_colors)

        # Add counts on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval)}', ha='center', va='bottom',
                     fontsize=self.font_size)

        # Get the current axis
        ax = plt.gca()

        # Remove the upper and right spines (axes)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Set ticks and labels on the horizontal axis, ensuring all 10 labels are visible
        ax.set_xticks(range(1, 11))  # Set ticks from 1 to 10
        ax.set_xticklabels(range(1, 11), fontsize=self.font_size)  # Ensure labels are visible

        # Add explanatory text based on the legend dictionary
        legend_text = "\n".join([f"{key}: {value}" for key, value in legend.items()])
        plt.text(0.05, 0.95, legend_text, transform=ax.transAxes, fontsize=self.font_size - 4,
                 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        self.save_plot(file_path)
        # plt.show()

    def plot_stacked_bar_chart(self, data, title, color_map, file_path=None):
        """Plot a stacked bar chart to show the distribution of statuses across multiple columns."""
        category_sums = data.apply(lambda x: x.value_counts(normalize=True).fillna(0)).T * 100  # Convert to percentage
        category_sums = category_sums.fillna(0)

        self.create_figure(title)
        # Create the bar chart
        ax = category_sums.plot(kind='bar', stacked=True,
                                color=[color_map.get(x, "#000000") for x in category_sums.columns])

        # Add counts on top of bars
        for i in range(len(category_sums)):
            cumulative = 0  # To track the position of the counts
            for j in range(len(category_sums.columns)):
                count = category_sums.iloc[i, j]

                # Check if count is not NaN before converting to int
                if pd.notna(count):
                    count = int(count)  # Safely convert percentage value to int

                    # Only add text if count is greater than 0
                    if count > 0:
                        ax.text(i, cumulative + count / 2, f'{count}%', ha='center', va='center', fontsize=9)  # Centered vertically
                        # Position text next to the bar (right side)
                        # ax.text(i + 0.2, cumulative + count / 2, f'{count}%', ha='left', va='bottom', fontsize=8, color='black')
                cumulative += count

                # Remove y-axis label
        ax.set_ylabel('')  # No y-axis label

        # Adjust x-tick labels to be horizontal
        ax.set_xticklabels(category_sums.index, rotation=0, ha='center')

        # Create a legend with just labels
        ax.legend(category_sums.columns, loc='lower right', fontsize=self.font_size - 5, title=None)

        ax.set_title(title, fontsize=self.font_size + 2)

        # Remove upper and right axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Adjust layout for better spacing
        plt.tight_layout(pad=2.0)
        if file_path:
            plt.savefig(file_path, bbox_inches='tight')
