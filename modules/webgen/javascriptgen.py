# Author: Jason Kim
# Collaborators: Zachary Schmidt, Moaz Abdelmonem
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term

# This file contains all the functions neccessary to generate the JS of the 
# webpage which is not releated to the generation of the lines

# Dependencies: cleaner

from .. import cleaner

# Function that generates the JS before the generation of the course diagram
# Parameters:
#   controller - file handle for controller JS file
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
def intializeControllerJavaScript(sequenceDict, controller):
    generateIntitalBlockController(sequenceDict, controller)
    generatePlanBasedBlocksController(sequenceDict, controller)

# Function that properly concludes and closes the controller JS
# Parameters:
#   controller - file handle for controller JS
def closeControllerJavaScript(controller):
    controller.write("});\n")
    writeRightClickDirective(controller)
    controller.close()

# Function that appends the custom Angular directive to allow handling of
# right click events
# Parameters:
#   controller - file handle for controller JS
def writeRightClickDirective(controller):
    rightClickDirective = """app.directive('ngRightClick', function($parse) {
    return function(scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function(event) {
            scope.$apply(function() {
                event.preventDefault();
                fn(scope, {$event:event});
            });
        });
    };
    });"""
    controller.write(rightClickDirective)

# Function that generates the intital block of Javascript
# Parameters:
#   controller - file handle for controller JS file
def generateIntitalBlockController(sequenceDict, controller):
    planList = list(sequenceDict.keys())
    controller.write("var app = angular.module(\"main\", []);\n")
    controller.write("app.controller(\"main\", function($scope) { \n")
    controller.write("$scope.selectedPlan = \"" + cleaner.cleanString(planList[0])+ "\";\n")
    controller.write("var that = this;\n")
    controller.write("this.previousPlan = $scope.selectedPlan;\n")

    controller.write("""this.render = function(plan) {
            this.disable(this.previousPlan);
            this.enable(plan);
            this.previousPlan = plan;
};\n""")

    controller.write("""var radios = document.querySelectorAll("input[type=radio][name=planselector]");
Array.prototype.forEach.call(radios, function (radio) {
    radio.addEventListener("change", function () {
        that.render($scope.selectedPlan);
    });
});\n""")



# Function that generates the blocks of the controller JS that is dependent
# on the number and names of plans provided
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generatePlanBasedBlocksController(sequenceDict, controller):
    generatePlanBasedInitalVariables(sequenceDict, controller)
    generateDisableSwitchStatement(sequenceDict, controller)
    generateEnableSwitchStatement(sequenceDict, controller)
    generateAddLineSwitch(sequenceDict, controller)
    generateDeleteLineSwitch(sequenceDict, controller)
    generateAddToClickSwitch(sequenceDict, controller)
    generateDeleteFromClickSwitch(sequenceDict, controller)
    generateCategoryLegendJS(sequenceDict, controller)

# Function that generates the intial variables for the controller
# based on the plans
# Parameters: 
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generatePlanBasedInitalVariables(sequenceDict, controller):
    for plan in sequenceDict:
        controller.write("this." + cleaner.cleanString(plan) + "List = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "Clicked = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "LegendBtns = [];\n")
        controller.write("this." + cleaner.cleanString(plan) + "LegendBtnsClicked = [];\n")
        numterms = len(sequenceDict[plan].keys())
        controller.write("this." + cleaner.cleanString(plan) + "Terms = " + str(numterms) + ";\n")
        maxcourses = 0
        for term in sequenceDict[plan]:
            termcourses = len(sequenceDict[plan][term])
            if termcourses > maxcourses:
                maxcourses = termcourses
        controller.write("this." + cleaner.cleanString(plan) + "MaxCourses = " + str(maxcourses) + ";\n")

# Function that generates the switch statements and functions which handle
# disabling the lines of a plan when switched off.
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDisableSwitchStatement(sequenceDict, controller):
    formattedFunctionStatement = """this.{functionName} = function(plan) {{
    switch (plan) {{ \n"""
    formattedSwitchStatement = """  case "{planName}": 
    for (let i = 0; i < this.{planName}List.length; i++) {{
        this.{planName}List[i][0].{actionName}(true);
    }}
    break; \n"""
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    controller.write(formattedFunctionStatement.format(functionName="disable"))
    for plan in sequenceDict:
        controller.write(formattedSwitchStatement.format(planName=cleaner.cleanString(plan), 
                                                         actionName="hide"))
    controller.write(switchEndString)


# Function that generates the switch statements and functions which handle
# enabling of course boxes, lines between plans, and boxes that were highlighted
# from the legend.
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateEnableSwitchStatement(sequenceDict, controller):

    categoriesDict = sortIntoCategories(sequenceDict)  # sort courses into categories
    findLegendButtons(categoriesDict, controller)  # find legend buttons in the document, store them in a list

    formattedFunctionStatement = """this.{functionName} = function(plan) {{
  switch(plan) {{\n"""

    # layout: for each plan, show/display every course box in that plan,
    # then adjust the webpage width and height, then (for loop #1) restore all courses
    # that were clicked to their clicked state (highlighted with arrows drawn).
    # For loop #2: Restore all courses that were highlighted with the legend buttons
    # to their highlighted state and restore legend buttons to their pressed state.
    formattedSwitchStatement = """    case "{planName}": 
      for (let i = 0; i < this.{planName}List.length; i++) {{
          this.{planName}List[i][0].{actionName}(true);
      }}
      width = this.{planName}Terms*220 + 20;
      widthstr = width.toString() + "px";
      document.getElementById("main").style.width = widthstr;
      height = this.{planName}MaxCourses*100 + 440;
      heightstr = height.toString() + "px";
      document.getElementById("main").style.height = heightstr;
      for (let i = 0; i < this.{planName}Clicked.length; i++) {{
          var element = document.getElementById(this.{planName}Clicked[i][0]);
          element.classList.remove(this.{planName}Clicked[i][1]);
          element.classList.add(this.{planName}Clicked[i][1]+"-highlighted");
      }}
      for (let i = 0; i < this.{planName}LegendBtns.length; i++) {{
          var found = false;
          for (let j = 0; j < this.{planName}LegendBtnsClicked.length; j++) {{
              if (this.{planName}LegendBtnsClicked[j] == this.{planName}LegendBtns[i]) {{
                  found = true;
              }}
          }}
          if (found == false) {{
              this.{planName}LegendBtns[i].classList.remove("legendbutton-pressed");
              this.{planName}LegendBtns[i].classList.add("legendbutton");
          }}
          if (found == true) {{
              this.{planName}LegendBtns[i].classList.remove("legendbutton");
              this.{planName}LegendBtns[i].classList.add("legendbutton-pressed");
          }}
      }}
      break; \n"""

    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""

    controller.write(formattedFunctionStatement.format(functionName="enable"))
    for plan in sequenceDict:
        controller.write(formattedSwitchStatement.format(planName=cleaner.cleanString(plan), 
                                                         actionName="show"))
    controller.write(switchEndString)

# Finds all of the legend buttons in all categories & plans. Writes the js that
# pushes these button elements to a list storing all buttons in that plan.
# eg: TraditionalPlanLegendBtns is a list that holds all legend button elements in
# the Traditional Plan
# Parameters:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
#   controller - file handle for controller.js file
def findLegendButtons(categoriesDict, controller):
    # find the button in the doc
    formattedbtnStatement = """  var currbtn = document.getElementById("{categoryName}");\n"""
    # push the button element to a list
    formattedpushbtnStatement = """  that.{planName}LegendBtns.push(currbtn);\n"""

    for category in categoriesDict:
        # Only necessary to find button for each category (not each plan)
        # Special cases to handle electives
        if category == "ComplementaryElective":
            controller.write(formattedbtnStatement.format(categoryName="COMP"))
        elif category == "ProgramTechnicalElective":
            controller.write(formattedbtnStatement.format(categoryName="PROG"))
        elif category == "ITSElective":
            controller.write(formattedbtnStatement.format(categoryName="ITS"))
        else:
            # not an elective
            controller.write(formattedbtnStatement.format(categoryName=category))

        for plan in categoriesDict[category]:
            controller.write(formattedpushbtnStatement.format(planName=plan))

# Function that generates the switch statement and function addLine
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateAddLineSwitch(sequenceDict, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(line) {{
switch($scope.selectedPlan) {{ \n"""
    formattedAddLineSwitchStatement = """ case "{planName}":
    var index = this.{planName}List.findIndex((element) => element[0] == line);
    if (index == -1) {{
        line.show(false);
        this.{planName}List.push([line, 1])
    }}
    else {{
        this.{planName}List[index][1]++;
    }}
    break;\n"""
    controller.write(formattedFunctionStatement.format(functionName="addLine"))
    for plan in sequenceDict:
        controller.write(formattedAddLineSwitchStatement.format(planName=cleaner.cleanString(plan)))
    controller.write(switchEndString)


# Function that generates the switch statement and function removeLine
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDeleteLineSwitch(sequenceDict, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(line) {{
switch($scope.selectedPlan) {{ \n"""
    formmattedDeleteLineSwitchStatement = """ case "{planName}":
    var index = this.{planName}List.findIndex((element) => element[0] == line);
    if (index != -1) {{
        this.{planName}List[index][1]--
        if (this.{planName}List[index][1] <= 0) {{
            line.hide(false);
            this.{planName}List.splice(index, 1);
        }}
    }}
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="removeLine"))

    for plan in sequenceDict:
        controller.write(formmattedDeleteLineSwitchStatement.format(planName=cleaner.cleanString(plan)))

    controller.write(switchEndString)

# Function that generates the switch statement associated with the addToClicked method
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateAddToClickSwitch(sequenceDict, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(element) {{
switch($scope.selectedPlan) {{ \n"""
    formattedAddToClickStatement = """ case "{planName}":
    var index = this.{planName}Clicked.findIndex((item) => item[0] == element[0]);
    if (index == -1) {{
        this.{planName}Clicked.push(element);
    }}
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="addToClicked"))
    for plan in sequenceDict:
        controller.write(formattedAddToClickStatement.format(planName=cleaner.cleanString(plan)))
    
    controller.write(switchEndString)

# Function that generates the switch statement associated with the deleteFromClicked method
# Parameters:
#   sequenceDict - dict that maps plan name to a dict that represents the plan sequence
#   controller - file handle for controller.js file
def generateDeleteFromClickSwitch(sequenceDict, controller):
    switchEndString = """    default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedFunctionStatement = """this.{functionName} = function(element) {{
switch($scope.selectedPlan) {{ \n"""
    formattedAddToClickStatement = """ case "{planName}":
    var index = this.{planName}Clicked.findIndex((item) => item[0] == element);
    if (index != -1) {{
        this.{planName}Clicked.splice(index, 1);
    }}
    break;"""
    controller.write(formattedFunctionStatement.format(functionName="removeFromClicked"))
    for plan in sequenceDict:
        controller.write(formattedAddToClickStatement.format(planName=cleaner.cleanString(plan)))
    
    controller.write(switchEndString)

def generateHighlightCategoryFlags(categoriesDict, controller):
    formattedCategoriesFlagStatement = """var {categoryName}{planName}flag = false;\n"""
    for category in categoriesDict:
        if category == "": 
            continue
        for plan in categoriesDict[category]:
            if category == "ComplementaryElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "COMP", 
                                                                     planName = cleaner.cleanString(plan)))
            elif category == "ProgramTechnicalElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "PROG", 
                                                                     planName = cleaner.cleanString(plan)))
            elif category == "ITSElective":
                controller.write(formattedCategoriesFlagStatement.format(categoryName = "ITS", 
                                                                     planName = cleaner.cleanString(plan)))
            else:
                controller.write(formattedCategoriesFlagStatement.format(categoryName = cleaner.cleanString(category), 
                                                                     planName = cleaner.cleanString(plan)))
# Function that generates the listeners for the buttons for each
# category on the legend
# Parameters:
#   - categoriesDict: dict that maps categories to plans dict containing courses in 
#   that category
#   - controller: file handle to controller.js
def generateCategoryListeners(categoriesDict, controller):
    # format string for a category listener
    formattedCategoriesListener = """$scope.{categoryName}clickListener = function() {{
    var planName = $scope.selectedPlan;
    var pressedbtn = document.getElementById("{categoryNameId}");
    var checkFlag = "!{categoryName}" + planName + "flag";
    var flagBool = eval(checkFlag);
    if (flagBool) {{
        that.highlightCategory("{categoryName}", $scope.selectedPlan);
        pressedbtn.classList.remove("legendbutton");
        pressedbtn.classList.add("legendbutton-pressed");
        var addClick = "that." + planName + "LegendBtnsClicked.push(pressedbtn)";
        eval(addClick);
        var flagName = "{categoryName}" + planName + "flag";
        eval(flagName + " = true");
    }}
    else {{
        that.unhighlightCategory("{categoryName}", $scope.selectedPlan);
        pressedbtn.classList.remove("legendbutton-pressed");
        pressedbtn.classList.add("legendbutton");
        var findIndex = "var index = that." + planName + "LegendBtnsClicked.findIndex((element) => element[0] == pressedbtn)";
        eval(findIndex);
        var removeClick = "that." + planName + "LegendBtnsClicked.splice(index, 1)";
        eval(removeClick);
        var flagName = "{categoryName}" + planName + "flag";
        eval(flagName + " = false");
    }}\n"""
    for category in categoriesDict:
        # special cases to handle electives, category is not the same as ID
        if category == "ComplementaryElective":
            controller.write(formattedCategoriesListener.format(categoryName="COMP", categoryNameId="COMP"))
        elif category == "ProgramTechnicalElective":
            controller.write(formattedCategoriesListener.format(categoryName="PROG", categoryNameId="PROG"))
        elif category == "ITSElective":
            controller.write(formattedCategoriesListener.format(categoryName="ITS", categoryNameId="ITS"))
        else:
            # not an elective
            controller.write(formattedCategoriesListener.format(categoryName=category, categoryNameId=category))
        controller.write("}\n")

# Function that generates the switch statement to switch between catergoies within highlight
# or unhighlight function
# Parameters:
#   - categoriesDict: dict that maps categories to a dict of plans which contain courses within
#   that category
#   - controller: file handle to controller.js
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (T for highlighting)  
def generateCategorySwitch(categoriesDict, controller, highlight):
    # outer switch between categories
    switchEndString = """break;   default:
    console.log("shouldn't be here");
    }
};\n"""
    formattedCaseCat = """  case "{categoryName}":\n"""
    for category in categoriesDict:
        if cleaner.cleanString(category) == "ComplementaryElective":
            controller.write(formattedCaseCat.format(categoryName="COMP"))
        if cleaner.cleanString(category) == "ProgramTechnicalElective":
            controller.write(formattedCaseCat.format(categoryName="PROG"))
        if cleaner.cleanString(category) == "ITSElective":
            controller.write(formattedCaseCat.format(categoryName="ITS"))
        else:
            controller.write(formattedCaseCat.format(categoryName=cleaner.cleanString(category)))
        generatePlanSwitch(categoriesDict[category], controller, category, highlight)
        controller.write("""       }\n""")
        controller.write("""      break;\n""")
    controller.write(switchEndString)

# Function that generates the switch statement to switch between plans within highlight
# or unhighlight function for a specific category
# Parameters:
#   - planDict: dict that maps plans to courses in that category
#   - controller: file handle to controller.js
#   - category: name of the category
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (T for highlighting)  
def generatePlanSwitch(planDict, controller, category, highlight):
    # inner switch between plans
    formattedCasePlan  = """      case "{planName}":\n"""
    controller.write("    switch(planName) {\n")
    for plan in planDict:
        controller.write(formattedCasePlan.format(planName=cleaner.cleanString(plan)))
        generateCourseStatements(planDict[plan], controller, plan, category, highlight)
        controller.write("""       break;\n""")

# Function that generates the highlight or unhighlight statements for a specfic categtory
# and plan
# Parameters:
#   - courseList: list of course objects in that category for that plan
#   - controller: file handle to controller.js
#   - plan: name of current plan
#   - category: name of the category
#   - highlight: flag indicating if it is highlighting or unhighlighting 
#   (T for highlighting)  
def generateCourseStatements(courseList, controller, plan, category, highlight):
    compcounter = 0
    progcounter = 0
    itscounter = 0
    for course in courseList:
        # special cases to handle electives
        if course.name == "Complementary Elective":
            if highlight:
                generateElectiveHighlightStatement("COMP", 
                                                   "ComplementaryElective", 
                                                    plan, 
                                                    progcounter, 
                                                    controller)
            else:
                generateElectiveUnhighlightStatement("COMP", 
                                                   "ComplementaryElective", 
                                                    plan, 
                                                    progcounter, 
                                                    controller)
            compcounter += 1
            continue
        if course.name == "Program/Technical Elective":
            if highlight:
                generateElectiveHighlightStatement("PROG", 
                                                   "ProgramTechnicalElective", 
                                                    plan, 
                                                    progcounter, 
                                                    controller)
            else:
                generateElectiveUnhighlightStatement("PROG", 
                                                   "ProgramTechnicalElective", 
                                                    plan, 
                                                    progcounter, 
                                                    controller)
            progcounter += 1
            continue
        if course.name == "ITS Elective":
            if highlight:
                generateElectiveHighlightStatement("ITS", 
                                                   "ITSElective", 
                                                   plan, 
                                                   itscounter, 
                                                   controller)
            else:
                generateElectiveUnhighlightStatement("ITS", 
                                                   "ITSElective", 
                                                   plan, 
                                                   itscounter, 
                                                   controller)
            itscounter += 1
            continue
        # not an elective, fill formatted statement in with course attributes
        if highlight:
            generateNormalCourseHighlightStatement(course, plan, category, controller)
        else:
            generateNormalCourseUnhighlightStatement(course, plan, category, controller)


# Generates the statements needed to unhighlight a single elective when pressing
# the legend buttons
# Parameters:
#   - elective: shortend elective type
#   - longelective: long elective type
#   - plan: current plan
#   - category: category of course
#   - controller: file handle to controller.js
def generateElectiveHighlightStatement(elective, longelective, plan, counter, controller):
    formattedElectiveGetUnhighlightedElement = """        var {electiveName}elements = document.getElementsByClassName("{electiveName}");\n"""
    formattedElectivesHighlight = """        for (let i = 0; i < {electiveName}elements.length; i++) {{
          var currelement = document.getElementById({electiveName}elements.item(i).id);
          currelement.classList.remove("{electiveName}");
          currelement.classList.add("{electiveName}-highlighted");
          that.addToClicked(["{longElectiveName}{planName}{count}","{categoryName}"]);
        }}\n"""
    controller.write(formattedElectiveGetUnhighlightedElement.format(electiveName=elective))
    controller.write(formattedElectivesHighlight.format(electiveName=elective, 
                                                        count=counter, 
                                                        longElectiveName=longelective, 
                                                        planName=plan, 
                                                        categoryName=elective))

# Generates the statements needed to unhighlight a single elective when pressing
# the legend buttons
# Parameters:
#   - elective: shortend elective type
#   - longelective: long elective type
#   - plan: current plan
#   - category: category of course
#   - controller: file handle to controller.js
def generateElectiveUnhighlightStatement(elective, longelective, plan, counter, controller):
    formattedElectiveGetHighlightedElement = """        var {electiveName}elements = document.getElementsByClassName("{electiveName}-highlighted");\n"""
    formattedElectivesUnhighlight = """        for (let i = 0; i < {electiveName}elements.length; i++) {{
          var currelement = document.getElementById({electiveName}elements.item(i).id);
          currelement.classList.remove("{electiveName}-highlighted");
          currelement.classList.add("{electiveName}");
          that.removeFromClicked("{longElectiveName}{planName}{count}");
        }}\n"""
    controller.write(formattedElectiveGetHighlightedElement.format(electiveName=elective))
    controller.write(formattedElectivesUnhighlight.format(electiveName=elective, 
                                                          longElectiveName=longelective, 
                                                          count=counter, 
                                                          planName=plan, 
                                                          categoryName=elective))
# Generates the statements needed to highlight a single normal course when pressing
# the legend buttons
# Parameters:
#   - course: course object
#   - plan: current plan
#   - category: category of course
#   - controller: file handle to controller.js
def generateNormalCourseHighlightStatement(course, plan, category, controller):
    formattedGetElement = """       var {courseName}{planName}element = document.getElementById("{courseName}{planName}");\n"""
    formattedRemoveUnclicked = """       {courseName}{planName}element.classList.remove("{categoryName}");\n"""
    formattedAddToClicked = """       {courseName}{planName}element.classList.add("{categoryName}-highlighted");
       that.addToClicked(["{courseName}{planName}","{categoryName}"]);\n"""
    controller.write(formattedGetElement.format(planName=cleaner.cleanString(plan), courseName=cleaner.cleanString(course.name)))
    controller.write(formattedRemoveUnclicked.format(planName=cleaner.cleanString(plan), 
                                                     courseName=cleaner.cleanString(course.name), 
                                                     categoryName=cleaner.cleanString(category)))
    controller.write(formattedAddToClicked.format(planName=cleaner.cleanString(plan), 
                                                  courseName=cleaner.cleanString(course.name), 
                                                  categoryName=cleaner.cleanString(category)))

# Generates the statements needed to unhighlight a single normal course when pressing
# the legend buttons
# Parameters:
#   - course: course object
#   - plan: current plan
#   - category: category of course
#   - controller: file handle to controller.js
def generateNormalCourseUnhighlightStatement(course, plan, category, controller):
    formattedIfStatement = "if (!{courseName}{planName}flag) {{ \n"
    formattedGetElement = """       var {courseName}{planName}element = document.getElementById("{courseName}{planName}");\n"""
    formattedRemoveClicked = """       {courseName}{planName}element.classList.remove("{categoryName}-highlighted");\n"""
    formattedAddToUnclicked = """       {courseName}{planName}element.classList.add("{categoryName}");\n       
       that.removeFromClicked("{courseName}{planName}");\n"""
    controller.write(formattedIfStatement.format(planName=cleaner.cleanString(plan), 
                                                             courseName=cleaner.cleanString(course.name)))
    controller.write(formattedGetElement.format(planName=cleaner.cleanString(plan), 
                                                courseName=cleaner.cleanString(course.name)))
    controller.write(formattedRemoveClicked.format(planName=cleaner.cleanString(plan), 
                                                   courseName=cleaner.cleanString(course.name), 
                                                   categoryName=cleaner.cleanString(category)))
    controller.write(formattedAddToUnclicked.format(planName=cleaner.cleanString(plan), 
                                                    courseName=cleaner.cleanString(course.name), 
                                                    categoryName=cleaner.cleanString(category)))
    controller.write(" } \n")
          

# Generates the clickable category legend. Allows a click to highlight all
# courses in that category.
# Parameters:
#   sequenceDict - dict that stores course objects
#       key - plan name
#       value - dict with term name as key and list of course objs in that plan & term
#   controller - file handle for controller.js file
# Returns:
#   None
def generateCategoryLegendJS(sequenceDict, controller):
    # sort courses into categories and plans
    categoriesDict = sortIntoCategories(sequenceDict)

    # flags for click on legend
    generateHighlightCategoryFlags(categoriesDict, controller)

    #listeners for categories
    generateCategoryListeners(categoriesDict, controller)
       
    formattedFunctionStatement = """this.{functionName} = function(categoryName, planName) {{
switch(categoryName) {{ \n"""

    controller.write(formattedFunctionStatement.format(functionName="highlightCategory"))

    # switch statement between categories for highlight category
    generateCategorySwitch(categoriesDict, controller, True)

    controller.write(formattedFunctionStatement.format(functionName="unhighlightCategory"))

     # switch statement between categories for unhighlight category
    generateCategorySwitch(categoriesDict, controller, False)
    
# Sorts courses in sequnceDict into their categories.
# Parameters:
#   sequenceDict - dict that stores course objects
#       key - plan name
#       value - dict with term name as key and list of course objs in that plan & term
# Returns:
#   categoriesDict - dict storing course objects
#       key - category name (eg: MATH)
#       value - dict with key as plan name, value as course object
def sortIntoCategories(sequenceDict):
    categoriesDict = {}  # outer dict
    for plan in sequenceDict:
        for term in sequenceDict[plan]:
            for course in sequenceDict[plan][term]:
                cat = cleaner.cleanString(course.category)
                cleanplan = cleaner.cleanString(plan)
                interdict = {}  # inner dict
                interdict[cleanplan] = [course]
                if cat not in categoriesDict.keys():
                    # category not taken yet, add new category and new course list
                    categoriesDict[cat] = interdict
                else:
                    # category is present in dict
                    if cleanplan not in categoriesDict[cat].keys():
                        # category taken but not plan
                        # keep existing categories but add a new plan
                        categoriesDict[cat].update(interdict)
                    else:
                        # add to the existing list of courses in that plan in that category
                        categoriesDict[cat][cleanplan].append(course)
    
    return categoriesDict