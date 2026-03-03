#!/usr/bin/env python
# -*- coding:utf-8 -*-
import io
import os
from datetime import datetime
from typing import List, Dict
from threading import Lock

from docx import Document

from report_generator.oss_client import S3Client
from utils.logger_util import get_logger

logger = get_logger()

S3_REPORT_PREFIX = "credit_analysis_reports"


class ReportGenerator:

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.log_lock = Lock()
        logger.info(f"ReportGenerator 初始化完成 | 最大线程数: {self.max_workers}")

    def generate_report(
        self,
        report_id: str,
        company_name: str,
        html_sdoss_id: str,
        creat_user: str,
        req_files: List[Dict],
        skip_upload: bool = False,
    ) -> Dict:
        logger.info(f"【{report_id}】开始生成报告 | 公司: {company_name}")

        docx_bytes = self._build_word_report(
            report_id=report_id,
            company_name=company_name,
            html_sdoss_id=html_sdoss_id,
            creat_user=creat_user,
            req_files=req_files,
        )

        file_name = f"{report_id}.docx"

        sdoss_id = self._upload(
            docx_bytes=docx_bytes,
            file_name=file_name,
            report_id=report_id,
            skip_upload=skip_upload,
        )

        logger.info(f"【{report_id}】报告完成 | 文件: {file_name} | sdossId: {sdoss_id}")

        return {
            "dealRemark": "报告生成成功",
            "reportFiles": [
                {
                    "fileName": file_name,
                    "sdossId": sdoss_id,
                }
            ],
        }

    def _build_word_report(
        self,
        report_id: str,
        company_name: str,
        html_sdoss_id: str,
        creat_user: str,
        req_files: List[Dict],
    ) -> bytes:
        doc = Document()

        def add(text: str):
            doc.add_paragraph(text)

        add(f"公司名称：{company_name}")
        add(f"报告ID：{report_id}")
        add(f"征信报告地址：{html_sdoss_id or '—'}")
        add(f"发起用户：{creat_user}")
        add(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        add("")
        add("请求附件：")
        if req_files:
            for i, f in enumerate(req_files, 1):
                add(f"  {i}. 文件名：{f.get('fileName', '')}  地址：{f.get('fileUrl', '')}")
        else:
            add("  （无附件）")

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf.getvalue()

    def _upload(
        self,
        docx_bytes: bytes,
        file_name: str,
        report_id: str,
        skip_upload: bool,
    ) -> str:
        if skip_upload:
            local_dir = os.path.join("data", "result", report_id)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, file_name)
            with open(local_path, "wb") as f:
                f.write(docx_bytes)
            logger.info(f"【{report_id}】本地保存: {local_path}")
            return local_path

        object_key = f"{S3_REPORT_PREFIX}/{report_id}/{file_name}"
        logger.info(f"【{report_id}】上传 S3: {object_key}")
        sdoss_id = S3Client.upload_bytes(docx_bytes, object_key)
        return sdoss_id


if __name__ == "__main__":
    gen = ReportGenerator(max_workers=5)
    result = gen.generate_report(
        report_id="test_001",
        company_name="测试科技股份有限公司",
        html_sdoss_id="ciis/test_credit.html",
        creat_user="25020156",
        req_files=[
            {"fileName": "财务报告.pdf", "fileUrl": "http://example.com/finance.pdf"},
            {"fileName": "审计报告.pdf", "fileUrl": "http://example.com/audit.pdf"},
        ],
        skip_upload=True,
    )
    print(f"dealRemark : {result['dealRemark']}")
    print(f"reportFiles: {result['reportFiles']}")