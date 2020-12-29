import os
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtWidgets import QFileDialog, QPushButton, QLineEdit, QMessageBox, QDialog, QLabel, QCheckBox, QWidget

from models.save_file import HadesSaveFile
import gamedata

mainWin = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def except_hook(cls, exception, traceback):

    mainWin.error_widget.setVisible(1)
    mainWin.error_label.setText("{}: {}".format(exception.__class__.__name__, str(exception)))
    sys.__excepthook__(cls, exception, traceback)


def _easy_mode_level_from_damage_reduction(damage_reduction: int) -> int:
    # Make sure the damage reduction is between 20-80 as that is what the game uses, out of range might not be safe
    damage_reduction = max(20, min(80, damage_reduction))
    easy_mode_level = (damage_reduction - 20) / 2
    return easy_mode_level


def _damage_reduction_from_easy_mode_level(easy_mode_level: int) -> int:
    # Easy mode level is half the amount of damage reduction added to the base damage reduction from enabling god mode
    # easy mode level 10 => 20 + (10 * 2) = 40% damage reduction
    damage_reduction = (easy_mode_level * 2) + 20
    return damage_reduction


class App(QDialog):
    def __init__(self, application):
        super().__init__()
        self.app = application

        self.file_path = None
        self.save_file: HadesSaveFile = None
        self.dirty = False

        uic.loadUi(resource_path('pluto.ui'), self)  # Load the .ui file
        self.error_widget = self.findChild(QWidget, "errorWidget")
        self.error_label = self.findChild(QLabel, "errorValue")

        self.ui_state = self.findChild(QLabel, "state")

        self.error_widget.setVisible(0)

        self.load_button = self.findChild(QPushButton, "load")
        self.load_button.clicked.connect(lambda: self.load_file(self.get_save_file_name()))

        self.save_button = self.findChild(QPushButton, "save")
        self.save_button.clicked.connect(self.write_file)

        self.save_button = self.findChild(QPushButton, "export")
        self.save_button.clicked.connect(self.export_runs_as_csv)

        self.dump_lua_button = self.findChild(QPushButton, "button_dump_lua_state")
        self.dump_lua_button.clicked.connect(self.dump_lua_state)

        self.load_lua_button = self.findChild(QPushButton, "button_load_lua_state_and_save")
        self.load_lua_button.clicked.connect(self.load_lua_state_and_save)

        self.exit_button = self.findChild(QPushButton, "exit")
        self.exit_button.clicked.connect(self.safe_quit)

        self.interaction_reset = self.findChild(QPushButton, "interactionReset")
        self.interaction_reset.clicked.connect(self.reset_gift_record)

        self.path_label = self.findChild(QLabel, "pathValue")
        self.version_label = self.findChild(QLabel, "versionValue")
        self.run_label = self.findChild(QLabel, "runValue")
        self.location_label = self.findChild(QLabel, "locationValue")

        self.darkness_field = self.findChild(QLineEdit, "darknessEdit")
        self.gems_field = self.findChild(QLineEdit, "gemsEdit")
        self.diamonds_field = self.findChild(QLineEdit, "diamondsEdit")
        self.nectar_field = self.findChild(QLineEdit, "nectarEdit")
        self.ambrosia_field = self.findChild(QLineEdit, "ambrosiaEdit")
        self.keys_field = self.findChild(QLineEdit, "chthonicKeyEdit")
        self.titan_blood_field = self.findChild(QLineEdit, "titanBloodEdit")
        self.god_mode_damage_reduction_field = self.findChild(QLineEdit, "godModeDamageReductionEdit")

        self.hell_mode = self.findChild(QCheckBox, "hellModeCheckbox")

        self.show()  # Show the GUI

    def get_save_file_name(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            f"{QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]}/Saved Games/Hades",
            "All Files (*);;Hades Save Files (*.sav)",
            "Hades Save Files (*.sav)",
            options=options
        )
        # If user cancels we get an empty string
        return fileName

    def load_file(self, path):
        if not path:
            return

        self.file_path = path
        self.save_file = HadesSaveFile.from_file(self.file_path)

        self.error_widget.setVisible(0)

        self.path_label.setText(path)
        self.version_label.setText(str(self.save_file.version))
        self.run_label.setText(str(self.save_file.runs))
        self.location_label.setText(str(self.save_file.location))

        self.darkness_field.setText(str(self.save_file.lua_state.darkness))
        self.gems_field.setText(str(self.save_file.lua_state.gems))
        self.diamonds_field.setText(str(self.save_file.lua_state.diamonds))
        self.nectar_field.setText(str(self.save_file.lua_state.nectar))
        self.ambrosia_field.setText(str(self.save_file.lua_state.ambrosia))
        self.keys_field.setText(str(self.save_file.lua_state.chthonic_key))
        self.titan_blood_field.setText(str(self.save_file.lua_state.titan_blood))
        self.hell_mode.setChecked(bool(self.save_file.lua_state.hell_mode))
        self.god_mode_damage_reduction_field.setText(str(_damage_reduction_from_easy_mode_level(self.save_file.lua_state.easy_mode_level)))

        self.dirty = True
        self.ui_state.setText("Loaded!")

    def write_file(self):
        self.save_file.lua_state.darkness = float(self.darkness_field.text())
        self.save_file.lua_state.gems = float(self.gems_field.text())
        self.save_file.lua_state.diamonds = float(self.diamonds_field.text())
        self.save_file.lua_state.nectar = float(self.nectar_field.text())
        self.save_file.lua_state.ambrosia = float(self.ambrosia_field.text())
        self.save_file.lua_state.chthonic_key = float(self.keys_field.text())
        self.save_file.lua_state.titan_blood = float(self.titan_blood_field.text())
        self.save_file.lua_state.hell_mode = bool(self.hell_mode.isChecked())
        self.save_file.hell_mode_enabled = bool(self.hell_mode.isChecked())
        self.save_file.lua_state.easy_mode_level = _easy_mode_level_from_damage_reduction(float(self.god_mode_damage_reduction_field.text()))

        self.save_file.to_file(self.file_path)
        self.dirty = False
        self.ui_state.setText("Saved!")

    def dump_lua_state(self):
        if not self.file_path:
            self.ui_state.setText("No savegame loaded!")
            return
        path, _ = QFileDialog.getSaveFileName(
            parent=self,
            directory=f"{self.file_path}.lua_state"
        )
        self.save_file.lua_state.dump_to_file(path)
        self.ui_state.setText("Lua state dumped!")

    def load_lua_state_and_save(self):
        if not self.file_path:
            self.ui_state.setText("No savegame loaded!")
            return
        path, _ = QFileDialog.getOpenFileName(
            parent=self,
            directory=f"{self.file_path}.lua_state"
        )
        self.save_file.lua_state.load_from_file(path)
        self.save_file.to_file(self.file_path)
        self.dirty = False
        self.load_file(self.file_path)
        self.ui_state.setText(f"Lua state loaded from {path} and saved to {self.file_path}")

    def reset_gift_record(self):
        self.save_file.lua_state.gift_record = {}
        self.save_file.lua_state.npc_interactions = {}
        self.save_file.lua_state.trigger_record = {}
        self.save_file.lua_state.activation_record = {}
        self.save_file.lua_state.use_record = {}
        self.save_file.lua_state.text_lines = {}
        self.ui_state.setText("Reset NPC gifting status")

    def safe_quit(self):
        if self.dirty:
            qm = QMessageBox
            ret = qm.question(self, '', "You haven't saved since your last load. Really exit?", qm.Yes | qm.No)
            if ret == qm.No:
                return

        self.app.quit()

    def _get_aspect_from_trait_cache(self, trait_cache):
        for trait in trait_cache:
            if trait in gamedata.AspectTraits:
                return f"Aspect of {gamedata.AspectTraits[trait]}"
        return "Redacted"  # This is what it says in game

    def _get_weapon_from_weapons_cache(self, weapons_cache):
        for weapon_name in gamedata.HeroMeleeWeapons.keys():
            if weapon_name in weapons_cache:
                return gamedata.HeroMeleeWeapons[weapon_name]
        return "Unknown weapon"

    def export_runs_as_csv(self):
        if not self.file_path:
            self.ui_state.setText("Export failed, no savegame loaded!")
            return

        runs = self.save_file.lua_state.to_dicts()[0]["GameState"]["RunHistory"]

        csvfilename = "runs.csv"

        import csv
        with open(csvfilename, "w", newline='') as csvfile:
          run_writer = csv.writer(csvfile, dialect='excel')
          run_writer.writerow(["Attempt", "Heat", "Weapon", "Form", "Elapsed time (seconds)", "Outcome", "Godmode", "Godmode damage reduction"])

          for key, run in runs.items():
              run_writer.writerow([
                  # Attempt
                  int(key),
                  # Heat
                  run.get("ShrinePointsCache", ""),  # This seems to be heat
                  # Weapon
                  self._get_weapon_from_weapons_cache(run["WeaponsCache"]) if "WeaponsCache" in run else "",
                  # Form
                  self._get_aspect_from_trait_cache(run["TraitCache"]) if "TraitCache" in run else "",
                  # Run duration (seconds)
                  run["GameplayTime"] if "GameplayTime" in run else "",
                  # Outcome
                  "Escaped" if run.get("Cleared", False) else "",
                  # Godmode
                  "EasyModeLevel" in run,
                  # Godmode damage reduction
                  _damage_reduction_from_easy_mode_level(run["EasyModeLevel"]) if "EasyModeLevel" in run else ""
                  ])

        self.ui_state.setText(f"Exported to {csvfilename}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = App(app)

    import sys

    sys.excepthook = except_hook

    sys.exit(app.exec_())
