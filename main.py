
from data import getDataFrameCountries, DataApi as da
import matplotlib.pyplot as plt

LIST_NAME_COUNTRIES = ['chile', 'peru', 'argentina', 'ecuador']
LIST_COLOR = ['r', 'b', 'g', 'k']
NAME_DEATH = da.NAME_DEATHS_SCALED
N = len(LIST_NAME_COUNTRIES)
dataFrameCountries = getDataFrameCountries(LIST_NAME_COUNTRIES, NAME_DEATH)

fig, ax = plt.subplots()
fig.suptitle('COVID-19')
for i in range(N):
    dataFrameCountries[i].plot(ax=ax, kind='scatter', x=da.NAME_TIME, y=NAME_DEATH, color=LIST_COLOR[i], label=LIST_NAME_COUNTRIES[i])
#ax.set_xticks()
ax.set_xlabel('days')
plt.show()
