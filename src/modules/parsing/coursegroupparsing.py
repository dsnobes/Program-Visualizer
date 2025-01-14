# Author: Jason Kim
# Collaborators: Zachary Schmidt, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# The file contains the functions needed to extract the course group 
# information needed to generate the web page

# Function that finds the initial values to set each course group variable to
# in the JS
# Parameters:
#   courseGroupDict - dict that maps plans to the course groups that exist in them
#   courseGroupList - list of course groups taken in that program
# Returns a dict that maps the course group with the initial value it should take
def findInitialValuesofCourseGroups(courseGroupDict, courseGroupList):
    initialSelectionGroups = list(courseGroupDict.values())[0]
    initialCourseGroupVals = {}
    for element in courseGroupList:
        if element not in initialSelectionGroups:
            initialCourseGroupVals[element] = ""
        else:
            initialCourseGroupVals[element] = initialSelectionGroups[element][0]
    return initialCourseGroupVals

# Function that finds the list of all course groups taken that term
# Parameters:
#   courseGroupDict - dict that maps plans to the course groups that exist in them
# Returns a list of course groups taken in that program
def findListofAllCourseGroups(courseGroupDict):
    currentList = []
    for plan in courseGroupDict:
        for element in courseGroupDict[plan]:
            if element not in currentList:
                currentList.append(element)
    return currentList

# Function that constructs a dict that maps plans to the course groups existing in that plan
# and their options
# Parameters:
#   sequenceDict - dict that maps plan names to the plan dict which contains sequencing info about that plan
# Returns a dict that maps plans to the course groups that exist in them
def extractPlanCourseGroupDict(sequnceDict):
    courseGroupDict = {}
    for plan in sequnceDict:
        index = plan.find("{")
        if index != -1:
            shortenedPlanName = plan[0:index].strip()
        else:
            shortenedPlanName = plan
        if shortenedPlanName not in courseGroupDict:
            courseGroupDict[shortenedPlanName] = {}
        courseGroupList = extractCourseGroupListFromString(plan)
        if courseGroupList == []:
            continue
        planCourseGroupsDict = courseGroupDict[shortenedPlanName]
        courseGroupDict[shortenedPlanName] = appendCourseGroups(planCourseGroupsDict,courseGroupList)
    return courseGroupDict

# Function that appends course groups and options to a specfic plan course group dict
#   planCourseGroupDict - dict that maps course groups to a list of options taken in that group
#   courseGroupList - list of course group options
# Returns a new course group dict for that specifc plan
def appendCourseGroups(planCourseGroupsDict, courseGroupList):
    for group in courseGroupList:
        numOfGroup = int(''.join(filter(lambda s: (s.isdigit()), group)))  # if group is '3A' then numOfGroup is 3
        if numOfGroup not in planCourseGroupsDict:
            planCourseGroupsDict[numOfGroup] = []
        if group not in planCourseGroupsDict[numOfGroup]:
            planCourseGroupsDict[numOfGroup].append(group)
    return planCourseGroupsDict

# Function that creates a list of course groups for a specfic variation of a course group
# selection
# Parameters:
#   planName - long plan name of specific variant
# Returns a list of the options chosen in that variant
def extractCourseGroupListFromString(planName):
    index = planName.find("{")
    if index == -1:
        return []
    endIndex = planName.find("}")
    return planName[index+1:endIndex].split()
