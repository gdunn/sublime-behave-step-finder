import os
import glob
import codecs


class OsInterface():
    def __init__(self, step_path, root_path):
        self.step_path = step_path
        self.root_path = root_path

    def get_files(self):
        files = []
        for path in self.step_path:
            search_path = os.path.join(self.root_path, path)
            files.extend(glob.glob(search_path))

        return files

    def open(self, filename):
        lines = []
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f:
                lines.append(line)

        return lines
