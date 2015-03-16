import re


class StepFinder():
    def __init__(self, os_interface):
        self.os_interface = os_interface
        self.steps = []

    def find_all_steps(self):
        self.steps = []

        all_step_files = self.os_interface.get_files()
        for filename in all_step_files:
            self._find_steps_in_file(filename)

        return self.steps

    def match(self, text):
        matches = []
        for (step, index, filename) in self.steps:
            class SubstituteCounter:
                def __init__(self):
                    self.count = 0

                def substitute_variable(self, m):
                    self.count += 1
                    return "$" + str(self.count)

            counter = SubstituteCounter()

            step_label = re.sub(r'^@(.*)\(["\'](.*)["\']\)', r'\1 \2', step)
            step_usage = re.sub(r'\{[^}]+\}', counter.substitute_variable, step_label)
            if self._match_step_to_text(text, step_usage):
                matches.append((step_label, self._strip_to_text_placement(text, step_usage)))
        return sorted(matches)

    def _find_steps_in_file(self, filename):
        lines = self.os_interface.open(filename)
        for linenumber in range(len(lines)):
            match = self._line_is_a_step(lines[linenumber])
            if match:
                self.steps.append((match.group(), linenumber, filename))
            elif lines[linenumber].strip() and (linenumber + 1) < len(lines):
                line = self._double_line_is_a_step(lines[linenumber].strip() + lines[linenumber+1].strip())
                if line:
                    self.steps.append((line, linenumber, filename))

    def _line_is_a_step(self, text):
        pattern = re.compile(r'(@(.+)(\(["\'].+))["\']\)')
        return re.match(pattern, text)

    def _double_line_is_a_step(self, double_line):
        pattern = re.compile(r'@(.+)\(["\'](.+)["\']["\'](.+)["\']\)')
        match = re.match(pattern, double_line)
        if match:
            return "@{0}('{1}{2}')".format(match.group(1), match.group(2), match.group(3))
        return False

    def _match_step_to_text(self, text, step_usage):
        step_usage_matcher = step_usage[:len(text)]
        return text.lower() == step_usage_matcher.lower()

    def _strip_to_text_placement(self, prefix, full_step):
        """ Remove last word from prefix """
        if re.search(r'\s', prefix):
            prefix = re.sub(r'(.*)\s[^\s]+$', r'\1', prefix)
            return full_step[len(prefix):].strip()
        return full_step
