import requests
from decimal import Decimal
from typing import List
import datetime

urlbegin = "https://www.smogon.com/stats/"

class Date:
    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
    def toString(self):
        strMonth = ""
        if self.month < 10:
            strMonth = "0" + str(self.month)
        else:
            strMonth = str(self.month)
        return str(self.year) + "-" + strMonth

class _UsageData:
    def __init__(self, id: str, data: str):
        self.id = id
        self.data = data

class PokeUsage:
    def __init__(self, dl):
        self.list = [["Name"]]
        if not isinstance(dl, list):
            dl = [dl]
        self.submitDataList(dl)
    def submitData(self, data: _UsageData):
        if data == None:
            return
        self.list[0].append(data[0])
        lines = str(data[1]).split("\\n")
        shearedData = []
        for line in lines:
            if line.__len__() <= 3 or not line[3].isnumeric():
                continue
            split = line.split("|")
            shearedData.append([split[2].strip(), Decimal(split[3].strip()[:-1])])
        shearedData.sort(key = lambda x: x[0])
        if self.list.__len__() == 1:
            for x in shearedData:
                self.list.append(x)
        else:
            # Uh-oh. After hours of work, and not managing to crack this,
            # I'm starting to feel a little in over my head.
            # I suppose there's only one choice here....
            # Take it away, ChatGPT!
            for i in range(1, len(shearedData)):
                pokemon_name = shearedData[i][0]
                pokemon_data = shearedData[i][1]

                # Check if the pokemon exists in self.list
                pokemon_found = False
                for j in range(1, len(self.list)):
                    if self.list[j][0] == pokemon_name:
                        self.list[j].append(pokemon_data)
                        pokemon_found = True
                        break

                # If the pokemon was not found, add a new sublist to self.list
                if not pokemon_found:
                    new_pokemon_sublist = [pokemon_name] + [Decimal("0")] * (len(self.list[0])-1)
                    new_pokemon_sublist[-1] = pokemon_data

                    # Find the correct index to insert the new sublist in alphabetical order
                    insert_index = 1
                    while insert_index < len(self.list) and self.list[insert_index][0] < pokemon_name:
                        insert_index += 1

                    # Insert the new sublist at the correct index
                    self.list.insert(insert_index, new_pokemon_sublist)
                    #Thanks ChatGPT, you're a real one!
    def submitDataList(self, datalist: List[_UsageData]):
        for data in datalist:
            self.submitData(data)
    def getData(self, poke: str, date: Date, rating):
        dataId = date.toString() + "-" + str(rating)
        dataIndex = 0
        try:
            dataIndex = self.list[0].index(dataId)
        except ValueError:
            return None
        for x in self.list:
            if x[0] == poke:
                return x[dataIndex]
    def averageUsage(self):
        out = []
        divisor = len(self.list[0]) - 1
        for x in self.list:
            if self.list.index(x) == 0:
                continue
            sum = Decimal("0")
            for y in x:
                if x.index(y) == 0:
                    continue
                sum += y
            out.append([x[0], sum/divisor])
        return out
        
            

#Method to download stats.
def getStats(year, month, format, rating):
    url = urlbegin + Date(year, month).toString() + "/" + format + "-" + str(rating) + ".txt"
    response = requests.head(url)
    if response.status_code == 200:
        r = requests.get(url, allow_redirects=True)
        return [Date(year, month).toString() + "-" + str(rating), r.content]

#A master method for downloading lots of data at once.
def getStatsBulk(format: str, startDate: Date, ratings: List[int], endDate: Date = None, exclusions: List[Date] = None, extras: List[Date] = None):
    year = startDate.year
    month = startDate.month
    datalist = []
    if endDate == None:
        endDate = Date(datetime.datetime.now().year, datetime.datetime.now().month)
    strExclusions = []
    for e in exclusions:
        strExclusions.append(e.toString())
    while year != endDate.year or month != endDate.month:
        if not Date(year, month).toString() in strExclusions:
            for r in ratings:
                datalist.append(getStats(year, month, format, r))
        month += 1
        if month == 13:
            year += 1
            month = 1
    if extras != None:
        for ext in extras:
            for r in ratings:
                datalist.append(getStats(ext.year, ext.month, format, r))
    return datalist