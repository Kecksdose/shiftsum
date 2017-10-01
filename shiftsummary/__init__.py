import datetime

class Shifter(dict):

    def __init__(self, name, df_runs, shifts, **kwargs):
        self["name"] = name
        self["df_runs"] = df_runs
        self["shifts"] = shifts
        self["daytime_time"] = kwargs.pop("daytime_time", {"morning":"06:30:00",
                                                           "evening":"14:30:00",
                                                           "night":"22:30:00"})
        self["shift_dur"] = kwargs.pop("shift_dur", datetime.timedelta(hours=8, minutes=0, seconds=0))
        self["digits"] = kwargs.pop("digits", 2)
        self._check_for_matching_time()

    def _check_for_matching_time(self):
        shift_time = []
        run_time = []
        total_lumi = []
        logged_lumi = []
        for start_shift in self._format_shift(self["shifts"]):
            shift_time.append(self["shift_dur"])
            for cnt, (start_run, end_run) in enumerate(zip(self["df_runs"]["starttime_formatted"],
                                                           self["df_runs"]["endtime_formatted"])):
                temptime = self._time_overlap([start_run, end_run], [start_shift, start_shift + self["shift_dur"]])
                if temptime:
                    run_time.append(temptime)
                    total_lumi.append(temptime/self["df_runs"]["time_total"][cnt]*self["df_runs"]["lumi_total"][cnt])
                    logged_lumi.append(temptime/self["df_runs"]["time_total"][cnt]*self["df_runs"]["lumi_logged"][cnt])
                    #print "start_run={0}, end_run={1}, start_shift={2}, dur={3}".format(start_run, end_run, start_shift, temptime)

        self["dlumi"] = sum(total_lumi)/1e6 #pb^-1
        self["clumi"] = sum(logged_lumi)/1e6 #pb^-1
        self["runtime"] = run_time
        self["shifttime"] = shift_time
        if self._timedelta_sum(self["runtime"]) != datetime.timedelta(0):
            self["shifteff"] = self._timedelta_sum(self["runtime"])/self._timedelta_sum(self["shifttime"])
        else: self["shifteff"] = 0.0
        if self["dlumi"] != 0:
            self["ineff"] = self["clumi"]/self["dlumi"]
        else: self["ineff"] = 0.0

    def _time_overlap(self, ti_1, ti_2):
        if ti_1[1]>=ti_2[0] and ti_2[1]>=ti_1[0]:
            if ti_1[0] <= ti_2[0] <= ti_1[1]: start = ti_2[0]
            else: start = ti_1[0]
            stop = min(ti_1[1], ti_2[1])
            return abs(start-stop)
        else: return datetime.timedelta(hours=0)


    def _format_shift(self, shifts):
        return [datetime.datetime.strptime(shift[0]+" {0}".format(self["daytime_time"][shift[1]]), "%Y-%m-%d %H:%M:%S") for shift in shifts]

    def _timedelta_sum(self, timedeltas):
        time_sum = datetime.timedelta(0)
        for timedelta in timedeltas:
            time_sum = time_sum + timedelta
        return time_sum

    def get_name(self):
        return self["name"]

    def get_dlumi(self):
        return self["dlumi"]

    def get_clumi(self):
        return self["clumi"]

    def get_runtime(self):
        return self["runtime"]

    def get_runtime_sum(self):
        return self._timedelta_sum(self["runtime"])

    def get_shifttime(self):
        return self["shifttime"]

    def get_shifttime_sum(self):
        return self._timedelta_sum(self["shifttime"])

    def get_shifteff(self):
        return self["shifteff"]

    def get_ineff(self):
        return self["ineff"]

    def describe(self):
        name = self['name']
        shifttime_tot = self.get_shifttime_sum()
        runtime_tot = self.get_runtime_sum()
        runtime_frac = round(self["shifteff"]*100,self["digits"])
        del_lumi = round(self["dlumi"],self["digits"])
        col_lumi = round(self["clumi"],self["digits"])
        lumi_frac = round(self["ineff"]*100,self["digits"])

        description = (
            f'Name: {name}\nTotal time shifted: {shifttime_tot}, '
            f'time in stable beams condition: {runtime_tot} ({runtime_frac}%)'
            f'\nDelivered Lumi: {del_lumi:.2f}, collected Lumi: {col_lumi:.2f}'
            f' pb^-1 ({lumi_frac}%).'
        )
        return description

def shiftsummary(rundb, shifters, output_dir):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import json
    import os
    import datetime

    # Read and format data
    df = pd.read_csv(rundb)
    df["time_total"] = [
        datetime.timedelta(seconds=duration) for duration in df["time_total"]
    ]
    df["endtime_formatted"] = [
        datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        for timestamp in df["timestamp"]
    ]
    df["starttime_formatted"] = [
        endtime - duration for endtime, duration in
        zip(df["endtime_formatted"], df["time_total"])
    ]

    shifts_json = json.load(open(shifters, 'r'))

    daytimetitle_daytime_dict = {
        "morning":"06:30:00",
        "evening":"14:30:00",
        "night":"22:30:00"
    }

    duration = (8,0,0)   # hours, minutes, seconds
    shift_duration = datetime.timedelta(
        hours=duration[0], minutes=duration[1], seconds=duration[2]
    )

    shifter_group = np.array([
        Shifter(shifter, df, shifts_json['shifters'][shifter]['shifts'])
        for shifter in shifts_json['shifters'].keys()
    ])

    descriptions = []

    for shifter in shifter_group:
        descriptions.append(shifter.describe())

    summary = '\n'.join(descriptions)
    print(summary)
    with open(os.path.join(output_dir, 'summary.log'), 'w') as logfile:
        logfile.write(summary)

    # Plot beamtime
    names_base = [shifter.get_name() for shifter in shifter_group]
    shifter_colors_base = [f'C{i}' for i in range(len(names_base))]

    shifttime = [
        shifter.get_shifttime_sum().total_seconds()/3600.
        for shifter in shifter_group
    ]
    runtime = [
        shifter.get_runtime_sum().total_seconds()/3600.
        for shifter in shifter_group
    ]

    # Sort for runtime
    runtime, shifttime, names, shifter_colors = zip(*sorted(
        zip(runtime, shifttime, names_base, shifter_colors_base), reverse=True)
    )

    sb_fracs = [run / shift for run, shift in zip(runtime, shifttime)]

    x_positions = range(len(names))
    plt.bar(x_positions, shifttime, color=shifter_colors, alpha=0.5)
    plt.bar(x_positions, runtime, color=shifter_colors)

    plt.xticks(x_positions, list(names))

    max_y = plt.gca().get_ylim()[1]
    for tick, sb_frac in enumerate(sb_fracs):
        plt.annotate(f'{sb_frac:.1%}', (tick, max_y/30), ha='center', color='white', fontweight='bold')

    plt.ylabel("Total time shifted / time with stable beams [h]")
    plt.savefig(os.path.join(output_dir, 'beamtime.pdf'))
    plt.clf()

    # Plot lumi plot
    dellumi = [shifter.get_dlumi() for shifter in shifter_group]
    collumi = [shifter.get_clumi() for shifter in shifter_group]
    lumi_fracs = [collum / dellum if dellum != 0 else 0 for collum, dellum in zip(collumi, dellumi)]

    # Sort for lumi_fracs
    lumi_fracs, dellumi, collumi, names, shifter_colors = zip(*sorted(
        zip(lumi_fracs, dellumi, collumi, names_base, shifter_colors_base), reverse=True)
    )

    x_positions = range(len(names))
    plt.bar(x_positions, dellumi, color=shifter_colors, alpha=0.5)
    plt.bar(x_positions, collumi, color=shifter_colors)

    plt.xticks(x_positions, list(names))

    max_y = plt.gca().get_ylim()[1]
    for tick, sb_frac in enumerate(lumi_fracs):
        plt.annotate(f'{sb_frac:.1%}', (tick, max_y/30), ha='center', color='white', fontweight='bold')

    plt.ylabel("Delivered / collected lumi while on shift [$pb^{-1}$]")
    plt.savefig(os.path.join(output_dir, 'lumi.pdf'))
