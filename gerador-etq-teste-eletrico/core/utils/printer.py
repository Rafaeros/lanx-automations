import platform
import subprocess
import tempfile
import os

try:
    import win32print
    import win32api
except ImportError:
    win32print = None
    win32api = None

class PrinterManager:
    def __init__(self):
        self.default_printer = None

    @staticmethod
    def is_windows():
        return platform.system().lower().startswith("win")

    @staticmethod
    def is_linux():
        return platform.system().lower().startswith("linux")

    def list_printers(self):
        if self.is_windows():
            return self._list_windows()
        elif self.is_linux():
            return self._list_linux()
        return []

    def _list_windows(self):
        if not win32print:
            raise RuntimeError("win32print não instalado.")
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return [p[2] for p in printers]

    def _list_linux(self):
        try:
            result = subprocess.check_output(["lpstat", "-a"], text=True)
            return [line.split()[0] for line in result.splitlines()]
        except Exception:
            return []

    def find_printer(self, name_contains: str):
        name_contains = name_contains.lower()
        for p in self.list_printers():
            if name_contains == p.lower() or name_contains in p.lower():
                return p
        return None

    def print_label(self, printer_name: str, file_path: str, quantity: int):
        real_printer = self.find_printer(printer_name)
        if not real_printer:
            raise RuntimeError(f"Impressora '{printer_name}' não encontrada no sistema.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo '{file_path}' não foi encontrado.")

        if self.is_windows():
            return self._print_pdf_windows(real_printer, file_path)
        elif self.is_linux():
            return self._print_image_linux(real_printer, file_path, quantity)

        raise RuntimeError("Sistema operacional não suportado.")

    def _print_pdf_windows(self, printer_name, pdf_path):
        if not win32api:
            raise RuntimeError("win32api não instalado.")
        try:
            win32api.ShellExecute(0, "printto", pdf_path, f'"{printer_name}"', ".", 0)
        except Exception as e:
            raise RuntimeError(f"Erro ao tentar imprimir PDF no Windows: {e}")

    def _print_image_linux(self, printer_name, img_path, quantity: int):
        try:
            subprocess.run(
                ["lp", "-d", printer_name, "-n", str(quantity), "-o", "fit-to-page", img_path], 
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erro ao imprimir imagem no Linux: {e}")