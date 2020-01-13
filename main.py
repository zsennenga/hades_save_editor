import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QPushButton, QLineEdit, QMessageBox, QDialog, QLabel

from models.save_file import HadesSaveFile


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class App(QDialog):
    def __init__(self, application):
        super().__init__()
        self.app = application

        self.file_path = None
        self.save_file: HadesSaveFile = None
        self.dirty = False

        uic.loadUi(resource_path('pluto.ui'), self)  # Load the .ui file
        self.load_button = self.findChild(QPushButton, "load")
        self.load_button.clicked.connect(self.open_file_name_dialog)

        self.save_button = self.findChild(QPushButton, "save")
        self.save_button.clicked.connect(self.write_file)

        self.exit_button = self.findChild(QPushButton, "exit")
        self.exit_button.clicked.connect(self.safe_quit)

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

        self.show()  # Show the GUI

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;Hades Save Files (*.sav)",
            options=options
        )
        self.file_path = fileName
        self.save_file = HadesSaveFile.from_file(self.file_path)

        self.path_label.setText(fileName)
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

        self.dirty = True

    def write_file(self):
        self.save_file.lua_state.darkness = float(self.darkness_field.text())
        self.save_file.lua_state.gems = float(self.gems_field.text())
        self.save_file.lua_state.diamonds = float(self.diamonds_field.text())
        self.save_file.lua_state.nectar = float(self.nectar_field.text())
        self.save_file.lua_state.ambrosia = float(self.ambrosia_field.text())
        self.save_file.lua_state.chthonic_key = float(self.keys_field.text())
        self.save_file.lua_state.titan_blood = float(self.titan_blood_field.text())

        self.save_file.to_file(self.file_path)
        self.dirty = False

    def safe_quit(self):
        if self.dirty:
            qm = QMessageBox
            ret = qm.question(self, '', "You haven't saved since your last load. Really exit?", qm.Yes | qm.No)
            if ret == qm.No:
                return

        self.app.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = App(app)
    sys.exit(app.exec_())
