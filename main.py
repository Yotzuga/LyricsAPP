from PyQt6 import QtWidgets, uic
import sys
import os
from controllers.BibliotecaController import BibliotecaController 
from controllers.LyricsController import LyricsController        
from controllers.ImportContoller import ImportContoller         
from controllers.PlayerController import PlayerController
from controllers.TimesController import TimesController

def resource_path(*paths: str) -> str:
    """Devuelve la ruta de un recurso compatible con PyInstaller (onefile) y modo normal."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))  # type: ignore[attr-defined]
    return os.path.join(base, *paths)


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        ui_file = resource_path("gui", "LyricsGUI.ui")
        self.ui = uic.loadUi(ui_file, self)  # type: ignore

       # Fija los anchos que quieres
        self.ui.tableWidgetLyrics.setColumnWidth(0, 85)    # type: ignore
        self.ui.tableWidgetLyrics.setColumnWidth(1, 528)    # type: ignore 

        self.biblioteca_controller = BibliotecaController(self.ui, parent=self)
   
        self.player_controller = PlayerController(self.ui, self.biblioteca_controller)
    
        self.lyrics_controller = LyricsController(self.ui, self.biblioteca_controller, player_controller=self.player_controller)
        
        self.times_controller = TimesController(self.ui, player_controller=self.player_controller)
        
        try:
            setattr(self.player_controller, 'times_controller', self.times_controller)
        except Exception:
            pass
         
        self.import_controller = ImportContoller(self.ui, parent=self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())