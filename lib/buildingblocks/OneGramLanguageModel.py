from lib.Configuration import Configuration
from data.datasets import identifyDataset
import pylev

DEFAULT_CONFIG = {
    "punctuation": " '.-,/(?);:*!\"&",
    "separator": "|",
    "dataset": "iam",
    "source": "./data/raw",
    "subset": "words"
}


class OneGramLanguageModel(object):

    def __init__(self, config={}):
        self.config = Configuration(config, DEFAULT_CONFIG)
        self.dataset = identifyDataset(self.config["dataset"])
        self._build_dictionary()

    def _build_dictionary(self):
        self.dictionary = {}
        all_lines, _ = self.dataset.getFilesAndTruth(
            self.config["source"], self.config["subset"])
        for line in all_lines:
            for word in line["truth"].split(self.config["separator"]):
                if word not in self.config["punctuation"]:
                    word = word.lower()
                    self.dictionary[word] = 1 if word not in self.dictionary else self.dictionary[word] + 1

    def __call__(self, regions):
        return [self._process_region(region) for region in regions if region.text is not None and region.text != '']

    def _process_region(self, region):
        return self.config["separator"].join([self._process_word(word) for word in region.text.split(self.config["separator"])])

    def _process_word(self, word: str):
        if word.lower() in self.config["punctuation"] or word.lower() in self.dictionary:
            return word
        word_lower = word.lower()
        new_word = self._get_best_match(word_lower)
        return new_word

    def _get_case_map(self, word):
        word_lower = word.lower()
        return [1 if word_lower[idx] != word[idx] else 0 for idx in range(len(word))], word_lower

    def _apply_case_map(self, word, word_map):
        return ''.join([word[idx].upper() if word_map[idx] else word[idx] for idx in range(len(word))])

    def _get_best_match(self, word):
        minimum_lev = len(word)
        matches = []
        for new_word in self.dictionary.keys():
            lev = pylev.levenshtein(word, new_word)
            if lev < minimum_lev:
                matches = [new_word]
                minimum_lev = lev
            elif lev == minimum_lev:
                matches.append(new_word)

        max_prob = 0
        final_match = ""
        for match in matches:
            if max_prob < self.dictionary[match]:
                max_prob = self.dictionary[match]
                final_match = match
        return final_match


if __name__ == "__main__":

    class test(object):
        text = "An|aahple|does|not|fahl|far|from|the|tree|!"

    model = OneGramLanguageModel()
    print(model._process_region(test()))
