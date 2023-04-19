from pokeusage import *

pku = PokeUsage(getStatsBulk("gen7doublesou", Date(2019, 4), [1695, 1630], exclusions = [Date(2020, 2)]))
avgUsage = pku.averageUsage()

avgUsage.sort(key = lambda x: x[1])
output = ""

for x in avgUsage:
    output = x[0] + ", " + str(x[1]) + "\n" + output
output.strip()

file = open("ExampleOutput.csv", 'w')
file.write(output)