import glob
import codecs


class OsInterface():
    def __init__(self, step_path):
        self.step_path = step_path

    def get_files(self):
        return glob.glob(self.step_path)

    def open(self, filename):
        lines = []
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f:
                lines.append(line)

        return lines
