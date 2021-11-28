# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib import rcParams
from math import ceil

from pyproject.plan import Project, Category, Milestone, Task

# Plotting heuristics
ROW_HEIGHT = 0.3
MONTH_WIDTH = 3
MAX_X_DIVS_PER_INCH = 4

# Plotting colors
TASK_COLOR = '#8080FF'
CRITICAL_COLOR = '#FF4040'
class Gantt():
    def __init__(self,project: Project):

        rows = project.root.get_list()
        names = [r.name for r in rows]
        ids = [r.id for r in rows]
        idx_map = {id:idx for id,idx in zip(ids,range(len(ids)))}

        fig,ax = plt.subplots()
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        ax.xaxis.set_major_locator(mdates.DayLocator())

        for idx,r in enumerate(rows):
            if isinstance(r,Category):
                s,e = r.get_time_bounds()
                ax.barh(idx,width=e-s,left=s,color='#000000')
            elif isinstance(r,Task):
                c = CRITICAL_COLOR if r.critical else TASK_COLOR
                ax.barh(idx,width=r.duration,left=r.start,color=c)
            elif isinstance(r,Milestone):
                ax.scatter(r.start,idx,marker='d',color='k',s=rcParams['lines.markersize']**2.5)
            for p in r.predecessors:
                pred = rows[idx_map[p]]
                if pred.end >= r.start:
                    continue
                
                xs = [pred.end,r.start,r.start]
                ys = [idx_map[pred.id],idx_map[pred.id],idx]
                ax.plot(xs,ys,color="k")
                if not isinstance(r,Milestone):
                    ax.scatter(r.start,idx,color="k")
                # self.plot_link(ax,rows[id_map[int(p)-1]],r)
            # ax.text(r.start,idx,r.name,horizontalalignment='right',verticalalignment='center')
        
        fig.set_figheight(len(rows)*ROW_HEIGHT)
        s,e = project.root.get_time_bounds();
        n_months = (e-s)/timedelta(days=30)
        fig.set_figwidth(n_months*MONTH_WIDTH)

        ax.set_yticks(list(idx_map.values()),names)
        # ax.set_yticks([])

        # Some goofy math to calculate the x ticks based on the pre-defined heuristics
        weeks = (e-s).days/7
        skip_weeks = ceil(weeks/fig.get_figwidth()/MAX_X_DIVS_PER_INCH)
        xticks = [(s + timedelta(days = 6 - s.weekday())) + i*skip_weeks*timedelta(days=7) for i in range(int(weeks//skip_weeks))] 
        xticklabels = [i.strftime("%a %b %d") for i in xticks]
        ax.set_xticks(xticks,xticklabels,rotation=70)

        ax.grid('minor')
        ax.set_axisbelow(True)

        plt.tight_layout()

        self.fig = fig
        self.ax = ax
        
    # @staticmethod
    # def plot_link(ax,source,dest) -> None:
    #     # TODO Plot line from source to desk on ax
    #     # TODO Calculate whether the link goes forwards or backwards
    #     # TODO If forwards, plot straight right and up/down
    #     # TODO If backwards...raise an error?

    #     if source.end >= dest.start:
    #         return
        
    #     xs = [source.end,dest.start,dest.start]
    #     ys = [source.id,source.id,dest.id]
    #     ax.plot(xs,ys,color="k")
    #     if not isinstance(dest,Milestone):
    #         ax.scatter(dest.start,dest.id,color="k")
    #     # ax.arrow(source.end,source.id,dest.start-source.end,0)
    #     # ax.plot([source.end, dest.start],[source.id,source.id],color='k')
    #     # ax.c(dest.start,source.id,0,dest.id-source.id)
    #     return

class WBS():
    def __init__(self,project: Project) -> None:
        pass