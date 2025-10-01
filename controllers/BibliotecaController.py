from PyQt6 import QtWidgets, QtCore, QtGui

from utils.Biblioteca import Biblioteca

class BibliotecaController:
    def __init__(self, ui, parent=None, verbose: bool = True):
        self.ui = ui
        self.parent = parent or ui
        self.verbose = verbose

        self.biblioteca = Biblioteca()
        self.model = QtGui.QStandardItemModel()

        self.ui.listViewBiblioteca.setModel(self.model)
        self.ui.pushButtonAgregarBiblioteca.clicked.connect(self.on_add_library)

    def on_add_library(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.parent, "Seleccionar carpeta de música")
        if not folder:
            return
        count = self.biblioteca.cargar_desde_carpeta(folder, recursive=True, verbose=self.verbose)
        self._update_view()
        if self.verbose:
            print(f"{count} canciones cargadas.")

    def populate_from_folder(self, folder_path: str):
        count = self.biblioteca.cargar_desde_carpeta(folder_path, recursive=True, verbose=self.verbose)
        self._update_view()
        return count

    def _update_view(self):
        self.model.clear()
        for key, song in self.biblioteca.songs.items():
            title = getattr(song, "title", "") or ""
            artist = getattr(song, "artist", "") or ""
            if title or artist:
                text = f"{title} - {artist}".strip(" -")
            else:
                text = getattr(song, "file_path", "<sin ruta>")
            item = QtGui.QStandardItem(text)
            item.setData(key, QtCore.Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)

    def get_selected_song(self):
        sel = self.ui.listViewBiblioteca.selectedIndexes()
        if not sel:
            return None
        idx = sel[0]
        key = idx.data(QtCore.Qt.ItemDataRole.UserRole)
        return self.biblioteca.songs.get(key)