from typing import List

from PySide2.QtWidgets import QPushButton
from src.util.plugin_abstract import IPlugin
from faker import Faker

class FakeButton(QPushButton):

    def __init__(self, parent, fake, word_pos):
        super(FakeButton, self).__init__()
        self.parent = parent
        self.fake = fake
        self.word_pos = word_pos
        self.setText(fake)
        self.clicked.connect(self.modify)

    def modify(self):
        self.parent.plugin_manager.replace_selection(self.fake)
        self.parent.add_used(self.fake)

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.faker : Faker = None
        self.used = []

    # probably better to make them static
    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        if self.faker is None:
            self.faker = Faker(self.plugin_manager.get_language())

        if self.plugin_manager.get_language().replace("-", "_") not in self.faker.locales:
            self.faker = Faker(self.plugin_manager.get_language())


        fake_data = [self.faker.first_name_female() + " " + self.faker.last_name(),
                     self.faker.first_name_male() + " " + self.faker.last_name(),
                     self.faker.street_address(),
                     self.faker.postcode(),
                     self.faker.phone_number()]

        fake_btns = []
        for fake in fake_data:
            fake_btns.append(FakeButton(self, fake, word_pos))
        self.plugin_manager.add_new_word_by_word_action(fake_btns, self.get_name(), word, word_pos)

        if len(self.used) > 0:
            used_btns = []
            for used in self.used:
                used_btns.append(FakeButton(self, used, word_pos))
            self.plugin_manager.add_new_word_by_word_action(used_btns, self.get_name() + " used", word, word_pos)

    def add_used(self, fake):
        if fake not in set(self.used):
            self.used.append(fake)

    def get_name(self) -> str:
        return "Fake Data"