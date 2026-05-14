

from db.database import selectFromDB
from utils.helpers import isEarlierThan, getDateTime
class PartFilter():
    def __init__(self):
        self.filterVariables = {"UPLOAD TIME": "upload_date", 
        "START TIME": "start_date", "END TIME": "end_date", "VIRGIN PARTS":"0", 
        "CURRENT PARTS":"1", "TERMINATED PARTS":"-1"}
        self.isUsingDates = True
        self.isUsingStatus = True
        self.part_num = ""
        self.order_id = ""
        self.startDate = None
        self.endDate = None
        self.timeVariable = None
        self.statusVariable = None
    def filter(self, startDate, endDate, timeVariable, isUsingDates, statusVariable, isUsingStatus, part_num, order_id):
        self.isUsingDates = isUsingDates
        self.isUsingStatus = isUsingStatus
        self.part_num = part_num
        self.order_id = order_id
        self.startDate = startDate
        self.endDate = endDate
        self.timeVariable = timeVariable
        self.statusVariable = statusVariable
        currentIds = self.getAllIds()

        if self.isUsingStatus:
           currentIds = self.filterByStatus(self.filterVariables[self.statusVariable], currentIds)
        if self.isUsingDates:
            currentIds = self.filterByTime(self.filterVariables[timeVariable], currentIds)
        if order_id != "":
            currentIds = self.filterByOrder(currentIds)
        if part_num != "":
            currentIds = self.filterByPartNumber(currentIds)
        if currentIds:
            return list(currentIds)
        else:
            return []

    def getAllIds(self):
        return selectFromDB(f"""SELECT DISTINCT part_id FROM history ORDER BY part_id """)

    def filterByPartNumber(self, ids):
        filterIds = []
        for id in ids:
            id = id[0] if isinstance(id, tuple) else id
            if self.getPartNum(id) == self.part_num:
                filterIds.append(id)
        return filterIds
    def filterByOrder(self, ids):
        filterIds = []
        for id in ids:
            id = id[0] if isinstance(id, tuple) else id
            if self.getWorkOrder(id) == self.order_id:
                filterIds.append(id)
        return filterIds

    def filterByTime(self, filterVariable, ids):
        filteredIds = []
        for id in ids:
            if isEarlierThan(self.getDateVariable(id, filterVariable), self.endDate)  and isEarlierThan(self.startDate, self.getDateVariable(id, filterVariable)): 
                filteredIds.append(id)
        return filteredIds
        
    def filterByStatus(self, status, ids):
        if status == "0":
            filterFunction = self.isVirgin
        elif status == "1": 
            filterFunction = self.isCurrent
        else:
            filterFunction = self.isTerminated
        filteredIds = []
        for id in ids:
            realId = id[0] if isinstance(id, tuple) else id
            if filterFunction(realId):
                filteredIds.append(realId)
        return filteredIds

    
    def isVirgin(self, partId):
        starts = selectFromDB(f"""
        SELECT start_date FROM history WHERE start_date IS NOT NULL AND start_date IS NOT '00/00/00' AND part_id=? 
        """, (partId, ))
        if starts:
            return False
        else:
            return True

    def isTerminated(self, partId):
        lastEndDate = selectFromDB("""
        SELECT end_date FROM history WHERE step=(SELECT MAX(step) FROM history WHERE part_id=?) AND part_id=? 
        """, (partId, partId))
        if lastEndDate[0][0] in [None, '00/00/00']:
            return False
        else:
            return True

    def isCurrent(self, partId):
        currentId = selectFromDB("""
        SELECT part_id FROM currentParts WHERE part_id = ?
        """, (partId, ))
        if currentId:
            return True
        else:
            return False

    def getDateVariable(self, partId, dateVariable):
        partId = partId[0] if isinstance(partId, tuple) else partId
        date = selectFromDB(f"""
            SELECT {dateVariable} FROM history WHERE {dateVariable} IS NOT NULL AND {dateVariable} IS NOT '00/00/00' AND part_id=? 
            """, (partId, ))
        if date:
            return date[0][0]
        return date

    def getWorkOrder(self, partId):
        orderId = selectFromDB(f"""
        SELECT DISTINCT order_id FROM history WHERE part_id=?
        """, (partId, ))
        if orderId:
            return orderId[0][0]
        return orderId
    
    def getPartNum(self, partId):
        partNum = selectFromDB(f"""
        SELECT DISTINCT part_num FROM history WHERE part_id=?
        """, (partId, ))
        if partNum:
            return partNum[0][0]
        return partNum