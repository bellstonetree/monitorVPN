import unittest

from runtime_environment import (
    MissingRuntimeComponents,
    detect_missing_components,
    format_missing_components,
)


class RuntimeEnvironmentTests(unittest.TestCase):
    def test_complete_windows_environment_has_no_missing_components(self) -> None:
        missing = detect_missing_components(
            platform_name="win32",
            version_info=(3, 14),
            module_loader=lambda _name: object(),
            executable_finder=lambda _name: r"C:\Windows\System32\netsh.exe",
        )

        self.assertEqual([], missing)

    def test_all_missing_components_are_named(self) -> None:
        def missing_module(_name: str) -> object:
            raise ImportError

        missing = detect_missing_components(
            platform_name="linux",
            version_info=(3, 8),
            module_loader=missing_module,
            executable_finder=lambda _name: None,
        )

        self.assertEqual(
            ["Microsoft Windows", "Python 3.9+", "Tkinter", "netsh"],
            missing,
        )

    def test_error_message_lists_every_missing_component(self) -> None:
        message = format_missing_components(["Tkinter", "netsh"])

        self.assertIn("- Tkinter", message)
        self.assertIn("- netsh", message)

        error = MissingRuntimeComponents(["Tkinter", "netsh"])
        self.assertEqual(("Tkinter", "netsh"), error.components)
        self.assertEqual(message, str(error))


if __name__ == "__main__":
    unittest.main()
