import logging
import sqlite3
import traceback
import datetime
from colorama import Fore, Style, init

# Inicializa o colorama para compatibilidade no Windows
init(autoreset=True)

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path="logs.db"):
        super().__init__()
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                email TEXT,
                file_name TEXT,
                line_number INTEGER,
                application_name TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def emit(self, record):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            log_time = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO logs (
                    timestamp, 
                    level, 
                    message, 
                    email, 
                    file_name, 
                    line_number, 
                    application_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_time,
                record.levelname,
                record.getMessage(),
                getattr(record, 'email', None),
                record.pathname,
                record.lineno,
                getattr(record, 'application_name', None)
            ))
            conn.commit()
            conn.close()
        except Exception:
            print("Erro ao salvar log no banco de dados:", traceback.format_exc())

# Classe para colorir logs no console
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        formatted_message = super().format(record)
        return f"{log_color}{formatted_message}{Style.RESET_ALL}"

# Configuração do logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Remove handlers existentes (se houver)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Configuração do formato do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o SQLiteHandler
sqlite_handler = SQLiteHandler()
sqlite_handler.setFormatter(formatter)
logger.addHandler(sqlite_handler)

# Adiciona um handler para exibir logs no console com cores
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Testando os logs coloridos
logger.debug("Este é um log de debug")
logger.info("Este é um log de informação")
logger.warning("Este é um log de aviso")
logger.error("Este é um log de erro")
logger.critical("Este é um log crítico")
