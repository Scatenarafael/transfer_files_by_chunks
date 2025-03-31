import logging
import os

# import threading
import time

from core.tasks import merge_chunks_task, save_chunk
from django.conf import settings
from django.core.files.storage import default_storage

# from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("conections_logger")


class AsyncChunkedFileUploadView(APIView):
    # async def save_chunk(self, file_content, file_path):
    #     """Salva o chunk de forma assíncrona"""
    #     try:
    #         logger.debug(f"Salvando chunk: {file_path}")

    #         async with aiofiles.open(file_path, "wb") as f:
    #             await f.write(file_content)

    #     except FileNotFoundError:
    #         logger.error(f"Arquivo não encontrado: {file_path}")
    #         raise
    #     except PermissionError:
    #         logger.error(f"Permissão negada ao salvar o arquivo: {file_path}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"Erro inesperado ao salvar o chunk: {e}")
    #         raise

    def post(self, request):
        """Recebe o chunk e delega a tarefa ao Celery"""
        file = request.FILES.get("file")
        chunk_number = int(request.data.get("chunk_number", 0))
        total_chunks = int(request.data.get("total_chunks", 1))
        file_name = request.data.get("file_name")
        file_path = f"uploads/{file_name}.part{chunk_number}"

        if not file:
            return Response({"error": "Nenhum arquivo enviado"}, status=400)

        # ✅ Ler o conteúdo antes de enviar para Celery (pois FILES é um stream)
        file_content = file.read()

        # ✅ Enviar a tarefa para Celery (worker processa em background)
        save_chunk.delay(file_content, file_path, chunk_number, total_chunks)

        if chunk_number == total_chunks - 1:
            logger.debug(f"Ultimo chunk recebido: {chunk_number}")
            time.sleep(1)  # Aguarda o processamento do último chunk
            # Chama a tarefa de merge_chunks_task
            merge_chunks_task.delay(file_name, total_chunks)

        return Response(
            {"message": f"Chunk {chunk_number} enviado para processamento"},
            status=200,
        )

    # def put(self, request):
    #     """Finaliza o upload chamando Celery para juntar os chunks"""
    #     file_name = request.data.get("file_name")
    #     total_chunks = int(request.data.get("total_chunks", 1))

    #     logger.debug(f"Beginnning to merge chunks of {file_name}...")
    #     logger.debug(f"Total chunks {total_chunks}...")

    #     # Dispara a tarefa assíncrona
    #     thread = threading.Thread(
    #         target=merge_chunks_task,
    #         args=(file_name, total_chunks),
    #     )
    #     thread.start()
    #     # merge_chunks_task(file_name, total_chunks)

    #     return Response(
    #         {"message": "Upload em processamento"},
    #         status=status.HTTP_202_ACCEPTED,
    #     )


def save_file(file_content, file_path):
    """Salva o chunk de forma assíncrona em segundo plano."""
    logger.debug(f"Standard Upload - Salvando arquivo: {file_path}")
    try:

        with default_storage.open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return {"error": str(e)}
    return {"message": f"Chunk salvo em {file_path}"}


class AsyncFileUploadView(APIView):
    def post(self, request):
        """Recebe o chunk e delega a tarefa ao Celery"""
        file = request.FILES.get("file")
        file_name = request.data.get("file_name")

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads/standard")
        file_path = os.path.join(upload_dir, file_name)

        # Garante que a pasta 'uploads/' existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        logger.debug(f"Standard Upload - file_path: {file_path}")
        logger.debug(f"Standard Upload - file_name: {file_name}")

        if not file:
            return Response({"error": "Nenhum arquivo enviado"}, status=400)

        # ✅ Ler o conteúdo antes de enviar para Celery (pois FILES é um stream)
        file_content = file.read()
        file_size = len(
            file_content
        )  # Identifica o tamanho do conteúdo do arquivo
        logger.debug(
            f"Standard Upload - Tamanho do arquivo recebido: {file_size} bytes"
        )

        # ✅ Enviar a tarefa para Celery (worker processa em background)
        save_file(file_content, file_path)

        return Response(
            {"message": "Arquivo recebido com sucesso"},
            status=200,
        )
