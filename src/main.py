# Author: Moaz Abdelmonem
# Collaborators: Jason Kim, Zachary Schmidt
# Oversight: Dr. David Nobes
# University of Alberta, Summer 2022, Curriculum Development Co-op Term


# This file is the main script for the generation of the program
# visualizer. When run, it will generate a Graphical User Interface (GUI)
# which will alow user to insert all necessary excel files.
# the file will parse the provided Excel files containing course
# and plan information to generate progamatically an interactive program
# diagram in the output directory.

# Dependencies: bs4, parsing, webgen, tkinter, xlrd

import tkinter
import traceback
import xlrd
from bs4 import BeautifulSoup
import modules.parsing.categoriesparsing as categoriesparsing
import modules.parsing.coursegroupparsing as coursegroupparsing
import modules.parsing.courseparsing as courseparsing
import modules.parsing.sequenceparsing as sequenceparsing
import modules.webgen.javascriptgen as javascriptgen
import modules.webgen.htmlgen as htmlgen
import modules.webgen.linegen as linegen
import modules.webgen.cssgen as cssgen
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image



# Debug function for cleanly printing contents of plan sequences
# Parameters:
#   sequenceDict - dict mapping plan names to a dict containing plan seqeunce
def debug(sequenceDict):
    for plan in sequenceDict:
        print(plan)
        for term in sequenceDict[plan]:
            print(term)
            for course in sequenceDict[plan][term]:
                print(course.name)
            print("\n")
        print("\n")

###Main GUI Window ###
window = Tk()
window.title('Program Visualizer Generator')
window.iconbitmap('output/images/favicon.ico')
window.geometry("1110x655")
window.configure(bg = "#ffffff")
canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 665,
    width = 1110,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)
window.resizable(False, False)

###progress Bar##
def add_progbar():
    global progbar
    progbar = ttk.Progressbar(
    window,
    orient='horizontal',
    mode='determinate',
    length=280
    )
    progbar.place(
    x=661, y=560
    )


def progress():
    progbar['value']+= 7.7
    window.update_idletasks()
    return progbar['value']

def websiteGeneration(value_label):
    print("Beginning generation...")
    # opening the template html file and constructing html
    # note: here we calling parsing to extract the course data!
    try:  
        with open("template.html") as input:
            # deriving parsed html and creating soup object
            soup = BeautifulSoup(input, 'html.parser')
            
            # opening the JS files
            print("Opening files...")
            value_label['text'] = 'Opening files...'
            controller = open("./output/js/controller.js", "w")
            indexJS = open("./output/js/index.js", "w")
            progress()

            #opening the CSS file
            categoryCSS = open("./output/styles/category.css", "w")

            # creating line manager
            lineManager = linegen.LineManager()

            # parsing the excel files with course info, pulls dependencies (prereqs, coreqs, reqs) too
            print("Parsing courses...")
            value_label['text'] = 'Parsing courses...'
            courseDict = courseparsing.parseCourses(courses_excel.get())
            progress()

            # extracting dept name for program sequence
            deptName = department.get()

            # parsing the excel file with accreditation unit info
            print("Parsing accreditation...")
            value_label['text'] = 'Parsing accreditation...'
            courseparsing.parseAccred(courseDict, acc_excel.get(), deptName)
            progress()
            
            # pulling the category and color info from excel
            print("Parsing categories...")
            value_label['text'] = 'Parsing categories...'
            courseDict, categoryDict = categoriesparsing.parseCategories(courseCat_excel.get(), courseDict)
            progress()

            # writing colour highlighting CSS
            print("Writing category CSS...")
            value_label['text'] = 'Writing category CSS...'
            mainCategoryDict, subCategoryDict = categoriesparsing.splitCategoryDict(categoryDict)
            cssgen.writeCategoryCSS(mainCategoryDict, subCategoryDict, categoryCSS)
            progress()

            # sequencing courses
            print("Parsing sequences...")
            value_label['text'] = 'Parsing sequences...'
            sequenceDict = sequenceparsing.parseSeq(seq_excel.get(), courseDict)
            progress()

            # extracting course group information
            courseGroupDict = coursegroupparsing.extractPlanCourseGroupDict(sequenceDict)
            courseGroupList = coursegroupparsing.findListofAllCourseGroups(courseGroupDict)
            initialCourseGroupVals = coursegroupparsing.findInitialValuesofCourseGroups(courseGroupDict, courseGroupList)


            # generating initial JS based on the number and names of plans
            print("Intialzing JS files...")
            value_label['text'] = 'Intialzing JS files...'
            javascriptgen.initializeControllerJavaScript(sequenceDict, 
                                                        initialCourseGroupVals,
                                                        courseGroupDict,
                                                        courseGroupList, 
                                                        controller)
            progress()
            #locating title tag
            topTitleTag = soup.head.find("title")
            titleTag = soup.body.find("a", class_="site-title")

            #locating main div, this is where all the html will be written
            mainTag = soup.body.find("div", id="main")

            # customizing webpage title
            print("Writing title...")
            value_label['text'] = 'Writing title...'
            htmlgen.switchTitle(titleTag, topTitleTag, deptName)
            progress()

            # locating form tag
            formTag = mainTag.find("form")

            # placing main radio inputs
            print("Placing radio inputs...")
            value_label['text'] = 'Placing radio inputs...'
            htmlgen.placeRadioInputs(formTag, courseGroupDict, soup)
            progress()

            # locating course group selector
            courseGroupSelectTag = soup.body.find("div", class_="coursegroupselector")

            # placing submenu radio inputs
            htmlgen.placeCourseGroupRadioInputs(courseGroupSelectTag, soup, courseGroupDict)

            # locating legend tag
            legendTag = mainTag.find("div", class_="legend")

            # places legend for color-coding
            print("Placing legend...")
            value_label['text'] = 'Placing legend...'
            htmlgen.placeLegend(legendTag, categoryDict, soup)
            progress()

            # Generating display tag, this is where the course divs will be written
            print("Generating display tag...")
            value_label['text'] = 'Generating display tag...'
            displayTag = htmlgen.generateDisplayDiv(soup, courseGroupList)
            progress()

            mainTag.append(displayTag)

            #placing the HTML and generating JS based on the courses (drawing lines)
            value_label['text'] = 'Placing course diagram...'
            print("Placing course diagram...")
            htmlgen.placePlanDivs(displayTag, 
                                  sequenceDict, 
                                  soup, 
                                  indexJS, 
                                  controller, 
                                  lineManager)
            progress()
            # closing JS and CSS files
            print("Closing files...")
            value_label['text'] = 'Closing files...'
            javascriptgen.closeControllerJavaScript(controller)
            indexJS.close()
            categoryCSS.close()
            progress()
    except FileNotFoundError as err:
       if (err.strerror == "No such file or directory"):
        raise FileNotFoundError("Either the template HTML file is not in the same directory as the script or" +
       " the output directory is not organized correctly or does not exist")
       else:
        raise FileNotFoundError(str(err))
    return soup

def writingHTML(soup):
    # writing output to an output html
    try:
        print("Writing final HTML...")
        with open("./output/index.html", "w", encoding="utf-8") as output:
            output.write(str(soup))
    except FileNotFoundError:
        raise FileNotFoundError("The directory you are in does not have a directory named output.")

def main():
    add_progbar()
    value_label = Label(window, bg="white")
    value_label.place(x=748, y= 585)
    try:
        soup = websiteGeneration(value_label)
        writingHTML(soup)
        print("Generation Completed!")
        value_label['text'] = 'Generation Completed!'
        messagebox.showinfo('Status',message="Webpage successfully generated!")
    except (FileNotFoundError, xlrd.biffh.XLRDError, AssertionError) as e:
        print("Error occured! Handling exception")
        messagebox.showerror("Error", str(e))
        traceback.print_exc()
    except Exception as e:
        print("Error occured! Handling exception")
        messagebox.showerror("Error", "An unhandled error has occured, please contact the developers" + 
        " and include the following stack trace:\n" +
        traceback.format_exc())
        traceback.print_exc()
    finally:
        progress()
        progbar.destroy()
        value_label.destroy()



###browse functions###
def courseBrowse():
    filename =filedialog.askopenfilename()
    courses_excel.delete(0, END)
    courses_excel.insert(tkinter.END, filename) 

def catBrowse():
    filename =filedialog.askopenfilename()
    courseCat_excel.delete(0, END)
    courseCat_excel.insert(tkinter.END, filename)

def seqBrowse():
    filename =filedialog.askopenfilename()
    seq_excel.delete(0, END)
    seq_excel.insert(tkinter.END, filename) 

def accBrowse():
    filename =filedialog.askopenfilename()
    acc_excel.delete(0, END)
    acc_excel.insert(tkinter.END, filename) 

def show(selection):
    department.delete(0, END)
    department.insert(tkinter.END, selection) 

#new window
def new_window():

    global new_img1, new_img2, new_img3,new_img4, new_tutorial, new_web_img, new_header, new_footer
    helpWin = Toplevel()
    helpWin.geometry('1400x700')
    helpWin.title("Manual")
    helpWin.iconbitmap('output/images/favicon.ico')
    helpWin.resizable(0,0)

    #### Scroll bar ####
    # Create A Main Frame
    main_frame = Frame(helpWin)
    main_frame.pack(fill=BOTH, expand=1)

    # Create A Canvas
    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # Add A Scrollbar To The Canvas
    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)

    # Configure The Canvas
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))

    # Create ANOTHER Frame INSIDE the Canvas
    second_frame = Frame(my_canvas)

    # Add that New frame To a Window In The Canvas
    my_canvas.create_window((0,0), window=second_frame, anchor="nw")

    header_img = Image.open("GUI_images/helpbg.png")
    header_resize = header_img.resize((1600,100))
    new_header = ImageTk.PhotoImage(header_resize)
    header_label = Label(second_frame,image=new_header, anchor=W)
    header_label.place(x=0, y=0)

    header = Message(second_frame, 
    text="Plan Visualizer WebGen\nUser Manual",
    aspect=800,
    justify=CENTER,
    font= ('Helvetica 15 underline'),
    bg='#275D38',
    fg='white'
    )
    header.grid(row=0, column=1, pady=25)


    message1 = Label(second_frame, 
    text="1- Make sure the directory you are in has a directory named output and a template.html file."
    )
    message1.grid(row=1, column=0,padx=20, pady=20)

    message2 = Label(second_frame, 
    text="2- Make sure you have the following Excel files (All Excel files must be in the .xls format): "
    )
    message2.grid(row=2, column=0,padx=20, pady=20)
    #courses.xls image
    excel_pic1 = Image.open("GUI_images/courseexcel.png")
    resized1 = excel_pic1.resize((100,100))
    new_img1 = ImageTk.PhotoImage(resized1)
    img_label = Label(second_frame,image=new_img1)
    img_label.place(x=100, y=228)

    #categories.xls image
    excel_pic2 = Image.open("GUI_images/catexcel.png")
    resized2 = excel_pic2.resize((100,100))
    new_img2 = ImageTk.PhotoImage(resized2)
    img_label2 = Label(second_frame,image=new_img2)
    img_label2.place(x=500, y=228)

    #Sequencing.xls image
    tutorial_img = Image.open("GUI_images/seqexcel.png")
    resized_img = tutorial_img.resize((100,100))
    new_img4 = ImageTk.PhotoImage(resized_img)
    img_label3 = Label(second_frame,image=new_img4)
    img_label3.place(x=900, y= 228)

    #AU_Count.xls image
    accreditation_img = Image.open("GUI_images/AU_count.png")
    resized_img = accreditation_img.resize((100,100))
    new_img3 = ImageTk.PhotoImage(resized_img)
    img_label4 = Label(second_frame,image=new_img3)
    img_label4.grid(row=3, column=2, padx=150)


    #excel file description
    pic1_description = Label(second_frame, text="This Excel file must contain\nall individual course information.")
    pic1_description.place(x=65, y=330)

    pic2_description = Label(second_frame, text="This Excel file must contain course categories\nand all courses that fall under each category.")
    pic2_description.place(x=430, y=330)

    pic3_description = Label(second_frame, text="This Excel file must contain\nall possible plan sequences.")
    pic3_description.place(x=880, y=330)

    pic4_description = Label(second_frame, text="This Excel file must contain\nall accreditation unit information.")
    pic4_description.grid(row=4, column=2)

    message3 = Label(second_frame, 
    text="3- Type in the Excel file name (if it's present in the same directory as the program files) or\n provide it's path:"
    )
    message3.grid(row=5, column=0,padx=20, pady=25)

    #GUI image 
    tutorial_img = Image.open("GUI_images/tutorial.png")
    resized_img = tutorial_img.resize((500,300))
    new_tutorial = ImageTk.PhotoImage(resized_img)
    tut_label = Label(second_frame,image=new_tutorial)
    tut_label.grid(row=6, column=1, padx=10, pady=20)

    message4 = Label(second_frame, 
    text="4- Refresh the webpage and the plan visualizer webpage will be generated! "
    )
    message4.grid(row=7, column=0,padx=20, pady=25)

    web_img = Image.open("GUI_images/website.png")
    resized_webImg = web_img.resize((500, 300))
    new_web_img = ImageTk.PhotoImage(resized_webImg)
    web_label = Label(second_frame, image=new_web_img)
    web_label.grid(row=8, column=1)

    footer_img = Image.open("GUI_images/helpbg.png")
    footer_resize = footer_img.resize((1630,200))
    new_footer = ImageTk.PhotoImage(footer_resize)
    footer_label = Label(second_frame,image=new_footer, anchor=W)
    footer_label.place(x = 0, y=1180)
    footer = Message(second_frame, 
    text="Developers:\nJason Kim, Summer 2022\n Moaz Abdelmonem, Summer 2022\n Zachary Schmidt, Summer 2022\n\n Supervised by: Dr. David Nobes ",
    aspect=800,
    justify=CENTER,
    font= ('Helvetica 12'),
    bg='#275D38',
    fg='white'
    )
    footer.grid(row=9, column=1, pady=25)

menubar = Menu(window)
window.config(menu=menubar)
# create the Help menu
help_menu = Menu(
    menubar,
    tearoff=0
)

# adding the Help menu to the menubar
menubar.add_cascade(
    label="Help",
    menu=help_menu
)

help_menu.add_command(
    label='About...',
    command=new_window

)
help_menu.add_separator()
help_menu.add_command(
    label='Version1-2022',
    font='Times 10'
    
)

##Course Excel file UI##
courseEntry_img = PhotoImage(file = f"GUI_images/img_textBox0.png")
courseEntry_bg = canvas.create_image(
    800.5, 151.5,
    image = courseEntry_img)

courses_excel = Entry(
    bd = 0,
    bg = "#d9d9d9",
    highlightthickness = 0,
    font='halvetica 12')
courses_excel.insert(tkinter.END, "")
courses_excel.place(
    x = 661, y = 134,
    width = 279,
    height = 33)

##Categories excel file UI##
catEntry_img = PhotoImage(file = f"GUI_images/img_textBox1.png")
catEntry_bg = canvas.create_image(
    800.5, 226.5,
    image = catEntry_img)

courseCat_excel = Entry(
    bd = 0,
    bg = "#d9d9d9",
    highlightthickness = 0,
    font='halvetica 12')
courseCat_excel.insert(tkinter.END, "")
courseCat_excel.place(
    x = 661, y = 209,
    width = 279,
    height = 33)

##Sequencing excel file UI##
seqEntry_img = PhotoImage(file = f"GUI_images/img_textBox2.png")
seqEntry_bg = canvas.create_image(
    800.5, 304.5,
    image = seqEntry_img)

seq_excel = Entry(
    bd = 0,
    bg = "#d9d9d9",
    highlightthickness = 0,
    font='halvetica 12')
seq_excel.insert(tkinter.END, "")
seq_excel.place(
    x = 661, y = 287,
    width = 279,
    height = 33)

##Accreditation Excel file UI##
accEntry_img = PhotoImage(file = f"GUI_images/img_textBox3.png")
accEntry_bg = canvas.create_image(
    800.5, 382.5,
    image = accEntry_img)

acc_excel = Entry(
    bd = 0,
    bg = "#d9d9d9",
    highlightthickness = 0,
    font='halvetica 12')
acc_excel.insert(tkinter.END, "")
acc_excel.place(
    x = 661, y = 365,
    width = 279,
    height = 33)


##department name UI##
deptEntry_img = PhotoImage(file = f"GUI_images/img_textBox4.png")
deptEntry_bg = canvas.create_image(
    800.5, 459.5,
    image = deptEntry_img)


department = Entry(
    bd = 0,
    bg = "#d9d9d9",
    highlightthickness = 0,
    font='halvetica 12')
department.insert(tkinter.END, "")
department.place(
    x = 661, y = 442,
    width = 279,
    height = 33)

##deptNames menu##
menubutton = tkinter.Menubutton(window, text="Select", font='Helvatica 13',
                           borderwidth=0, relief="raised",
                           indicatoron=True, bg='#27715B',fg='White', border=3)
deptMenu = tkinter.Menu(menubutton, tearoff=False)
menubutton.configure(menu=deptMenu)
deptMenu.add_radiobutton(label="Chemical Engineering", font='halvetica 12', command=lambda: show('Chemical Engineering'))
deptMenu.add_radiobutton(label="Civil Engineering", font='halvetica 12', command= lambda:show('Civil Engineering'))
deptMenu.add_radiobutton(label="Computer Engineering", font='halvetica 12', command= lambda:show('Computer Engineering'))
deptMenu.add_radiobutton(label="Electrical Engineering", font='halvetica 12', command= lambda:show('Electrical Engineering'))
deptMenu.add_radiobutton(label="Engineering Physics", font='halvetica 12',command= lambda:show('Engineering Physics'))
deptMenu.add_radiobutton(label="Materials Engineering", font='halvetica 12',command= lambda:show('Materials Engineering'))
deptMenu.add_radiobutton(label="Mechanical Engineering", font='halvetica 12',command= lambda:show('Mechanical Engineering'))
deptMenu.add_radiobutton(label="Mechatronics Engineering", font='halvetica 12',command= lambda:show('Mechatronics Engineering'))
deptMenu.add_radiobutton(label="Mining Engineering", font='halvetica 12',command= lambda:show('Mining Engineering'))
deptMenu.add_radiobutton(label="Petroleum Engineering", font='halvetica 12',command= lambda:show('Petroleum Engineering'))

menubutton.place(x=985, y=442)

##Background image##
background_img = PhotoImage(file = f"GUI_images/background.png")
background = canvas.create_image(
    470.0, 332.5,
    image=background_img)

##Browse buttons##
browseImg1 = PhotoImage(file = f"GUI_images/img1.png")
button1_excel = Button(
    image = browseImg1,
    borderwidth = 0,
    highlightthickness = 0,
    command = courseBrowse,
    relief = "flat")

button1_excel.place(
    x = 982, y = 134,
    width = 95,
    height = 37)

browseImg2 = PhotoImage(file = f"GUI_images/img2.png")
button2_excel = Button(
    image = browseImg2,
    borderwidth = 0,
    highlightthickness = 0,
    command = catBrowse,
    relief = "flat")

button2_excel.place(
    x = 982, y = 213,
    width = 95,
    height = 38)

browseImg3 = PhotoImage(file = f"GUI_images/img3.png")
button3_excel = Button(
    image = browseImg3,
    borderwidth = 0,
    highlightthickness = 0,
    command = seqBrowse,
    relief = "flat")

button3_excel.place(
    x = 982, y = 288,
    width = 95,
    height = 37)


browseImg4 = PhotoImage(file = f"GUI_images/img4.png")
button4_excel = Button(
    image = browseImg4,
    borderwidth = 0,
    highlightthickness = 0,
    command = accBrowse,
    relief = "flat")

button4_excel.place(
    x = 982, y = 365,
    width = 95,
    height = 37)

##Generation button##
genImg = PhotoImage(file = f"GUI_images/img0.png")
generate_button = Button(
    image = genImg,
    borderwidth = 0,
    highlightthickness = 0,
    command = main,
    relief = "flat")

generate_button.place(
    x = 738, y = 501,
    width = 126,
    height = 43)







if __name__ == "__main__":
    window.mainloop()