from db.mongo import db
from models import ReportMessageModel
from typing import List
from models import PyObjectId

class ReportMessagesRepository:
    def __init__(self):
        self.reports = db['report_messages']

    async def find_one_by_id(self, id: str) -> ReportMessageModel | None:
        report = await self.reports.find_one({"_id": PyObjectId(id)})
        if report:
            return ReportMessageModel(**report)
        return None
    
    async def delete_one_by_id(self, id: str):
        await self.reports.delete_one({"_id": PyObjectId(id)})
        return None
    
    async def find_all_by_user_id(self, user_id: PyObjectId) -> List[ReportMessageModel]:
        data_list = await self.reports.find({"user_id": user_id}).to_list(length=None)

        reports = [
            ReportMessageModel(**{**data})
            for data in data_list
        ]
        return reports
    
    async def find_all(self) -> List[ReportMessageModel]:
        data_list = await self.reports.find().to_list(length=None)

        reports = [
            ReportMessageModel(**{**data})
            for data in data_list
        ]
        return reports

    async def store(self, report: ReportMessageModel) -> ReportMessageModel:
        report = await self.reports.insert_one(report.dict(by_alias=True))
        return report