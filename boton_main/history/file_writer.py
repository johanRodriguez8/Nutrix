
from db.repositories import history_repo, parts_repo
import csv
from csv2pdf import convert
from utils.helpers import isEarlierThan, getDateTime
from db.part_tracking.part  import Part
import os
class FileWriter():
    def __init__(self):
        self.__init__
        self.fileTypes = {"CSV Files (*.csv)":".csv", "HTML Files (*.html)":".html"}
        self.partHeader = ["PART NUMBER", "WORK ORDER", "PART ID", "UPLOAD TIME"]
        self.programHeader = [
                "PROGRAM", "ROBOT", "MIN DRY", "MAX DRY",
                "STATE", "DATE", "START", "END", "RUN",
                "FROM HANGER", "FROM CONV", "TO HANGER", "TO CONV", "TIME DEV"
            ]
        self.ids = None
        self.currentExtension = None
        self.filePath = None
        self.extension = None

    def createFile(self, path, extension, ids):
        self.ids = ids
        self.currentExtension = extension
        self.filePath = path
        if extension == "CSV Files (*.csv)":
            self.createCSVFile()
        elif extension == "HTML Files (*.html)":
            self.createHTMLFile()
        elif extension == "CSV y HTML":
            self.currentExtension = "CSV Files (*.csv)"
            self.createCSVFile()
            self.currentExtension = "HTML Files (*.html)"
            self.createHTMLFile()
    
    def getTerminatedPartInfo(self, partId):
        pid = partId[0] if isinstance(partId, tuple) else partId
        return history_repo.get_terminated_part_info(pid)
    def getDefaultName(self, path):
        fecha, hora = getDateTime()
        fecha = fecha.replace("/", "_")
        fileName = path + "/SUMMARY" + fecha 
        return fileName

    def createCSVFile(self):
        fileName = self.filePath + self.fileTypes[self.currentExtension]
        with open(fileName, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            piezas = []
            partHeader = ["PART NUMBER", "WORK ORDER", "PART ID", "UPLOAD TIME"]
            programHeader = [
                "PROGRAM", "ROBOT", "MIN DRY", "MAX DRY", "CURRENT DRY",
                "STATE", "DATE", "START", "END", "RUN",
                "FROM HANGER", "FROM CONV", "TO HANGER", "TO CONV", "TIME DEV"
            ]
            for id in self.ids:
                pid = id[0] if isinstance(id, tuple) else id
                headerInfo = history_repo.get_file_header(pid)
                writer.writerow(partHeader)
                writer.writerow(headerInfo[0])
                writer.writerow(programHeader)
                programInfo = self.getTerminatedPartInfo(id)
                for program in programInfo:
                    writer.writerow(program)
            csvfile.close()

    def createHTMLFile(self):
        fileName = self.filePath + self.fileTypes[self.currentExtension]
        with open(fileName, 'w', newline='') as htmlfile:
            fecha, hora = getDateTime()
            headerHtml = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>HISTORY REPORT {fecha}, {hora}</title>
    <meta name="viewport" content="width=device-width" />
    <style>
    table {{
            border: 3px solid #919191;
            border-radius: 8px;
            background-color: #f5f5f5;
            margin: 8px;
    }}
    th, td {{
        border: 1px solid;
    }}
    </style>
  </head>
  <body>
"""
            htmlfile.write(headerHtml)
            for id in self.ids:
                id = id if not isinstance(id, tuple) else id[0]
                header = self.getPartHTMLHeader(id)
                htmlfile.write(header)
                programsInfo = self.getTerminatedPartInfo(id)
                programTable = self.getHistoryTableHTML(programsInfo)
                htmlfile.write(programTable)
                line = "<hr style=\"border: 0; height: 4px; background: #333; width: 100%;\"> \n"
                htmlfile.write(line)
            endHtml = "</body> \n </html>"
            htmlfile.write(endHtml)
            htmlfile.close()


    def getPartHTMLHeader(self, partId):
        headerInfo = parts_repo.get_file_header(partId)
        if not headerInfo:
            headerInfo = history_repo.get_file_header(partId)
        partNum, order_id, part_id, upload_date = headerInfo[0]
        header = f"""
            <table width="100%" cellspacing="0" cellpadding="4">
                <tr>
                    <th align="center">PART NUMBER</th>
                    <th align="center">WORK ORDER</th>
                    <th align="center">PART ID</th>
                    <th align="center">UPLOAD TIME</th>
                </tr>
                <tr>
                    <td align="center">{partNum}</td>
                    <td align="center">{order_id}</td>
                    <td align="center">{partId}</td>
                    <td align="center">{upload_date}</td>
                </tr>
        </table>
        """
        return header
    def getHistoryTableHTML(self, programsInfo):
        table = """<table width="100%" cellspacing="0" cellpadding="15">\n"""
        programHeader = [
                "PROGRAM", "ROBOT", "MIN DRY", "MAX DRY",
                "STATE", "DATE", "START", "END", "RUN",
                "FROM HANGER", "FROM CONV", "TO HANGER", "TO CONV", "TIME DEV"
            ]
        table = table + "<tr>\n"
        for title in programHeader:
            table = table + f"<th align=\"center\">{title}</th>\n"
        table = table + "</tr>\n"
        for program in programsInfo:
            table = table + "<tr>\n"
            for info in program:
                table = table + f"<td align=\"center\">{info}</td>\n"
            table = table + "</tr>\n"
        table = table + " </table>\n"
        return table