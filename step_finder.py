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
                matches.append((step_usage, step_usage))
        return matches

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
        if text[:3].lower() == "and":
            text = text[3:].lstrip()
            step_usage = re.sub(r'^(Given|When|Then) (.+)', r'\2', step_usage, flags=re.IGNORECASE)
            step_usage_matcher = step_usage[:len(text)]
            return text.lower() == step_usage_matcher.lower()
        else:
            step_usage_matcher = step_usage[:len(text)]
            return text.lower() == step_usage_matcher.lower()
