class Sequence:

    def __init__(self, repeated_part: list[str], repeated_times: int, skip: int, skip_last: int):
        self.repeated_part = repeated_part
        self.repeated_times = repeated_times
        self.skip = skip
        self.skip_last = skip_last

    def __str__(self):
        if len(self.repeated_part) == 1:
            return f"{''.join(self.repeated_part)}x{self.repeated_times}"
        return f"{self.repeated_part}x{self.repeated_times}"

    def represent(self):
        return self.repeated_part, self.repeated_times


def represent(data: list):
    result = ""
    for lines, repetitions in data:
        line = "\n".join(lines)
        if repetitions > 1:
            result += f"[{line}]x{repetitions}\n"
        else:
            result += line
    return result


def merge_lines(lines):
    return represent(compile_merges(lines))


def compile_merges(lines):
    result = []
    skip = 0
    while skip < len(lines) - 1:
        found, sequence = find_repeating_sequence(lines[skip:])
        if found:

            result.append((lines[:sequence.skip], 1))
            skip = len(lines) - sequence.skip_last
            result.append(sequence.represent())
        else:
            break
    result.append((lines[skip:], 1)) if lines[skip:] else None
    return result


def find_repeating_sequence(strings):
    for i in range(len(strings)):
        for j in range(len(strings)):
            result, repeated_part, repeated_times = get_repeating_sequence(
                strings[i if i > 0 else None:(-j) if j > 0 else None])
            if result:
                return True, Sequence(repeated_part, repeated_times, i, j)
    return False, None


def get_repeating_sequence(strings):
    n = len(strings)

    def is_repeating(sequence_length):
        for i in range(0, n, sequence_length):
            if strings[i:i + sequence_length] != strings[:sequence_length]:
                return False
        return True

    for sequence_length in range(1, n // 2 + 1):
        if n % sequence_length == 0:
            if is_repeating(sequence_length):
                return True, strings[:sequence_length], n // sequence_length

    return False, '', 0
