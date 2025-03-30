import logging
import os
import time

from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage

# from core.settings import BASE_DIR

# from .celery import app

logger = logging.getLogger("conections_logger")


@shared_task(name="core.add")  # Defina um nome explícito
def add(x, y):
    logger.debug("Adding...")
    return x + y


@shared_task(name="core.write")  # Defina um nome explícito
def write():
    logger.debug("Adding...")
    return "Helloworld"


@shared_task(queue="emails", name="core.send_email")
def send_email(email):
    logger.debug("Sending email...")
    """Simula o envio de um e-mail."""
    print(f"📨 Enviando e-mail para {email}...")
    time.sleep(2)  # Simula o tempo de envio do e-mail
    return f"E-mail enviado para {email}!"


@shared_task(queue="files", name="core.move_files")
def move_files(filename, dir):
    logger.info(f"Moving file... {dir}, {filename}")
    time.sleep(20)
    # try:
    #     with open(f"{dir}/{filename}", "r", encoding="latin1") as file:
    #         file_content = file.read()
    #     logger.info(f"File {filename} successfully read!")
    # except FileNotFoundError:
    #     logger.error(f"File not found: {dir}/{filename}")
    #     return "File not found!"
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")
    #     return "An error occurred!"
    # try:
    #     logger.info(f"Moving {filename} to {BASE_DIR}/destination...")
    #     with open(f"{BASE_DIR}/destination/{filename}", "w") as file:
    #         file.write(file_content)
    # except FileNotFoundError:
    #     logger.error(f"Directory not found: {BASE_DIR}/destination")
    #     return "Directory not found!"
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")
    # logger.info(f"File {filename} successfully moved!")
    # return "File moved!"


def merge_chunk(chunk_index, file_name):
    """Lê e retorna um chunk do disco"""
    chunk_path = f"uploads/{file_name}.part{chunk_index}"

    if not default_storage.exists(chunk_path):
        logger.error(f"Chunk not found: {chunk_path}")
        return None  # Retorna None para evitar erros no merge

    try:
        with default_storage.open(chunk_path, "rb") as chunk_file:
            data = chunk_file.read()
        default_storage.delete(chunk_path)  # Remove o chunk após leitura
        return data
    except Exception as e:
        logger.error(f"Erro ao processar chunk {chunk_index}: {e}")
        return None


def merge_chunks_task(file_name, total_chunks):
    """Junta os chunks sequencialmente"""
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    final_file_path = os.path.join(upload_dir, file_name)

    # Garante que a pasta 'uploads/' existe
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    logger.debug("Montando arquivo...")

    try:
        with default_storage.open(final_file_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_data = merge_chunk(i, file_name)

                if chunk_data is None:
                    logger.error(
                        f"Erro ao ler chunk {i}. Processo interrompido."
                    )
                    return f"Erro ao ler chunk {i}. Processo interrompido."

                final_file.write(chunk_data)
        logger.debug("Arquivo montado com sucesso...")

    except Exception as e:
        logger.error(f"Erro inesperado ao montar o arquivo: {e}")
        return f"Erro inesperado ao montar o arquivo: {e}"

    return f"Arquivo {file_name} montado com sucesso!"
