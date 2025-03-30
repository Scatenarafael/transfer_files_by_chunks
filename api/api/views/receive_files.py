import asyncio
import logging
import os
import threading

import aiofiles
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.tasks import merge_chunks_task

logger = logging.getLogger("conections_logger")


class AsyncChunkedFileUploadView(APIView):
    async def save_chunk(self, file_content, file_path):
        """Salva o chunk de forma assíncrona"""
        try:
            logger.debug(f"Salvando chunk: {file_path}")

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_content)

        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {file_path}")
            raise
        except PermissionError:
            logger.error(f"Permissão negada ao salvar o arquivo: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar o chunk: {e}")
            raise

    def post(self, request):
        file = request.FILES.get("file")
        """Junta os chunks sequencialmente"""

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")

        # Garante que a pasta 'uploads/' existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        chunk_number = int(request.data.get("chunk_number", 0))
        file_name = request.data.get("file_name")
        file_path = f"{upload_dir}/{file_name}.part{chunk_number}"

        if not file:
            return Response({"error": "Nenhum arquivo enviado"}, status=400)

        # ✅ Ler o conteúdo do arquivo ANTES de passar para a thread
        file_content = file.read()

        def run_async():
            loop = (
                asyncio.new_event_loop()
            )  # ✅ Criar um novo loop de eventos na thread
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.save_chunk(file_content, file_path))
            loop.close()

        thread = threading.Thread(target=run_async)
        thread.start()

        return Response(
            {"message": f"Chunk {chunk_number} recebido"}, status=200
        )

    def put(self, request):
        """Finaliza o upload chamando Celery para juntar os chunks"""
        file_name = request.data.get("file_name")
        total_chunks = int(request.data.get("total_chunks", 1))

        logger.debug(f"Beginnning to merge chunks of {file_name}...")
        logger.debug(f"Total chunks {total_chunks}...")

        # Dispara a tarefa assíncrona
        thread = threading.Thread(
            target=merge_chunks_task,
            args=(file_name, total_chunks),
        )
        thread.start()
        # merge_chunks_task(file_name, total_chunks)

        return Response(
            {"message": "Upload em processamento"},
            status=status.HTTP_202_ACCEPTED,
        )
