

from db.repositories import history_repo, current_parts_repo
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
        return history_repo.distinct_part_ids()

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
        starts = history_repo.get_start_dates(partId)
        if starts:
            return False
        else:
            return True

    def isTerminated(self, partId):
        lastEndDate = history_repo.get_last_end_date(partId)
        if lastEndDate[0][0] in [None, '00/00/00']:
            return False
        else:
            return True

    def isCurrent(self, partId):
        currentId = current_parts_repo.get_id(partId)
        if currentId:
            return True
        else:
            return False

    def getDateVariable(self, partId, dateVariable):
        partId = partId[0] if isinstance(partId, tuple) else partId
        date = history_repo.get_dates(dateVariable, partId)
        if date:
            return date[0][0]
        return date

    def getWorkOrder(self, partId):
        orderId = history_repo.distinct_order_id(partId)
        if orderId:
            return orderId[0][0]
        return orderId

    def getPartNum(self, partId):
        partNum = history_repo.distinct_part_num(partId)
        if partNum:
            return partNum[0][0]
        return partNum