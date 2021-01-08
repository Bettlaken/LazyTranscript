# Python port of: https://github.com/IBM/wort-to-number
import functools

class WordToNumberConverter:

    numberDictionary = {
    "null": "0",
    "eins": "1",
    "zwei": "2",
    "drei": "3",
    "vier": "4",
    "fünf": "5",
    "fuenf": "5",
    "sechs": "6",
    "sieben": "7",
    "acht": "8",
    "neun": "9",
    "zehn": "10",
    "elf": "11",
    "zwölf": "12",
    "zwoelf": "12",
    "sechzehn": "16",
    "siebzehn": "17",
    "zwanzig": "20",
    "dreißig": "30",
    "dreissig" : "30",
    "vierzig": "40",
    "fünfzig": "50",
    "fuenfzig": "50",
    "sechzig": "60",
    "siebzig": "70",
    "achtzig": "80",
    "neunzig": "90",
    "hundert": "100",
    "einhundert": "100",
    "tausend": "1000",
    "eintausend": "1000"
    }

    def flat_map(self, array):
        a = []
        for ar in array:
            a = a + ar
        return a

    def insert_separators(self, array, separator):
        new_array = []
        i = 1

        while i < len(array):
            new_array.append(array[i-1])
            new_array.append(separator)
            i += 1

        new_array.append(array[i - 1])
        return new_array

    def transform_with_multiplican(self, string, index, multiplicand):
        multiplier = None

        if string[0:index] == "ein":
            multiplier = 1
        else:
            multiplier = self.cast_to_int(self.map_word_to_number(string[0:index]))
            if multiplier == 0:
                multiplier = 1

        rest = self.map_word_to_number(string[index+7:])

        if rest is None:
            rest = 0

        return str(multiplier * multiplicand + self.cast_to_int(rest))

    def map_word_to_number(self, word):
        index = None

        if self.numberDictionary.get(word):
            return self.numberDictionary[word]

        for digit, multiplicant in [("tausend", 1000), ("hundert", 100)]:
            index = self.find_index(word, digit)
            if index != -1:
                return self.transform_with_multiplican(word, index, multiplicant)

        index = self.find_index(word, "zehn")

        if index != -1 and word.endswith("zehn"):
            return str(10 + self.cast_to_int(self.numberDictionary.get(word[0:index])))

        array = word.split("und")
        if len(array) <= 1:
            return word

        return self.sum_numbers(array)

    def sum_numbers(self, array):
        return functools.reduce(self.reduce, array)

    def reduce(self, total, current):
        total = self.numberDictionary.get(total)
        if current is None:
            return self.cast_to_int(total)

        if current == "ein":
            return self.cast_to_int(total) + 1

        return self.cast_to_int(total) + self.cast_to_int(self.numberDictionary.get(current))

    def find_index(self, word, to_search):
        if not to_search:
            return len(word)
        try:
            index = word.index(to_search)
        except ValueError:
            index = -1
        return index

    def cast_to_int(self, word):
        if word is None:
            return 0
        if isinstance(word, int):
            return word
        if len(word) == 0:
            return 0
        else:
            return int(word)


if __name__ == '__main__':
    text = "dreihundertdreiunddreissig"
    conv = WordToNumberConverter()
    print(conv.map_word_to_number(text))



