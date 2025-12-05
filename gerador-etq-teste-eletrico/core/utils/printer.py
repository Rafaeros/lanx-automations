import platform
import subprocess
import tempfile
import os

# Windows-only
try:
    import win32print # type: ignore
except:
    win32print = None


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

        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
        return [p[2] for p in printers]

    def _list_linux(self):
        try:
            result = subprocess.check_output(["lpstat", "-a"], text=True)
            return [line.split()[0] for line in result.splitlines()]
        except:
            return []

    def find_printer(self, name_contains: str):
        name_contains = name_contains.lower()
        for p in self.list_printers():
            if name_contains in p.lower():
                return p
        return None

    def print_text(self, printer_name: str, text: str):
        real_printer = self.find_printer(printer_name)
        if not real_printer:
            raise RuntimeError(
                f"Impressora '{printer_name}' não encontrada no sistema."
            )

        if self.is_windows():
            return self._print_windows(real_printer, text)
        elif self.is_linux():
            return self._print_linux(real_printer, text)

        raise RuntimeError("Sistema operacional não suportado.")

    def _print_windows(self, printer_name, text):
        handle = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(
                handle, 1, ("Python Print Job", None, "RAW")
            )
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, text.encode("utf-8"))
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
        finally:
            win32print.ClosePrinter(handle)
        return True

    def _print_linux(self, printer_name, text):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(text.encode("utf-8"))
        tmp.close()

        try:
            subprocess.run(["lp", "-d", printer_name, tmp.name], check=True)
        finally:
            os.unlink(tmp.name)

        return True


if __name__ == "__main__":
    pm = PrinterManager()
    print(pm.list_printers())
    printer_name = pm.find_printer("ZTC")
    print(pm.print_text(printer_name, "Teste"))
