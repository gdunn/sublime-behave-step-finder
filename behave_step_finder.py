# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import os
import re
import threading
import os_interface
import step_finder


# Static data
shared_data = {
    'finder': None,
    'steps': []
}


class BehaveBaseCommand(sublime_plugin.WindowCommand, object):
    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)
        self.load_settings()

    def load_settings(self):
        self.settings = sublime.load_settings("behaveStepFinder.sublime-settings")
        self.steps_path = self.settings.get('behave_steps_path')  # Default is "IntegTests/steps/steps_*.py"

    def find_all_steps(self):
        os.chdir(self._get_root_folder())
        os_access = os_interface.OsInterface(self.steps_path)
        finder = step_finder.StepFinder(os_access)
        self.steps = finder.find_all_steps()

    def step_found(self, index):
        if index >= 0:
            if self.window.num_groups() > 1:
                self.window.focus_group(0)

            file_path = self.steps[index][2]
            file_path = os.path.normpath(file_path)
            file_path = os.path.join(self._get_root_folder(), file_path)
            view = self.window.open_file(file_path)
            self.active_ref = (view, self.steps[index][1])
            self.mark_step()

    def mark_step(self):
        view = self.window.active_view()

        if view.is_loading():
            sublime.set_timeout(self.mark_step, 50)
        else:
            view.run_command("goto_line", {"line": self.active_ref[1] + 1})

    def _get_root_folder(self):
        if len(self.window.folders()) == 0:
            return "No path found"

        return self.window.folders()[0]


class MatchStepCommand(BehaveBaseCommand):
    def __init__(self, window):
        BehaveBaseCommand.__init__(self, window)
        self.words = self.settings.get('behave_code_keywords')

    def run(self, file_name=None):
        self.get_line()

    def get_line(self):
        view = self.window.active_view()
        line_sel = view.line(view.sel()[0])
        text_line = view.substr(line_sel).strip()
        self.cut_words(text_line)

    def cut_words(self, text):
        upcased = [up.capitalize() for up in self.words]
        expression = "^{0}".format('|^'.join(upcased))

        pattern = re.compile(expression)
        short_text = re.sub(pattern, '', text).strip()
        self.find_all_steps()

        step_filter = re.compile(r'@.*\(["\'](.*)["\']\)')  # map all steps

        for step in self.steps:
            step_text = re.match(step_filter, step[0]).group(1)
            step_pattern = re.sub("{.*?}", "(.+)", step_text)
            step_regex = re.compile(step_pattern)
            match = re.match(step_regex, short_text)
            if match:
                index = self.steps.index(step)
                self.step_found(index)
            else:
                sublime.status_message('Can\'t find a match')


class behaveStepFinderCommand(BehaveBaseCommand):
    def __init__(self, window):
        BehaveBaseCommand.__init__(self, window)

    def run(self, file_name=None):
        self.list_steps()

    def list_steps(self):
        self.find_all_steps()
        steps_only = [x[0] for x in self.steps]
        self.window.show_quick_panel(steps_only, self.step_found)


class BehaveStepCollectorThread(threading.Thread):

    def __init__(self, root_path, steps_path):
        self.root_path = root_path
        self.steps_path = steps_path
        threading.Thread.__init__(self)

    def run(self):
        os.chdir(self.root_path)
        os_access = os_interface.OsInterface(self.steps_path)
        shared_data["finder"] = step_finder.StepFinder(os_access)
        shared_data["steps"] = shared_data["finder"].find_all_steps()


class BehaveAutoCompleteEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if is_feature_file_view(view):
            BehaveStepCollectorThread(self._get_root_folder(view), self._get_steps_path()).start()

    def on_load(self, view):
        if is_feature_file_view(view) and is_feature_file(view.file_name()):
            BehaveStepCollectorThread(self._get_root_folder(view), self._get_steps_path()).start()

    def on_query_completions(self, view, prefix, locations):
        if is_feature_file_view(view) and shared_data["finder"]:
            (predicate, search) = find_predicate(view)
            matches = []
            if search:
                matches.extend(shared_data["finder"].match(search))
            if predicate:
                matches.extend(shared_data["finder"].match(predicate))
            if not search and predicate is None:
                matches = shared_data["finder"].match(prefix)
            return (matches, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        return ([], 0)

    def _get_root_folder(self, view):
        if view.window() is None or len(view.window().folders()) == 0:
            """ Try and get it from the filename instead """
            return os.path.dirname(view.file_name())

        return view.window().folders()[0]

    def _get_steps_path(self):
        settings = sublime.load_settings("behaveStepFinder.sublime-settings")
        return settings.get('behave_steps_path')


def find_predicate(view):
    predicate = None
    search = None
    for sel in view.sel():
        if sel.empty():
            match = None
            while not match or sel.b > -1:
                line = view.substr(view.line(sel.b)).strip()
                if search is None:
                    search = line
                match = re.match(r'^(given|when|then)', line, re.IGNORECASE)
                if match:
                    predicate = match.group(0).lower()
                    break
                else:
                    row, col = view.rowcol(sel.b)
                    sel = sublime.Region(sel.a, view.text_point(row - 1, col))
            break
    search = re.sub(r'^(given|when|then|and)\s?', '', search)
    return (predicate, search)


def is_feature_file_view(view):
    is_feature_filename = view.file_name() and is_feature_file(view.file_name())
    is_gherkin_syntax = 'Cucumber' in view.settings().get('syntax')
    return is_feature_filename or is_gherkin_syntax


def is_feature_file(file):
    return file and file.endswith('.feature')
