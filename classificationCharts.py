import matplotlib.pyplot as plt
class Line:
    def __init__(self, line):
        # remove double spaces and split line into list
        split_line = line.replace("  ", " ").replace("\n", "").split(" ")
        self.problem = split_line[0]
        self.status = split_line[1]
        self.classification = split_line[2]
        self.sk_classification = split_line[3]


def countMap(dataSet):
    dataSetSet = set(dataSet)
    dataSetMap = {}
    for i in dataSetSet:
        dataSetMap[i] = dataSet.count(i)
    return dataSetMap

def classificationPieChart(title, classifications, filename):
    classificationMap = countMap(classifications)
    print(classificationMap)

    # plot classificationMap as a pie chart with a legend with percentages and actual values
    labels = ['{0} - {1}'.format(i, j) for i, j in classificationMap.items()]

    title = plt.title(title, fontweight="bold")
    title.set_ha("left")
    plt.gca().axis("equal")
    pie = plt.pie(classificationMap.values(), startangle=0, radius=1.2)
    plt.legend(pie[0], labels, bbox_to_anchor=(1, 0.5), loc="center right", fontsize=13,
               bbox_transform=plt.gcf().transFigure)
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
    plt.show()
    plt.savefig(filename)


classifications = open("fof_classification.txt", "r")
lines = []
# Print every line in the file
for line in classifications:
    lines.append(Line(line))
classifications.close()
# remove header line
lines.pop(0)

classifications = list(map(lambda x: x.classification, lines))
classificationPieChart("FOF problems without skolemization", classifications, "fof_classification.png")
classifications = list(map(lambda x: x.sk_classification, lines))
classificationPieChart("FOF problems with skolemization", classifications, "fof_sk_classification.png")

noneToFrag = list(filter(lambda x: x.sk_classification != "None" and x.classification == "None", lines))
noneToFrag = [x.sk_classification for x in noneToFrag]
classificationPieChart("None to Frag", noneToFrag, "noneToFrag.png")

classifications = open("cnf_classification.txt", "r")
lines = []
# Print every line in the file
for line in classifications:
    lines.append(Line(line))
classifications.close()
# remove header line
lines.pop(0)

classifications = list(map(lambda x: x.classification, lines))
classificationPieChart("CNF problems", classifications, "cnf_classification.png")