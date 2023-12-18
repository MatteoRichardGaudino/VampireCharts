import os
import matplotlib.pyplot as plt

VAMPIRE_1B = 'vampire/One_Binding'
VAMPIRE_CB = 'vampire/Conjunctive_Binding'
VAMPIRE_DB = 'vampire/Disjunctive_Binding'

ONE_BINDING = '1b/One_Binding'
CNF_ONE_BINDING = 'cnf_1b/One_Binding'
ONE_CB = '1b/Conjunctive_Binding'
ONE_DB = '1b/Disjunctive_Binding'

VAMPIRE_COLOR = 'red'
ONE_BINDING_COLOR = 'green'


def stringBetween(string, start, end):
    return string.split(start)[1].split(end)[0].strip().replace(' ', '')

def timeToMilliseconds(time):
    #time.strip().replace(' ', '').replace('\n', '')
    # if time ends with 'ms' then remove it and return the number
    if time.endswith('ms'):
        return float(time[:-2])
    # if time ends with μs then remove it and return the number / 1000
    elif time.endswith('μs'):
        return float(time[:-2]) / 1000
    # if time ends with ns then remove it and return the number / 1000000
    elif time.endswith('ns'):
        return float(time[:-2]) / 1000000
    # if time ends with 's' then remove it and return the number * 1000
    elif time.endswith('s'):
        return float(time[:-1]) * 1000


class TimeProfile:
    def __init__(self, name, percentage, total, avg, cnt):
        self.name = name
        self.percentage = percentage
        self.total = timeToMilliseconds(total)
        self.avg = timeToMilliseconds(avg)
        self.cnt = cnt

    def __str__(self):
        return '(' + self.name + " " + str(self.percentage) + " " + str(self.total) + " " + str(self.avg) + " " + str(self.cnt) + ")"

    def fromFlattenedTimeProfile(tp):
        times = []
        splitted = tp.split('\n')
        times.append(
            TimeProfile(
                "root",
                100,
                stringBetween(splitted[0], "total:", ","),
                stringBetween(splitted[0], "avg:", ","),
                stringBetween(splitted[0], "cnt:", ","),
            )
        )
        # remove first element from splitted
        splitted.pop(0)
        for row in splitted:
            times.append(
                TimeProfile(
                    stringBetween(row, "]", "("),
                    stringBetween(row, "[", "%"),
                    stringBetween(row, "total:", ","),
                    stringBetween(row, "avg:", ","),
                    stringBetween(row, "cnt:", ","),
                )
            )
        return times


class Statistic:
    def __init__(self, programOutput, name):
        self.problem = name
        self.solved = True

        if "Condition in file " in programOutput:
            self.szsStatus = "AssertionViolated"
            self.solved = False
            self.terminationReason = "Assertion violated"
            self.memoryUsed = float("inf")
            self.timeElapsed = float("inf")
            self.timeProfile = []
            return

        # if programOutput does not contain 'SZS status'
        if "% Time limit reached!" in programOutput:
            self.szsStatus = "TimeLimit"
            self.solved = False
        elif "% Refutation not found, non-redundant clauses discarded%" in programOutput:
            self.szsStatus = "RefutationNotFound (non-redundant clauses discarded)"
            self.solved = False
            print("Refutation not found in " + name)
        else:
            self.szsStatus = stringBetween(programOutput, '% SZS status', ' for')
        self.terminationReason = stringBetween(programOutput, '% Termination reason: ', '\n')
        self.memoryUsed = int(stringBetween(programOutput, '% Memory used [KB]: ', '\n'))
        self.timeElapsed = stringBetween(programOutput, '% Time elapsed: ', '\n')
        self.timeProfile = TimeProfile.fromFlattenedTimeProfile(stringBetween(programOutput, '===== start of flattened time profile =====\n', '===== end of flattened time profile ====='))
        self.timeElapsed = timeToMilliseconds(self.timeElapsed)

        # remove classification and parsing times from timeElapsed
        for tp in self.timeProfile:
            if tp.name == "parsing":
                self.timeElapsed -= tp.total
            if tp.name == "Fragmentclassification":
                self.timeElapsed -= tp.total
            if tp.name == "Onebindingalgorithmconfiguration":
                self.timeElapsed -= tp.total

    def __str__(self):
        return "Problem: " + self.problem + "\n" + \
               "SZS status: " + self.szsStatus + "\n" + \
               "Termination reason: " + self.terminationReason + "\n" + \
               "Memory used: " + str(self.memoryUsed) + "\n" + \
               "Time elapsed: " + str(self.timeElapsed) + "\n" + \
               "Time profile: " + "[" + ", ".join([str(tp) for tp in self.timeProfile]) + "]"

    def problemPath(self):
        return "./Problems/" + self.problem[:3] + "/" + self.problem + ".p"


def buildStatisticFromDir(directory):
    statistics = []
    for filename in os.listdir(directory):
        if filename.endswith('.out'):
            # create a new statistic object
            fileContent = open(directory + '/' + filename, 'r').read()
            try:
                stat = Statistic(fileContent, filename[:-4])
                statistics.append(stat)
            except:
                print("Error while parsing " + filename)
                print(fileContent)
                exit(1)
    return statistics


def winningCountBarChart(vampire, oneB, fragment):
    oneBWin = 0
    vampireWin = 0

    absMeanDev = 0
    tot = len(vampire)

    for i in range(len(vampire)):
        if not vampire[i].solved and not oneB[i].solved:
            tot -= 1
            continue
        if not vampire[i].solved:
            oneBWin += 1
            continue
        if not oneB[i].solved:
            vampireWin += 1
            continue

        if vampire[i].timeElapsed < oneB[i].timeElapsed:
            vampireWin += 1
        else:
            oneBWin += 1
        if not vampire[i].solved or not oneB[i].solved:
            tot -= 1
            continue
        absMeanDev += abs(vampire[i].timeElapsed - oneB[i].timeElapsed)

    absMeanDev /= tot

    print("Vampire won " + str(vampireWin) + " times.")
    print("OneB won " + str(oneBWin) + " times.")
    print("Absolute mean deviation: " + str(absMeanDev) + "ms")

    plt.bar(["Vampire (%d)" % vampireWin, "1b (%d)" % oneBWin], [vampireWin, oneBWin], color=[VAMPIRE_COLOR, ONE_BINDING_COLOR])
    plt.title("(time) Vampire vs 1b (" + fragment + ")")
    plt.ylabel("Winning times")
    plt.xlabel("(Absolute mean deviation: " + "{:.2f}".format(absMeanDev) + "ms)")
    plt.show()

def winningCountBarChartMemory(vampire, oneB, fragment):
    oneBWin = 0
    vampireWin = 0

    absMeanDev = 0
    tot = len(vampire)

    for i in range(len(vampire)):
        if not vampire[i].solved and not oneB[i].solved:
            tot -= 1
            continue
        if not vampire[i].solved:
            oneBWin += 1
            continue
        if not oneB[i].solved:
            vampireWin += 1
            continue

        if vampire[i].memoryUsed < oneB[i].memoryUsed:
            vampireWin += 1
        else:
            oneBWin += 1
        if not vampire[i].solved or not oneB[i].solved:
            tot -= 1
            continue
        absMeanDev += abs(vampire[i].memoryUsed - oneB[i].memoryUsed)

    absMeanDev /= tot

    print("(memory) Vampire won " + str(vampireWin) + " times.")
    print("(memory) OneB won " + str(oneBWin) + " times.")
    print("(memory) Absolute mean deviation: " + str(absMeanDev) + "kb")

    plt.bar(["Vampire (%d)" % vampireWin, "1b (%d)" % oneBWin], [vampireWin, oneBWin], color=[VAMPIRE_COLOR, ONE_BINDING_COLOR])
    plt.title("(memory) Vampire vs 1b (" + fragment + ")")
    plt.ylabel("Winning times")
    plt.xlabel("(Absolute mean deviation: " + "{:.2f}".format(absMeanDev) + "kb)")
    plt.show()


def solvedCountPieChart(vampire, oneB, fragment):
    sVampire = 0
    sOneB = 0
    for i in range(len(vampire)):
        if vampire[i].solved:
            sVampire += 1
        if oneB[i].solved:
            sOneB += 1


    # 2 pie chart on the left vampire and on the right 1b
    plt.suptitle("Solutions found (" + fragment + ")")
    plt.subplot(1, 2, 1)
    plt.pie([sVampire, len(vampire) - sVampire], labels=["Solved", "Not solved"], autopct='%1.1f%%')
    plt.title("Vampire (%d)" % sVampire)
    plt.subplot(1, 2, 2)
    plt.pie([sOneB, len(oneB) - sOneB], labels=["Solved", "Not solved"], autopct='%1.1f%%')
    plt.title("1b (%d)" % sOneB)
    plt.show()


    # plt.bar(["Vampire", "1b"], [sVampire, sOneB])
    # plt.title("Solutions found (%s)" % fragment)
    # plt.ylabel("solutions found")
    # plt.xlabel("Solver")
    # plt.show()

def solutionBarChart(dataset, fragment, color):
    solved = 0
    timeLimit = 0
    refutationNotFound = 0
    assertionViolated = 0

    for i in range(len(dataset)):
        if dataset[i].szsStatus == "TimeLimit":
            timeLimit += 1
        elif dataset[i].szsStatus == "RefutationNotFound (non-redundant clauses discarded)":
            refutationNotFound += 1
        elif dataset[i].szsStatus == "AssertionViolated":
            assertionViolated += 1
        else:
            solved += 1

    x = []
    y = []
    if solved > 0:
        x.append("Solved (%d)" % solved)
        y.append(solved)
    if timeLimit > 0:
        x.append("Time limit (%d)" % timeLimit)
        y.append(timeLimit)
    if refutationNotFound > 0:
        x.append("Refutation not found (%d)" % refutationNotFound)
        y.append(refutationNotFound)
    if assertionViolated > 0:
        x.append("Assertion violated (%d)" % assertionViolated)
        y.append(assertionViolated)

    plt.bar(x, y, color=[color])
    plt.title(fragment)
    plt.ylabel("solutions found")
    plt.show()


def printSecondVictories(first, second, firstName, secondName):
    print("Victories for " + secondName + " over " + firstName + ":")
    for i in range(len(first)):
        if not first[i].solved:
            print(firstName + "Not_solved " + first[i].problemPath() + " szs: " + first[i].szsStatus)
        if not second[i].solved:
            print(secondName + "Not_solved " + second[i].problemPath() + " szs: " + second[i].szsStatus)
        elif first[i].timeElapsed > second[i].timeElapsed:
            print("%s [%s] %f [%s] %f" % (first[i].problemPath(), firstName, first[i].timeElapsed, secondName, second[i].timeElapsed))


def printMeanMaxMinTotalTime(dataset, name):
    mean = 0
    max = 0
    maxProblem = ""
    min = float("inf")
    minProblem = ""
    tot = 0
    totTime = 0
    for i in range(len(dataset)):
        if not dataset[i].solved:
            continue
        tot += 1
        totTime += dataset[i].timeElapsed
        mean += dataset[i].timeElapsed
        if dataset[i].timeElapsed > max:
            max = dataset[i].timeElapsed
            maxProblem = dataset[i].problemPath()
        if dataset[i].timeElapsed < min:
            min = dataset[i].timeElapsed
            minProblem = dataset[i].problemPath()
    mean /= tot
    print("^^^^^^^ " + name + " ^^^^^^^")
    print("mean: " + str(mean))
    print(maxProblem + " max: " + str(max))
    print(minProblem + " min: " + str(min))
    print("total time: " + str(totTime))
    print("solved problems: " + str(tot))
    print("---------------------------")




def unPoDiTutto(first, second, firstName, secondName):
    # print(
    #     "------------------------------------------------------------------------------------------------------------------------")
    # printSecondVictories(vampire, oneB, "Vampire", "1b")
    # print(
    #     "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    # printSecondVictories(oneB, vampire, "1b", "Vampire")
    # print(
    #     "------------------------------------------------------------------------------------------------------------------------")
    #
    # solutionBarChart(oneB, "1b - One Binding", ONE_BINDING_COLOR)
    # winningCountBarChart(vampire, oneB, "One Binding")
    # winningCountBarChartMemory(vampire, oneB, "One Binding")
    # solvedCountPieChart(vampire, oneB, "One Binding")
    #
    # printMeanMaxMinTotalTime(vampire, "Vampire")
    # printMeanMaxMinTotalTime(oneB, "1b")

    # stesse cose del commento ma sostituisci vampire con first e oneB con second
    print("------------------------------------------------------------------------------------------------------------------------")
    printSecondVictories(first, second, firstName, secondName)
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    printSecondVictories(second, first, secondName, firstName)
    print("------------------------------------------------------------------------------------------------------------------------")

    solutionBarChart(second, secondName, ONE_BINDING_COLOR)
    winningCountBarChart(first, second, secondName)
    winningCountBarChartMemory(first, second, secondName)
    solvedCountPieChart(first, second, secondName)

    printMeanMaxMinTotalTime(first, firstName)
    printMeanMaxMinTotalTime(second, secondName)


# vampire = buildStatisticFromDir(VAMPIRE_1B+"_2")
# oneB = buildStatisticFromDir(ONE_BINDING+"_5")
#
# # unPoDiTutto(vampire, oneB, "Vampire", "1b")
#
vampire = buildStatisticFromDir(VAMPIRE_1B+"_2")
oneB = buildStatisticFromDir("fof_1b/One_Binding")

unPoDiTutto(vampire, oneB, "Vampire", "1b")
#
# vampire = buildStatisticFromDir(VAMPIRE_CB+"_2")
# oneB = buildStatisticFromDir(ONE_CB+"_2")
#
# unPoDiTutto(vampire, oneB, "Vampire", "1b")

# vampire = buildStatisticFromDir("cnf_vampire/One_Binding")
# oneB = buildStatisticFromDir(CNF_ONE_BINDING)
#
# unPoDiTutto(vampire, oneB, "Vampire_cnf", "1B_cnf")

# vampire = buildStatisticFromDir("vampire/One_Binding_2")
# oneB = buildStatisticFromDir("fof_1b/One_Binding")
#
# print(len(vampire))
# print(len(oneB))
#
# unPoDiTutto(vampire, oneB, "Vampire_fof", "1B_fof")

vampire = buildStatisticFromDir("vampire/Conjunctive_Binding_2")
oneB = buildStatisticFromDir("fof_1b/Conjunctive_Binding")

print(len(vampire))
print(len(oneB))

unPoDiTutto(vampire, oneB, "Cj Vampire_fof", "Cj 1B_fof")