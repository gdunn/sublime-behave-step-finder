import step_finder
import unittest


def buildStepFinderWithSteps(steps):
    class MockOs():
        def get_files(self):
            return ["common_steps.py"]

        def open(self, filename):
            return steps

    mock_os = MockOs()
    finder = step_finder.StepFinder(mock_os)
    finder.find_all_steps()
    return finder


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

    def test_get_simple_complete_match(self):
        finder = buildStepFinderWithSteps(["@Given('there is a step')"])
        matches = finder.match("Given there is a ste")
        self.assertEqual(matches[0], ("Given there is a step", "step"))

    def test_no_match(self):
        finder = buildStepFinderWithSteps(["@Given('there is a step')"])
        matches = finder.match("Given there is a no")
        self.assertEqual(len(matches), 0)

    def test_match_second(self):
        finder = buildStepFinderWithSteps(["@Given('there is a first step')", "@Then('there is a second step')"])
        matches = finder.match("th")
        self.assertEqual(matches[0], ("Then there is a second step", "Then there is a second step"))

    def test_do_not_match_later_part_in_string(self):
        finder = buildStepFinderWithSteps(["@Given('there is a first step')", "@Then('there is a second step')"])
        matches = finder.match("step")
        self.assertEqual(len(matches), 0)

    def test_all_matches(self):
        finder = buildStepFinderWithSteps(["@When('the device is turned on')", "@When('the device is on')"])
        matches = finder.match("When the device")
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], ("When the device is on", "device is on"))
        self.assertEqual(matches[1], ("When the device is turned on", "device is turned on"))

    def test_multiple_matches(self):
        finder = buildStepFinderWithSteps(["@Given('there is a first step')", "@When('the device is turned on')", "@When('the device is on')"])
        matches = finder.match("When the device")
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], ("When the device is on", "device is on"))
        self.assertEqual(matches[1], ("When the device is turned on", "device is turned on"))

    def test_and_matches_none(self):
        finder = buildStepFinderWithSteps(["@Given('there is a first step')", "@When('the device is turned on')", "@When('the device is on')"])
        matches = finder.match("And the device")
        self.assertEqual(len(matches), 0)

    def test_results_are_sorted(self):
        finder = buildStepFinderWithSteps(["@Given('there is a first step')", "@When('the device deactivates')", "@When('the device activates')"])
        matches = finder.match("When the device")
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], ("When the device activates", "device activates"))
        self.assertEqual(matches[1], ("When the device deactivates", "device deactivates"))

    def test_trailing_space(self):
        finder = buildStepFinderWithSteps(["@Given('the setup is okay')", "@Given('there is no setup')"])
        matches = finder.match("Given the ")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], ("Given the setup is okay", "setup is okay"))


if __name__ == '__main__':
    unittest.main()
