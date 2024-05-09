import logging
import sys
import os
from constants import LOGS_PATH
from datetime import datetime
import shutil

class Logger:
    """
    Clase para gestionar el registro de eventos.

    Attributes:
    - loggerName (str): Nombre del logger.
    - filename (str): Ruta del archivo de registro.
    - logger (logging.Logger): Objeto Logger de la biblioteca estándar de Python.
    """
    def __init__(self, loggerName, printConsole=False, clean=False):
        """
        Inicializa un objeto Logger.

        Parámetros:
        - loggerName (str): Nombre del logger.
        - printConsole (bool): Indica si se debe imprimir en la consola (por defecto False).
        - clean (bool): Indica si se deben limpiar los registros existentes (por defecto False).
        """
        if clean:
            self.clean_logs()
        self.loggerName = loggerName
        self.filename = LOGS_PATH + self.loggerName + ".log"
        self.logger = logging.getLogger(self.filename)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Configurar el manejador de archivos para escribir en el archivo de registro
        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

        # Configurar el manejador de consola para imprimir en la consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        if printConsole:
            console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def error(self, message):
        """
        Registra un mensaje de error.

        Parámetros:
        - message (str): Mensaje de error.
        """
        self.logger.error(message)

    def warning(self, message):
        """
        Registra un mensaje de advertencia.

        Parámetros:
        - message (str): Mensaje de advertencia.
        """
        self.logger.warning(message)

    def info(self, message):
        """
        Registra un mensaje informativo.

        Parámetros:
        - message (str): Mensaje informativo.
        """
        self.logger.info(message)
    
    def clean_logs(self):
        """
        Limpia los registros existentes.
        """
        shutil.rmtree(LOGS_PATH)
        os.mkdir(LOGS_PATH)

    def close(self):
        """
        Cierra el Logger.
        """
        # Limpiar los manejadores de registro
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

# Ejemplo de uso:
if __name__ == "__main__":
    # Crear un objeto Logger para un archivo específico
    logger = Logger("process-1")

    # Ejemplo de registro de mensajes con diferentes niveles de urgencia
    logger.error("Esto es un mensaje de error")
    logger.warning("Esto es un mensaje de advertencia")
    logger.info("Esto es un mensaje informativo")

    # Cerrar el Logger al finalizar
    logger.close()
