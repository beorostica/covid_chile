import http.client
import json
import pandas as pd


def getDataFrameCountries(LIST_NAME_COUNTRIES, NAME_DEATH):

    # Get the initial data of all the countries analyzed:
    firstDatas = {}
    listFirstData_deaths = []
    for nameCountry in LIST_NAME_COUNTRIES:
        firstData_date, firstData_deaths = DataApi.getFirstData_DateAndDeaths(nameCountry, NAME_DEATH)
        firstDatas[nameCountry] = {'date': firstData_date, 'deaths': firstData_deaths}
        listFirstData_deaths.append(firstData_deaths)

    # Get the maximum number of death of the first datas:
    numberDeathsOffset = max(listFirstData_deaths)

    listDateOffset = []
    for nameCountry in LIST_NAME_COUNTRIES:
        dateOffset = DataApi.getDateDeathOffset(nameCountry, NAME_DEATH, numberDeathsOffset)
        listDateOffset.append(dateOffset)

    dataFrameCountries = []
    index = 0
    for nameCountry in LIST_NAME_COUNTRIES:
        dataFrame = DataApi.getDataFrame(nameCountry, listDateOffset[index])
        dataFrameCountries.append(dataFrame)
        index += 1

    return dataFrameCountries


class DataApi:

    # Define the data to read:
    NAME_TIME = 'time'
    NAME_DEATHS = 'deaths'
    NAME_DEATHS_SCALED = 'deaths_scaled'

    def getPopulation(nameCountry):

        conn = http.client.HTTPSConnection("restcountries-v1.p.rapidapi.com")
        headers = {
            'x-rapidapi-host': "restcountries-v1.p.rapidapi.com",
            'x-rapidapi-key': "b15b00cb3bmshd1bdaf17de5af10p126a6ejsn5cc2017f8f60"
        }
        conn.request("GET", "/name/" + nameCountry, headers=headers)

        # Read the data:
        res = conn.getresponse()
        dataRaw = res.read().decode("utf-8")
        dataJson_raw = json.loads(dataRaw)[0]
        numberPopulation = dataJson_raw['population']

        # Return the population:
        return numberPopulation

    def getFirstData_DateAndDeaths(nameCountry, NAME_DEATH):

        dataFrame = DataApi.getRawDataFrame(nameCountry)

        # Get and return the date and deaths of the first data:
        firstData_date = dataFrame.loc[0, DataApi.NAME_TIME]
        firstData_deaths = dataFrame.loc[0, NAME_DEATH]
        return firstData_date, firstData_deaths

    def getDateDeathOffset(nameCountry, NAME_DEATH, numberDeaths):

        dataFrame = DataApi.getRawDataFrame(nameCountry)
        for i in range(len(dataFrame)):
            if not dataFrame.loc[i, NAME_DEATH] < numberDeaths:
                return dataFrame.loc[i + 1, DataApi.NAME_TIME]

        return dataFrame.loc[0, DataApi.NAME_TIME]

    def getDataFrame(nameCountry, dateOffset):

        dataFrame = DataApi.getRawDataFrame(nameCountry)

        # Transform the time column to days since the date offset:
        dataFrame[DataApi.NAME_TIME] = (dataFrame[DataApi.NAME_TIME] - dateOffset).dt.total_seconds() / 86400

        # Return the data frame of the country:
        return dataFrame

    def getRawDataJson(nameCountry):

        # Request data to API:
        conn = http.client.HTTPSConnection("covid-193.p.rapidapi.com")
        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "b15b00cb3bmshd1bdaf17de5af10p126a6ejsn5cc2017f8f60"
        }
        conn.request("GET", "/history?country=" + nameCountry, headers=headers)

        # # This are other options not used:
        # conn.request("GET", "/countries", headers=headers)
        # conn.request("GET", "/statistics", headers=headers)

        # Read the data:
        res = conn.getresponse()
        dataRaw = res.read().decode("utf-8")
        dataJson_raw = json.loads(dataRaw)
        dataJson = dataJson_raw['response']

        # Return the response as a json object:
        return dataJson

    def getRawDataFrame(nameCountry):

        dataJson = DataApi.getRawDataJson(nameCountry)
        numberPopulation = DataApi.getPopulation(nameCountry)

        # Create the data frame:
        dataFrame = pd.DataFrame(columns=[DataApi.NAME_TIME, DataApi.NAME_DEATHS, DataApi.NAME_DEATHS_SCALED])
        for dataObj in dataJson:
            dateTime = dataObj[DataApi.NAME_TIME]
            numberDeaths = dataObj[DataApi.NAME_DEATHS]['total']
            dataFrame_row = {DataApi.NAME_TIME: dateTime,
                             DataApi.NAME_DEATHS: numberDeaths,
                             DataApi.NAME_DEATHS_SCALED: numberDeaths}
            dataFrame = dataFrame.append(dataFrame_row, ignore_index=True)
        dataFrame[DataApi.NAME_DEATHS_SCALED] = 1000000*dataFrame[DataApi.NAME_DEATHS_SCALED] / numberPopulation
        dataFrame = dataFrame.iloc[::-1]
        dataFrame = dataFrame.reset_index()

        # Transform column objects to datatypes:
        dataFrame[DataApi.NAME_TIME] = pd.to_datetime(dataFrame[DataApi.NAME_TIME])
        dataFrame[DataApi.NAME_DEATHS] = pd.to_numeric(dataFrame[DataApi.NAME_DEATHS]).astype('float64')
        dataFrame[DataApi.NAME_DEATHS_SCALED] = pd.to_numeric(dataFrame[DataApi.NAME_DEATHS_SCALED]).astype('float64')

        # Return the data frame of the country:
        return dataFrame

    def printRawDataJson(nameCountry):

        dataJson = DataApi.getRawDataJson(nameCountry)

        print('')
        print('################')
        print('### dataJson ###')
        print('################')
        dataJson_keys = dataJson.keys()
        print('dataJson.keys() = ' + str(dataJson_keys))
        for key in dataJson_keys:
            print('##################################################################')
            print('key = ' + key)
            print('value = ' + str(dataJson[key]))

        print('')
        print('############################')
        print("### dataJson['response'] ###")
        print('############################')
        dataJson_response = dataJson['response']
        for dataObject in dataJson_response:
            print(dataObject)

        print('')
        print('###############################')
        print("### dataJson['response'][0] ###")
        print('###############################')
        dataObject0 = dataJson_response[0]
        dataObject0_keys = dataObject0.keys()
        print("dataJson['response'][0].keys() = " + str(dataObject0_keys))
        for key in dataObject0_keys:
            print('##################################################################')
            print('key = ' + key)
            print('value = ' + str(dataObject0[key]))
