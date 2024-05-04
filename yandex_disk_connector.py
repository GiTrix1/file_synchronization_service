import os
import time
from datetime import datetime
import requests
from loguru import logger


class YandexDiskConnector:
    def __init__(self, token, local_directory, cloud_directory):
        self.token = token
        self.local_directory = local_directory
        self.cloud_directory = cloud_directory
        self.url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.headers = {"Authorization": f"OAuth {self.token}"}
        self.list_file_modification_time = {}

    def update_time(self, root, file):
        try:
            self.list_file_modification_time[file] = datetime.fromtimestamp(
                os.path.getmtime(f"{root}/{file}")).strftime("%d-%m-%Y %H:%M:%S")
            return self.list_file_modification_time
        except FileNotFoundError:
            logger.error(f"synchroniser {datetime.now()} "
                         f"ERROR Папка по пути {self.local_directory}"
                         " не найдена, создайте её и попробуйте снова.")

    def sync_file(self, file_name, not_updated):
        try:
            res_get = requests.get(
                f"{self.url}/upload?path={self.cloud_directory}/{file_name}"
                "&overwrite=true", headers=self.headers
            ).json()
            with open(fr"{self.local_directory}/{file_name}", "rb") as f:
                requests.put(res_get["href"], files={"file": f})
                if not_updated:
                    logger.info(f"synchroniser {datetime.now()} "
                                f"INFO Файл {file_name} успешно записан.")
                else:
                    logger.info(f"synchroniser {datetime.now()} INFO Файл"
                                f" {file_name} успешно перезаписан.")
        except FileNotFoundError:
            logger.error(f"synchroniser {datetime.now()} "
                         f"ERROR Папка по пути {self.local_directory}"
                         " не найдена, создайте её и попробуйте снова.")
        except requests.exceptions.ConnectionError:
            logger.error(f"synchroniser {datetime.now()} "
                         "ERROR Не удалось удалить файл. "
                         "Ошибка соединения.")

    def delete_file(self, file_name):
        try:
            requests.delete(f"{self.url}?path={self.cloud_directory}/{file_name}",
                            headers=self.headers)
            logger.info(f"synchroniser {datetime.now()} "
                        f"INFO Файл {file_name} успешно удален.")
        except requests.exceptions.ConnectionError:
            logger.error(f"synchroniser {datetime.now()} "
                         "ERROR Не удалось удалить файл. "
                         "Ошибка соединения.")

    def cloud_files_information(self, connector):
        try:
            list_files = []
            req = requests.get(f"{self.url}?path=Backup",
                               headers=self.headers).json()
            files = req["_embedded"]["items"]
            for file in files:
                list_files.append(file["name"])
            return list_files
        except requests.exceptions.ConnectionError:
            logger.error(f"synchroniser {datetime.now()} "
                         "ERROR Невозможно получить информацию о файле. "
                         "Ошибка соединения.")
            time.sleep(10)
            connector.cloud_files_information(connector)

    def file_sync_manager(self, connector):
        cloud_files = connector.cloud_files_information(connector)
        if not cloud_files:
            logger.info(f"Создайте папку так, чтобы путь выглядел идентично этому: {self.local_directory}")
        for root, dirs, files in os.walk("F:/Backup"):
            for file in files:
                cloud_time_file = self.list_file_modification_time.get(file)
                local_time_file = datetime.fromtimestamp(os.path.getmtime(
                    f"{root}/{file}")).strftime("%d-%m-%Y %H:%M:%S")
                if file not in cloud_files:
                    connector.sync_file(file, not_updated=True)
                    connector.update_time(root, file)
                elif (cloud_time_file != local_time_file and
                      cloud_time_file is not None):
                    connector.update_time(root, file)
                    connector.sync_file(file, not_updated=False)
            for cloud_file in cloud_files:
                if cloud_file not in files:
                    connector.delete_file(cloud_file)
