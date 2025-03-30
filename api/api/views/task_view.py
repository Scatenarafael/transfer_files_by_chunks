import logging
import os
import time

from celery import chain
from celery.result import AsyncResult
from rest_framework import response, status
from rest_framework.views import APIView

# from core.settings import BASE_DIR
from core.tasks import move_files, send_email

logger = logging.getLogger("conections_logger")

# Create your views here.

EMAIL_DEMAND_IDS = [1, 2, 3, 4, 5]


def start_email_queue():
    task_email = []

    for task in EMAIL_DEMAND_IDS:
        task_id = send_email.delay(f"user_{task}@email.com")
        task_email.append(task_id.id)

    for task_id in task_email:
        email_result: AsyncResult | None = AsyncResult(task_id)

        while email_result.status != "SUCCESS":
            print(f"Aguardando envio do e-mail na task: {task_id}...")
            time.sleep(1)
        if email_result.status == "SUCCESS":
            print(f"E-mail da task {task_id} enviado com sucesso!")
        email_result = None


def get_filenames_by_dir(directory_path):
    try:
        filenames = os.listdir(directory_path)
        logger.debug(f"Files found: {filenames}")
        tasks = [move_files.si(file, directory_path) for file in filenames]
        task_chain = chain(*tasks)

        task_chain.apply_async()
        # [
        #     move_files.apply_async(args=(file, directory_path))
        #     for file in filenames
        #     if os.path.isfile(os.path.join(directory_path, file))
        # ]
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory_path}")
        return []
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []


class TaskView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def get(self, request, format=None):
        # Chamando as tarefas assíncronas
        logger.debug("GET TaskView")

        # get_filenames_by_dir(f"{BASE_DIR}/dados")
        # start_task()
        # start_email_queue()
        return response.Response(
            {"msg": "Helloworld"}, status=status.HTTP_200_OK
        )
