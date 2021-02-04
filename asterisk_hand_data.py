#!/usr/bin/env python3

import numpy as np
import pandas as pd
import math as m
from pathlib import Path
import pdb
import matplotlib.pyplot as plt
import asterisk_data_manager as datamanager
import asterisk_trial as trial
from asterisk_hand import HandObj


class AsteriskHandData:
    def __init__(self, subjects, hand_name):
        """
        Class to hold all the data pertaining to a specific hand.
        Combines data from all subjects
        """
        self.hand = HandObj(hand_name)
        self.subjects_containing = subjects
        self.data = self._gather_hand_data(subjects)
        self.filtered = False
        self.window_size = None

    def _gather_hand_data(self, subjects_to_get):
        """
        Returns a dictionary with the data for the hand, sorted by task.
        Each key,value pair of dictionary is:
        key: name of task, string. Ex: "a_n"
        value: list of AsteriskTrial objects for the corresponding task, with all subjects specified
        """
        data_dictionary = dict()
        for t, r in datamanager.generate_t_r_pairs(self.hand.get_name()):
            key = f"{t}_{r}"
            data_dictionary[key] = self._gather_trials(subjects_to_get, t, r, [1,2,3])

        return data_dictionary

    def _gather_trials(self, subjects, translation_label, rotation_label, trials):
        """
        Goes through data and compiles data with set attributes into an AsteriskTrial objects
        """
        gathered_data = list()
        for s in subjects:  # TODO: subjects is a list, make a type recommendation
            for n in trials:
                try:
                    asterisk_trial_file = f"{s}_{self.hand.get_name()}_{translation_label}_{rotation_label}_{n}.csv"
                    trial_data = trial.AsteriskTrial(asterisk_trial_file)
                    gathered_data.append(trial_data)
                except:
                    print("Skipping.")
                    continue

        return gathered_data

    def _get_batch(self, subject_to_run, trial_number):
        """
        Picks out the specified data
        """
        dfs = []
        translations = ["a", "b", "c", "d", "e", "f", "g", "h"]

        for dir in translations:
            dict_key = f"{dir}_n"
            trials = self.data[dict_key]
            # print(f"For {subject_to_run} and {trial_number}: {dir}")

            trial_we_want = None
            for t in trials:
                if (t.subject_num == subject_to_run) and (t.trial_num == trial_number):
                    # TODO: make sure trial_number is a string
                    trial_we_want = t
                    break
                # TODO: throw an exception in case there isn't the trial that we want

            # print("    ")

            dfs.append(trial_we_want)

        return dfs

    def filter_data(self, window_size=15):
        for key in self.data.keys():
            for t in self.data[key]:
                t.moving_average(window_size)

        self.filtered = True
        self.window_size = window_size

    def plot_data_subset(self, subject_to_run, trial_number, show_plot=True, save_plot=False):
        """
        Plots a subset of the data, as specified in parameters
        """
        colors = ["tab:blue", "tab:purple", "tab:red", "tab:olive",
                  "tab:cyan", "tab:green", "tab:pink", "tab:orange"]

        dfs = self._get_batch(subject_to_run, trial_number)  # TODO: make this work for the hand data object

        # plot data
        for i, df in enumerate(dfs):
            data_x, data_y, theta = df.get_poses()

            # data_x = pd.Series.to_list(df["f_x"])  # saving for reference, just in case for later
            # data_y = pd.Series.to_list(df["f_y"])
            # theta = pd.Series.to_list(df["f_rot_mag"])

            plt.plot(data_x, data_y, color=colors[i], label='trajectory')

            # plot data points separately to show angle error with marker size
            for n in range(len(data_x)):
                plt.plot(data_x[n], data_y[n], color=colors[i], alpha=0.5, markersize=10 * theta[n])

        # plot ideal lines
        self.plot_all_ideal(colors)

        plt.xticks(np.linspace(-0.5, 0.5, 11), rotation=30)
        plt.yticks(np.linspace(-0.5, 0.5, 11))

        plt.title(f"Plot: {subject_to_run}_{self.hand.get_name()}, set #{trial_number}")

        # saving figure
        # plt.savefig(f"fullplot4_{sub}_{hand}_{num}.jpg", format='jpg')  # name -> tuple: subj, hand  names

        if show_plot:
            plt.show()

        if save_plot:
            plt.savefig(f"pics/fullplot4_{subject_to_run}_{self.hand.get_name()}_{trial_number}.jpg", format='jpg')
            # name -> tuple: subj, hand  names
            print("Figure saved.")
            print(" ")

    def plot_data_1subject(self, subject_to_run):
        """
        Plots the data from one subject, averaging all of the data in each direction
        """
        pass

    def plot_data(self):
        """
        Plots all the data contained in object
        """
        pass

    def plot_all_ideal(self, order_of_colors):
        x_a, y_a = self.get_a()
        x_b, y_b = self.get_b()
        x_c, y_c = self.get_c()
        x_d, y_d = self.get_d()
        x_e, y_e = self.get_e()
        x_f, y_f = self.get_f()
        x_g, y_g = self.get_g()
        x_h, y_h = self.get_h()

        ideal_xs = [x_a, x_b, x_c, x_d, x_e, x_f, x_g, x_h]
        ideal_ys = [y_a, y_b, y_c, y_d, y_e, y_f, y_g, y_h]

        for i in range(8):
            plt.plot(ideal_xs[i], ideal_ys[i], color=order_of_colors[i], label='ideal', linestyle='--')

    # well, what I can do is do a linspace for both x and y...
    # its straightforward because these are perfect lines we are drawing
    def straight(self, num_points=11, mod=1):
        vals = np.linspace(0, 0.5, num_points)
        z = [0.] * num_points

        set1 = mod * vals
        return set1, z

    def diagonal(self, num_points=11, mod1=1, mod2=1):
        coords = np.linspace(0, 0.5, num_points)

        set1 = mod1 * coords
        set2 = mod2 * coords

        return set1, set2

    def get_a(self, num_points=11):
        y_coords, x_coords = self.straight(num_points)
        return x_coords, y_coords

    def get_b(self, num_points=11):
        x_coords, y_coords = self.diagonal(num_points)
        return x_coords, y_coords

    def get_c(self, num_points=11):
        x_coords, y_coords = self.straight(num_points)
        return x_coords, y_coords

    def get_d(self, num_points=11):
        x_coords, y_coords = self.diagonal(num_points=num_points, mod1=1, mod2=-1)
        return x_coords, y_coords

    def get_e(self, num_points=11):
        y_coords, x_coords = self.straight(num_points, mod=-1)
        return x_coords, y_coords

    def get_f(self, num_points=11):
        x_coords, y_coords = self.diagonal(num_points=num_points, mod1=-1, mod2=-1)
        return x_coords, y_coords

    def get_g(self, num_points=11):
        x_coords, y_coords = self.straight(num_points, mod=-1)
        return x_coords, y_coords

    def get_h(self, num_points=11):
        x_coords, y_coords = self.diagonal(num_points, mod1=-1)
        return x_coords, y_coords


test_type_name = ["Translation", "Rotation",
                  "Twist_translation", "undefined"]
translation_name = ["a", "b", "c", "d", "e", "f", "g", "h", "none"]
rotation_name = ["cw", "ccw", "none"]
twist_name = ["plus15", "minus15", "none"]
translation_angles = range(90, 90-360, -45)
twist_directions = {"Clockwise": -15, "Counterclockwise": 15}
rotation_directions = {"Clockwise": -25, "Counterclockwise": 25}
subject_nums = [1, 2, 3, 4, 5]


