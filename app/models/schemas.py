from pydantic import BaseModel, IPvAnyAddress
from typing import List, Optional
from datetime import datetime

class IPEntry(BaseModel):
  ip: IPvAnyAddress
  source: str
  added_at: datetime = datetime.now()
  reason: Optional[str] = None
  comment: Optional[str] = None

class BulkImportRequest(BaseModel):
  ips: List[str]
  source: str
  comment: Optional[str] = None

class ExportFilter(BaseModel):
  source: Optional[str] = None
  from_date: Optional[datetime] = None
  to_date: Optional[datetime] = None