#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt

from pathlib import Path
from zipfile import ZipFile


class AstData:
    def __init__(self):
        """
        Class which contains helper functions for data wrangling - getting ready for asterisk data analysis
        :param home: home directory of git repo
        """
        self.home = Path(__file__).parent.absolute()

    def view_images(self, subject_name, hand_name, translation_name, rotation_name, trial_number):
        """
        View images of trial specified as a video
        :param subject_name: name of subject
        :param hand_name: name of hand
        :param translation_name: name of direction
        :param rotation_name: name of rotation
        :param trial_number: trial number
        """
        os.chdir(self.home)
        data_name = f"{subject_name}_{hand_name}_{translation_name}_{rotation_name}_{trial_number}"
        file_dir = f"viz/{data_name}/"
        os.chdir(file_dir)

        files = [f for f in os.listdir('.') if f[-3:] == 'jpg']
        files.sort()

        img = None
        for f in files:
            im = plt.imread(f)

            if img is None:
                img = plt.imshow(im)
            else:
                img.set_data(im)

            plt.pause(.01)
            plt.draw()

        repeat = smart_input("Show again? [y/n]", "consent")
        if repeat == "y":
            # run again
            self.view_images(subject_name, hand_name, translation_name,
                             rotation_name, trial_number)
        else:
            # stop running
            quit()
    
    def single_extract(self, subject_name, hand_name, translation_name, rotation_name, trial_number):
        """
        Extract a single zip file, specified by parameters.
        :param subject_name: name of subject
        :param hand_name: name of hand
        :param translation_name: name of direction
        :param rotation_name: name of rotation
        :param trial_number: trial number
        """
        folders = f"asterisk_test_data/{subject_name}/{hand_name}/"
        file_name = f"{subject_name}_{hand_name}_{translation_name}_{rotation_name}_{trial_number}"

        extract_from = folders+file_name+".zip"

        extract_to = f"viz/{file_name}"

        with ZipFile(extract_from, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            print(f"Completed Extraction: {extract_to}")

    def batch_extract(self, subject_name, hand_name):
        """
        Extract a batch of zip files for a specific subject and hand
        :param subject_name: name of subject
        :param hand_name: name of hand
        """
        for s, h, t, r, n in generate_names_with_s_h(subject_name, hand_name):
            self.single_extract(s, h, t, r, n)


class AstNaming:
    options = {
        "subjects": ["sub1", "sub2", "sub3"],
        "hands": ["2v2", "2v3", "3v3", "barrett", "basic", "m2active", "m2stiff", "modelvf"],  # "human"
        "hands_only_n": ["basic", "m2stiff", "modelvf"],
        "translations": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "translations_all": ["a", "b", "c", "d", "e", "f", "g", "h", "n"],
        "rotations": ["n", "m15", "p15"],
        "rotations_n_trans": ["cw", "ccw"],
        "numbers": ["1", "2", "3", "4", "5"]
    }
    values = {  # TODO: make this use generate_options
        "subjects": ["sub1", "sub2", "sub3"],
        "hands": ["2v2", "2v3", "3v3", "barrett", "basic", "human", "m2active", "m2stiff", "modelvf"],
        "translations": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "translations_w_n": ["a", "b", "c", "d", "e", "f", "g", "h", "n"],
        "rotation_combos": ["n", "m15", "p15"],
        "rotations_n_trans": ["cw", "ccw"],
        "numbers": ["1", "2", "3", "4", "5"],
        "consent": ["y", "n"]
    }

    def __init__(self):
        pass

    def get_option(self, key):
        """
        Return set of objects for a given key. If no key, returns
        :param key:
        :return:
        """
        try:
            return self.options[key]
        except:
            return None

    def add_option(self, key, options, overwrite=False):
        """
        Adds a set of options at given key.
        Has the option to overwrite at an existing key, otherwise it won't overwrite.

        Returns True if operation succeeded, otherwise returns False
        """
        if key in self.options.keys:
            if overwrite:
                self.options[key] = options
                return True
            else:
                return False
        else:
            self.options[key] = options
            return True


# TODO: move following functions into a AstNaming object?
def generate_options(key):
    """
    One function to return all sorts of parameter lists. Mainly to be used outside of data manager
    :param key: the key of the list that you want
    :return: list of parameters
    """
    opt = AstNaming()
    return opt.get_option(key)


def generate_t_r_pairs(hand_name, no_rotations=False):
    """
    Generator that feeds all trial combinations pertaining to a specific hand
    :param hand_name: name of hand specified
    :return: yields translation and rotation combinations
    """
    translations = generate_options("translations_all")
    n_trans_rot_opts = generate_options("rotations_n_trans")
    rotations = generate_options("rotations")

    for t in translations:
        if t == "n":  # necessary to divide rotations because cw and ccw only happen with no translation
            if hand_name in generate_options("hands_only_n"):
                continue
            else:
                rot = n_trans_rot_opts
        else:
            if hand_name in generate_options("hands_only_n") or no_rotations:
                rot = "n"
            else:
                rot = rotations

        for r in rot:
            yield t, r


def generate_names_with_s_h(subject_name, hand_name, no_rotations=False):
    """
    Generates all trial combinations with a specific hand name
    :param subject_name: name of subject
    :param hand_name: name of hand
    :return: yields all parameters
    """
    num = generate_options("numbers")

    for t, r in generate_t_r_pairs(hand_name, no_rotations=no_rotations):
        for n in num:
            yield subject_name, hand_name, t, r, n


def generate_all_names(subject=None, hand_name=None, no_rotations=False):
    """
    Generate all combinations of all parameters
    :param subject: list of subjects to provide, if none provided defaults to all subjects
    :param hand_name: list of hands to provide, if none provided defaults to all hands
    :return: yields all combinations specified
    """
    # TODO: make smart version so you can be picky with your options... make the constant lists as default parameters
    if subject is None:
        subject = generate_options("subjects")

    if hand_name is None:
        hand_name = generate_options("hands")

    for s in subject:
        for h in hand_name:
            yield generate_names_with_s_h(s, h, no_rotations=no_rotations)


def smart_input(prompt, option, valid_options=None):
    """
    Asks for input and continues asking until there is a valid response
    :param prompt: the prompt that you want printed
    :param option: the option you want the input to choose from,
        if not in the options will look at valid_options for option
    :param valid_options: provides the ability to specify your own custom options
    """
    values = {  # TODO: make this use generate_options
        "subjects": ["sub1", "sub2", "sub3"],
        "hands": ["2v2", "2v3", "3v3", "barrett", "basic", "human", "m2active", "m2stiff", "modelvf"],
        "translations": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "translations_w_n": ["a", "b", "c", "d", "e", "f", "g", "h", "n"],
        "rotation_combos": ["n", "m15", "p15"],
        "rotations_n_trans": ["cw", "ccw"],
        "numbers": ["1", "2", "3", "4", "5"],
        "consent": ["y", "n"]
        }

    if option not in values.keys() and valid_options:  # TODO: Do as try catch clause
        values[option] = valid_options
    elif option not in values.keys() and valid_options is None:
        print("Please provide the valid inputs for your custom option")

    while True:
        print(prompt)
        print(f"Valid options: {values[option]}")
        response = str(input())

        if response in values[option]:
            break
        else:
            print("Invalid response.")

    return response


class AstDir:
    """
    Manages the folder paths where data is stored.
    """
    def __init__(self, home_dir=None, viz_folder_name="viz", aruco_folder_name="aruco_data",
                 trial_folder_name="trial_data", results_folder_name="results"):
        if home_dir is None:
            self.home = Path(__file__).parent.absolute()
        else:
            self.home = home_dir

        self.viz_folder = viz_folder_name  # where visual data is stored
        self.aruco_folder = aruco_folder_name  # where aruco analysis data is stored
        self.trial_folder = trial_folder_name  # where trial path data (with filtering) is stored
        self.results_folder = results_folder_name  # where metric results and images are stored


if __name__ == "__main__":
    """
    Run this file like a script and you can do everything you need to here.
    """
    data_manager = AstData()

    print("""
        ========= ASTERISK TEST DATA MANAGER ==========
          I MANAGE YOUR DATA FOR THE ASTERISK STUDY
              AT NO COST, STRAIGHT TO YOUR DOOR!
                           *****

        What can I help you with?
        1 - view a set of images like a video
        2 - extract a single data zip file
        3 - extract a batch of zip files
    """)
    ans = smart_input("Enter a function", "mode", ["1", "2", "3"])
    subject = smart_input("Enter subject name: ", "subjects")
    hand = smart_input("Enter name of hand: ", "hands")

    if ans == "1":
        translation = smart_input("Enter type of translation: ", "translations")
        rotation = smart_input("Enter type of rotation: ", "rotation_combos")
        trial_num = smart_input("Enter trial number: ", "numbers")

        data_manager.view_images(subject, hand, translation, rotation, trial_num)

    elif ans == "2":
        translation = smart_input("Enter type of translation: ", "translations")
        rotation = smart_input("Enter type of rotation: ", "rotation_combos")
        trial_num = smart_input("Enter trial number: ", "numbers")

        data_manager.single_extract(subject, hand, translation, rotation, trial_num)

    elif ans == "3":
        data_manager.batch_extract(subject, hand)

    else:
        print("Invalid entry. ")
        quit()
