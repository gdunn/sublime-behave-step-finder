import step_finder
import unittest


class TestStepFinder(unittest.TestCase):

    def test_no_matching_files(self):
        class MockOs():
            def get_files(self):
                return []

            def open(self, filename):
                assert(False)

        mock_os = MockOs()

        finder = step_finder.StepFinder(mock_os)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 0)

    def test_no_matching_lines(self):
        class MockOs():
            def get_files(self):
                return ["common_steps.py"]

            def open(self, filename):
                return ["# Just a comment"]

        mock_os = MockOs()

        finder = step_finder.StepFinder(mock_os)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 0)

    def test_search_and_find_one_step(self):
        class MockOs():
            def get_files(self):
                return ["common_steps.py"]

            def open(self, filename):
                return ["@Given('there is a step')"]

        mock_os = MockOs()

        finder = step_finder.StepFinder(mock_os)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0], ("@Given('there is a step')", 0, "common_steps.py"))

    def test_file_opened_matches(self):
        class MockOs1():
            def get_files(self):
                return ["common_steps.py"]

            def open(self, filename):
                assert(filename == "common_steps.py")
                return []

        class MockOs2():
            def get_files(self):
                return ["special.py"]

            def open(self, filename):
                assert(filename == "special.py")
                return []

        mock_os1 = MockOs1()
        mock_os2 = MockOs2()

        finder = step_finder.StepFinder(mock_os1)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 0)
        finder = step_finder.StepFinder(mock_os2)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 0)

    def test_search_and_find_two_steps(self):
        class MockOs():
            def get_files(self):
                return ["more_steps.py"]

            def open(self, filename):
                return [
                    "@Given('there is a step')",
                    "def impl(context):",
                    "    pass",
                    "",
                    "@When(\"it is ready\")  "]

        mock_os = MockOs()

        finder = step_finder.StepFinder(mock_os)
        steps = finder.find_all_steps()
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0], ("@Given('there is a step')", 0, "more_steps.py"))
        self.assertEqual(steps[1], ("@When(\"it is ready\")", 4, "more_steps.py"))


if __name__ == '__main__':
    unittest.main()
