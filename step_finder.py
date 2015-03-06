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
            # Construct natural string version
            step_usage = re.sub(r'^@(.*)\(["\'](.*)["\']\)', r'\1 \2', step)
            if self._match_step_to_text(text, step_usage):
                matches.append((step_usage, self._strip_to_text_placement(text, step_usage)))
        return sorted(matches)

    def _find_steps_in_file(self, filename):
        lines = self.os_interface.open(filename)
        for linenumber in range(len(lines)):
            match = self._line_is_a_step(lines[linenumber])
            if match:
                self.steps.append((match.group(), linenumber, filename))

    def _line_is_a_step(self, text):
        pattern = re.compile(r'(@(.*)(\(["\'].*))["\']\)')
        return re.match(pattern, text)

    def _match_step_to_text(self, text, step_usage):
        step_usage_matcher = step_usage[:len(text)]
        return text.lower() == step_usage_matcher.lower()

    def _strip_to_text_placement(self, prefix, full_step):
        """ Remove last word from prefix """
        if re.search(r'\s', prefix):
            prefix = re.sub(r'(.*)\s[^\s]+$', r'\1', prefix)
            return full_step[len(prefix):].strip()
        return full_step
