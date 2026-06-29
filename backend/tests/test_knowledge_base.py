import asyncio
from types import SimpleNamespace

import httpx

from app.knowledge_base import (
    KnowledgeBaseClient,
    _extract_response_error,
    _is_completed_temp_lock_error,
    _normalize_document,
)
from app.schemas import KnowledgeBaseDocument


def test_normalize_document_uses_stored_filename_as_file_id():
    document = _normalize_document(
        {
            "filename": "b9b14829a873491c932b896b25072122.json",
            "original_filename": "产品介绍.docx",
            "timestamp": "2026-06-29T16:30:08.664770",
        }
    )

    assert document is not None
    assert document.id == "b9b14829a873491c932b896b25072122"
    assert document.name == "产品介绍.docx"
    assert document.uploadedAt > 0


def test_normalize_document_uses_file_path_when_filename_is_missing():
    document = _normalize_document(
        {
            "file_path": "data\\parsed\\cec1d71964ea40a98b9bb12c3b2f40f1.json",
            "original_filename": "FAQ知识整理.md",
        }
    )

    assert document is not None
    assert document.id == "cec1d71964ea40a98b9bb12c3b2f40f1"
    assert document.name == "FAQ知识整理.md"


def test_resolve_document_id_accepts_display_name(monkeypatch):
    client = KnowledgeBaseClient(
        SimpleNamespace(
            knowledge_base_url="http://kb.example",
            knowledge_base_timeout_seconds=30,
        )
    )

    async def fake_list_documents(collection_name):
        assert collection_name == "test"
        return [
            KnowledgeBaseDocument(
                id="b9b14829a873491c932b896b25072122",
                name="产品介绍.docx",
                size=0,
                uploadedAt=0,
            )
        ]

    monkeypatch.setattr(client, "list_documents", fake_list_documents)

    assert asyncio.run(client.resolve_document_id("test", "产品介绍.docx")) == "b9b14829a873491c932b896b25072122"
    assert (
        asyncio.run(client.resolve_document_id("test", "b9b14829a873491c932b896b25072122.json"))
        == "b9b14829a873491c932b896b25072122"
    )


def test_completed_temp_lock_error_is_recoverable():
    response = httpx.Response(
        500,
        json={
            "message": "[WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'temp\\\\李健波-工作周报.xlsx'",
            "process_log": [
                {"step": 1, "name": "文件解析", "status": "completed"},
                {"step": 2, "name": "文本分块", "status": "completed"},
                {"step": 3, "name": "向量化", "status": "completed"},
                {"step": 4, "name": "知识图谱提取", "status": "completed"},
            ],
        },
    )

    assert _is_completed_temp_lock_error(response)
    assert _extract_response_error(response).startswith("[WinError 32]")


def test_incomplete_temp_lock_error_is_not_recoverable():
    response = httpx.Response(
        500,
        json={
            "message": "[WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'temp\\\\李健波-工作周报.xlsx'",
            "process_log": [
                {"step": 1, "name": "文件解析", "status": "completed"},
                {"step": 2, "name": "文本分块", "status": "failed"},
            ],
        },
    )

    assert not _is_completed_temp_lock_error(response)
