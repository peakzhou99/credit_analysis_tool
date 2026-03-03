# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import uuid
from datetime import datetime
from protos import credit_analysis_tool_pb2, credit_analysis_tool_pb2_grpc
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ReportGeneratorService(credit_analysis_tool_pb2_grpc.ReportGeneratorServicer):
    """报告生成服务"""

    def __init__(self):
        self.report_generator = ReportGenerator(max_workers=5)

    def gen_credit_analysis_tool(self, request, context):
        """
        报告生成接口
        """
        report_id = request.reportId
        company_name = request.companyName
        html_sdoss_id = request.htmlSdossId
        creat_user = request.creatUser
        req_files = [{"fileName": f.fileName, "fileUrl": f.fileUrl} for f in request.reqFiles]

        logger.info(
            f"【{report_id}】接收请求 | 公司: {company_name} | "
            f"发起人: {creat_user} | 附件数: {len(req_files)}"
        )

        # 生成UUID作为流水号
        str_uuid = str(uuid.uuid4())

        # 构造固定公共报文数据
        fixed_data = {
            "tranCode": "aihelper@aiReportCallback",
            "chanId": "llm",
            "sysId": "llm",
            "pubGloblJnno": request.pubGloblJnno,
            "seriNo": request.seriNo,
            "reqBizDate": datetime.now().strftime("%Y-%m-%d"),
            "tranCounter": "system",
            "orgNo": "00001",
            "protocol": "http",
            "preReverseFlag": "0",
            "legalCode": "9999",
            "headVerNo": "1.0.0",
            "preSysId": "llm",
            "preSerialNo": str_uuid,
            "preReqVerNo": "1.0.0",
            "preSubFlag": "0",
            "reportId": report_id,
        }

        try:
            # 调用生成器处理
            result = self.report_generator.generate_report(
                report_id=report_id,
                company_name=company_name,
                html_sdoss_id=html_sdoss_id,
                creat_user=creat_user,
                req_files=req_files,
            )

            # 构造动态数据
            dynamic_data = {
                "dealSts": "1",
                "dealRemark": result["dealRemark"],
                "reportFiles": [
                    credit_analysis_tool_pb2.ReportFile(
                        fileName=f["fileName"],
                        sdossId=f["sdossId"],
                    )
                    for f in result["reportFiles"]
                ],
            }

            response = credit_analysis_tool_pb2.GenReply(**{**fixed_data, **dynamic_data})
            logger.info(f"【{report_id}】返回成功 | 文件数: {len(result['reportFiles'])}")
            return response

        except Exception as e:
            logger.error(f"【{report_id}】处理失败 | 错误: {str(e)}", exc_info=True)

            dynamic_data = {
                "dealSts": "3",
                "dealRemark": f"报告生成失败: {str(e)}",
                "reportFiles": [],
            }

            response = credit_analysis_tool_pb2.GenReply(**{**fixed_data, **dynamic_data})
            return response