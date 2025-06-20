import subprocess
import time
import sys
import datetime
import traceback

LOG_FILE = "bot_restarter.log"
BOT_FILENAME = "main.py"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def run_bot():
    restart_count = 0
    while True:
        try:
            log(f"Запуск бота (попытка {restart_count + 1})")
            process = subprocess.Popen([sys.executable, BOT_FILENAME])
            process.wait()
        except KeyboardInterrupt:
            log("Остановка по запросу пользователя")
            break
        except Exception as e:
            log(f"Критическая ошибка: {str(e)}\n{traceback.format_exc()}")
        finally:
            restart_count += 1
            log(f"Бот завершил работу. Перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    log("Скрипт перезапуска бота запущен")
    try:
        run_bot()
    except Exception as e:
        log(f"Фатальная ошибка в скрипте перезапуска: {str(e)}")
    finally:
        log("Скрипт перезапуска бота остановлен")
