from supabase import create_client, Client
from fastapi import UploadFile, HTTPException, status
from typing import Optional
import uuid
from pathlib import Path

from src.core.config import settings


class StorageService:
    """Service para gerenciar uploads de arquivos no Supabase Storage"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
    
    async def upload_image(
        self, 
        file: UploadFile, 
        folder: str = "ingredients"
    ) -> str:
        """
        Faz upload de uma imagem para o Supabase Storage
        
        Args:
            file: Arquivo enviado pelo usuário
            folder: Pasta dentro do bucket (default: ingredients)
            
        Returns:
            str: Nome do arquivo salvo no storage
            
        Raises:
            HTTPException: Se houver erro no upload
        """
        # Validar tipo de arquivo
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic", "image/heif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não permitido. Use: {', '.join(allowed_types)}"
            )
        
        # Validar tamanho (máximo 5MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo muito grande. Tamanho máximo: 5MB"
            )
        
        # Resetar o ponteiro do arquivo
        await file.seek(0)
        
        # Gerar nome único para o arquivo
        file_extension = Path(file.filename).suffix
        unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"
        
        try:
            # Upload para o Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )
            
            return unique_filename
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao fazer upload da imagem: {str(e)}"
            )
    
    def get_public_url(self, file_path: str) -> str:
        """
        Gera a URL pública de um arquivo no Supabase Storage
        
        Args:
            file_path: Caminho do arquivo no storage
            
        Returns:
            str: URL pública do arquivo
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao gerar URL pública: {str(e)}"
            )
    
    async def delete_image(self, file_path: str) -> bool:
        """
        Remove uma imagem do Supabase Storage
        
        Args:
            file_path: Caminho do arquivo no storage
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            print(f"Erro ao deletar imagem: {str(e)}")
            return False
