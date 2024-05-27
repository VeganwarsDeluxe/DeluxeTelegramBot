import uuid


class LineMerger:
    def __init__(self):
        self.salt = str(uuid.uuid4())[:6]

    def merge(self, text: str) -> str:
        return "\n".join(self.merge_cast(text))

    def merge_cast(self, text):
        variant_a = self.split_every_two(text, True)
        variant_b = self.split_every_two(text, False)

        t_merge_a = self.merge_twoline(variant_a)
        t_merge_b = self.merge_twoline(variant_b)

        o_merge_a = self.trim(self.merge_oneline(t_merge_a))
        o_merge_b = self.trim(self.merge_oneline(t_merge_b))

        print(o_merge_a)
        print(o_merge_b)

        if len(o_merge_a) >= len(o_merge_b):
            return o_merge_b
        else:
            return o_merge_a

    def trim(self, text: list):
        if text[0] == '':
            text.pop(0)
        elif text[-1] == '':
            text.pop(-1)
        return text

    def split_every_two(self, text, switch=False):
        lines = text.split('\n')
        new_text = []
        part = ""

        for index in range(len(lines)):
            switch = not switch
            if switch:
                part = lines[index]
                if index + 1 == len(lines):
                    new_text.append(part + self.salt)
                continue
            else:
                new_text.append(part + self.salt + lines[index])

        return new_text

    def merge_twoline(self, text):
        new_text = []
        counter = 1

        for index in range(len(text)):
            line = text[index]
            pair = line.split(self.salt, 1)

            if pair[0] == pair[1]:
                new_text.extend(pair)
            else:
                if index + 2 <= len(text) and text[index] == text[index + 1]:
                    counter += 1
                else:
                    if counter == 1:
                        new_text.extend(pair)
                    else:
                        new_text.extend(f"[{pair[0]}\n{pair[1]}]✖️{counter}".split('\n'))
                        counter = 1

        return new_text

    def merge_oneline(self, text):
        text += ['\n']
        new_text = []
        counter = 1

        for i in range(len(text)):

            if i == 0:
                continue

            if text[i] != text[i - 1]:
                new_line = f"{text[i - 1]}" if counter == 1 else f"[{text[i - 1]}]✖{counter}"
                new_text.append(new_line)
                counter = 1
            else:
                counter += 1

        return new_text