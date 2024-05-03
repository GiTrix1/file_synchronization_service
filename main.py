from datetime import datetime
from dotenv import load_dotenv
from time import sleep
import os
from loguru import logger
from yandex_disk_connector import YandexDiskConnector


def main():
    load_dotenv(".env")
    token = os.getenv("TOKEN")
    local_directory = os.getenv("LOCAL_DIRECTORY")
    cloud_directory = os.getenv("CLOUD_DIRECTORY")
    sync_interval = int(os.getenv("SYNC_INTERVAL"))
    log_file_path = os.getenv("LOG_FILE_PATH")

    logger.add(log_file_path, format="{message}")
    logger.info(f"synchroniser {datetime.now()} "
                "INFO Программа сихронизации файлов начинает работу "
                f"с директорией {local_directory}.")

    cloud_connector = YandexDiskConnector(
        token,
        local_directory,
        cloud_directory
    )

    while True:
        cloud_connector.cloud_files_information(cloud_connector)
        cloud_connector.file_sync_manager(cloud_connector)
        sleep(sync_interval)


if __name__ == "__main__":
    main()
