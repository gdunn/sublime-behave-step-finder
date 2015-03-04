import re


class StepFinder():
    def __init__(self, os_interface):
        self.os_interface = os_interface

    def find_all_steps(self):
        steps = []

        all_step_files = self.os_interface.get_files()
        for filename in all_step_files:
            steps.extend(self._find_steps_in_file(filename))

        return steps

    def _find_steps_in_file(self, filename):
        steps = []
        lines = self.os_interface.open(filename)
        for linenumber in range(len(lines)):
            match = self._match_step(lines[linenumber])
            if match:
                steps.append((match.group(), linenumber, filename))

        return steps

    def _match_step(self, text):
        pattern = re.compile(r'(@(.*)(\(["\'].*))["\']\)')
        return re.match(pattern, text)
