# Exercise 1: Simplify a StringFormatter
# Simplify StringFormatter
# Solved
# Problem: A developer built an overengineered string formatting system. There is a FormatterRegistry that stores formatters, a FormatterFactory that creates them, and a FormatterChain that applies them in sequence. All of this just to format a user's display name (trim whitespace and capitalize the first letter).

# Your task: replace the entire system with a single formatDisplayName method.

# Requirements:

# Accept a raw name string (e.g., " john doe ")
# Trim leading and trailing whitespace
# Capitalize the first letter of the result
# Return the formatted string (e.g., "John doe")


class DisplayNameFormatter:
    def format_display_name(self, name: str) -> str:
        trimmed = name.strip()
        if not trimmed:
            return ""
        return trimmed[0].upper() + trimmed[1:].lower()

# Test
formatter = DisplayNameFormatter()
print(formatter.format_display_name("  john doe  "))
print(formatter.format_display_name("ALICE"))
print(formatter.format_display_name("  bob  "))




# Exercise 2: Build a Simple ReportExporter
# Build a Simple ReportExporter
# Problem: Build a simple CSV report exporter. No interfaces, no abstract classes, no factory. Just a class that takes a list of records and writes them as CSV.

# Requirements:

# Accept a list of string arrays, where each array is a row.
# The first row is the header.
# Return the CSV as a single string (rows separated by newlines, values separated by commas).


class ReportExporter:
    def export_csv(self, rows: list[list[str]]) -> str:
        # Your implementation here
        return "\n".join(",".join(row) for row in rows)

# Test
exporter = ReportExporter()
data = [
    ["Name", "Age", "City"],
    ["Alice", "30", "New York"],
    ["Bob", "25", "London"]
]
print(exporter.export_csv(data))