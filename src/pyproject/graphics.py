# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib import rcParams
from matplotlib import patches
from math import ceil

from pyproject.plan import Project, Category, Milestone, Task

# Global font choice
# rcParams['font.family'] = 'Helvetica'

# Gantt plotting heuristics
GANTT_ROW_HEIGHT = 0.3
GANTT_MONTH_WIDTH = 3
GANTT_MAX_X_DIVS_PER_INCH = 4

# Gantt plotting colors
GANTT_TASK_COLOR = '#8080FF'
GANTT_CRITICAL_COLOR = '#FF4040'


class Gantt():
    def __init__(self, project: Project):

        rows = project.root.get_list()
        names = [r.name for r in rows]
        ids = [r.id for r in rows]
        idx_map = {id: idx for id, idx in zip(ids, range(len(ids)))}

        fig, ax = plt.subplots()
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        for idx, r in enumerate(rows):
            if isinstance(r, Category):
                s, e = r.get_time_bounds()
                ax.barh(idx, width=e-s, left=s, color='#000000')
            elif isinstance(r, Task):
                c = GANTT_CRITICAL_COLOR if r.critical else GANTT_TASK_COLOR
                ax.barh(idx, width=r.duration, left=r.start, color=c)
            elif isinstance(r, Milestone):
                ax.scatter(r.start, idx, marker='d', color='k',
                           s=rcParams['lines.markersize']**2.5)
            for p in r.predecessors:
                if p in idx_map.keys():
                    pred = rows[idx_map[p]]
                    if pred.end >= r.start:
                        continue

                    xs = [pred.end, r.start, r.start]
                    ys = [idx_map[pred.id], idx_map[pred.id], idx]
                    ax.plot(xs, ys, color="k")
                    if not isinstance(r, Milestone):
                        ax.scatter(r.start, idx, color="k")
                else:
                    print("Missing Predecessor; continuing")

        fig.set_figheight(len(rows)*GANTT_ROW_HEIGHT)
        s, e = project.root.get_time_bounds()
        n_months = (e-s)/timedelta(days=30)
        fig.set_figwidth(n_months*GANTT_MONTH_WIDTH)

        ax.set_yticks(list(idx_map.values()), names)

        # Some goofy math to calculate the x ticks based on the pre-defined heuristics
        weeks = (e-s).days/7
        skip_weeks = ceil(weeks/fig.get_figwidth()/GANTT_MAX_X_DIVS_PER_INCH)
        xticks = [(s + timedelta(days=6 - s.weekday())) + i*skip_weeks *
                  timedelta(days=7) for i in range(int(weeks//skip_weeks))]
        xticklabels = [i.strftime("%a %b %d") for i in xticks]
        ax.set_xticks(xticks, xticklabels, rotation=70)

        ax.grid('minor')
        ax.set_axisbelow(True)

        plt.tight_layout()

        self.fig = fig
        self.ax = ax


# WBS plotting heuristics
WBS_ITEM_WIDTH = 4.0  # inches
WBS_ITEM_HEIGHT = 0.75  # inches
WBS_V_SEP = 0.5  # [inches] Vertical separation between rows
WBS_H_SEP = 0.5  # [inches] Horizontal separation between columns
WBS_COL_WIDTH = WBS_ITEM_WIDTH + WBS_H_SEP
WBS_ROW_HEIGHT = WBS_ITEM_HEIGHT + WBS_V_SEP
WBS_BBOX = {'width': WBS_ITEM_WIDTH, 'height': WBS_ITEM_HEIGHT,
            'edgecolor': 'black', 'boxstyle': 'round'}
WBS_CATEGORY_BBOX = {**WBS_BBOX, 'facecolor': '#CFCFCF'}
WBS_TASK_BBOX = {**WBS_BBOX, 'facecolor': '#FFFFFF'}


class WBS():
    def __init__(self, project: Project) -> None:

        fig, ax = plt.subplots()

        self.plot_category(ax, project.root, 0.0, 0.0)

        w, h = project.get_dims()

        width_inches = w*(WBS_ITEM_WIDTH+WBS_H_SEP)
        height_inches = h*(WBS_ITEM_HEIGHT+WBS_V_SEP)

        ax.set_xlim(-width_inches/2.0, width_inches/2.0)
        ax.set_ylim(-height_inches, WBS_H_SEP)
        ax.set_axis_off()

        fig.set_figheight(height_inches)
        fig.set_figwidth(width_inches)

        self.fig = fig
        self.ax = ax

    @classmethod
    def plot_category(cls, ax, category: Category, x, y) -> None:
        """Add a category to the axes originated at x,y

        Args:
            ax (Matplotlib.axes.Axes): Axes to plot on
            category (Category): Category to plot
            x (float): Origin x-position
            y (float): Origin y-position
        """

        cls.plot_box(ax, x, y, category.name, '#CFCFCF')

        category_width, _ = category.get_dims()

        tasks = [t for t in category.children if isinstance(t, Task)]
        categories = [t for t in category.children if isinstance(t, Category)]

        curr_left_edge = x-(category_width*WBS_COL_WIDTH)/2.0
        child_xs = []

        # If category has tasks as children, start with those in the leftmost column
        if len(tasks):

            # Get the center of the column
            center_x = curr_left_edge + WBS_COL_WIDTH/2.0
            child_xs.append(center_x)

            # The top of the first task should be one row below the current category
            top_y = y - WBS_ROW_HEIGHT

            # Plot line segment to the top of the first task
            ax.plot([center_x, center_x], [y-WBS_ITEM_HEIGHT -
                    (WBS_V_SEP/2.0), top_y], color='k')

            # Plot the top task
            cls.plot_box(ax, center_x, top_y, tasks[0].name, '#FFFFFF')

            for t in tasks[1:]:

                # Plot vertical line connector and box, decrementing the y-position
                ax.plot([center_x, center_x], [top_y-WBS_ITEM_HEIGHT,
                        top_y-WBS_ROW_HEIGHT], color='k')
                top_y -= WBS_ROW_HEIGHT
                cls.plot_box(ax, center_x, top_y, t.name, '#FFFFFF')

            # Move the current left edge marker over for next column to get plotted
            curr_left_edge += WBS_COL_WIDTH

        # Top of all child categories is one row below the top of the current category
        top_y = y - WBS_ROW_HEIGHT

        for c in categories:

            category_width, _ = c.get_dims()

            # Find the center of the columns spanned by this category
            center_x = curr_left_edge + category_width*(WBS_COL_WIDTH/2.0)
            child_xs.append(center_x)

            # Plot little line segment to the top of this category
            ax.plot([center_x, center_x], [y-WBS_ITEM_HEIGHT -
                    (WBS_V_SEP/2.0), top_y], color='k')

            cls.plot_category(ax, c, center_x, y-WBS_ROW_HEIGHT)

            # Increment the left edge marker to the left edge of the next child category
            curr_left_edge += category_width*WBS_COL_WIDTH

        # TODO Draw line to top of left and right things
        if child_xs:
            mid_height = y-WBS_ITEM_HEIGHT-(WBS_V_SEP/2.0)
            ax.plot([x, x], [y-WBS_ITEM_HEIGHT, mid_height], color='k')
            ax.plot([x, child_xs[0]], [mid_height, mid_height], color='k')
            ax.plot([x, child_xs[-1]], [mid_height, mid_height], color='k')

    @staticmethod
    def plot_box(ax, x, y, text, color) -> None:
        """Plot a box with text

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
            x (float): Horizontal center of box
            y (float): Vertical top of box
            text (str): Text to put in the box
            color (str): Face color of the box
        """
        cx = x  # Center x
        cy = y-WBS_ITEM_HEIGHT/2.0  # Center y

        lx = x-WBS_ITEM_WIDTH/2.0  # Left x
        by = y-WBS_ITEM_HEIGHT  # Bottom y

        rct = patches.Rectangle(
            (lx, by), WBS_ITEM_WIDTH, WBS_ITEM_HEIGHT, facecolor=color, edgecolor='black')
        ax.annotate(text, (cx, cy), fontsize=10, ha='center', va='center')
        ax.add_patch(rct)
