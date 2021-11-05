import csv
import datetime as dt
import glob
import os
import re
from optparse import OptionParser

import nltk
import pandas as pd

from Course import ENCS3130, Student

# defining an option parser to let the user execute the program using these options in the terminal
parser = OptionParser("""
-s path Student List sheet.
--ar Path to the folder of Meeting Attendance Reports.
--pr Path to the folder of Meeting Participation Reports.
-o Path to store all output documents/folders.
-p only consider students who attended more than P minutes in the meeting as present.
--Tb  All entries within Tb minutes of the first entry will be dropped and not considered in the Class Score Sheet.
--Te  All entries within Te minutes of the last entry will be dropped and not considered in the Class Score Sheet.
""")

# adding all the options required for the terminal with their default values
parser.add_option("-s", dest="List_sheet", default=os.getcwd(), type="string", help="Student List sheet.")
parser.add_option("--ar", dest="Ar_sheet", default="Attendance", type="string",
                  help="Path to the folder of Meeting Attendance Reports.")
parser.add_option("--pr", dest="Pr_sheet", default="Participation", type="string",
                  help="Path to the folder of Meeting Participation Reports.")
parser.add_option("-o", dest="out_sheet", default="output", type="string",
                  help="Path to store all output documents/folders.")
parser.add_option("-p", dest="P", default="0", type="int",
                  help="only consider students who attended more than P minutes in the meeting as present.")
parser.add_option("--Tb", dest="Tb", default="0", type="int",
                  help="All entries within Tb minutes of the first entry will be dropped and not considered in "
                       "the Class Score Sheet.")
parser.add_option("--Te", dest="Te", default="0", type="int",
                  help="All entries within Te minutes of the last entry will be dropped and not considered in "
                       "the Class Score Sheet.")
(options, args) = parser.parse_args()


def make_directory(path=''):
    """makes a directory in path if it doesn't exist and return the path to this directory

    Parameters
    ----------
    path : str
        path of the directory.

    """
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def time_control(edgeEntry, option=0, flag=0):
    """Returns the minimum time of edgeEntry plus number of minutes if flag is equal to 0.
     Returns the maximum time of edgeEntry minus number of minutes if flag is not equal to 0.
        Parameters
        ----------
        edgeEntry : list of str
            the edge of entries.

        option : int
            minutes to be added or subtracted to edgeEntry time.

        flag : int
            determine the time control type.

        """

    # split first string in edge entry (the time) into hours, minutes, seconds. And make timedelta from them
    edgeEntry = edgeEntry[0].split(":")
    controlTime = dt.timedelta(hours=float(edgeEntry[0]), minutes=float(edgeEntry[1]),
                               seconds=float(edgeEntry[2]))

    # add the control minutes depending on flag. And return the result
    if flag == 0:
        controlTime = controlTime + dt.timedelta(minutes=option)
    else:
        controlTime = controlTime - dt.timedelta(minutes=option)

    return controlTime


def file_name_check(files, courseName):
    """Returns a list with only files from our specific course name.
            Parameters
            ----------
            files : list of str
                files names.

            courseName: str
                name of the course.
            """

    # a loop to remove files from different courses than what we are working on
    for f in files:
        fileName = f.split('\\')
        fileName = fileName[-1].split('-')
        if fileName[0] != courseName:
            files.remove(f)
            f -= 1

    return files


def attendance_report(linuxData, outFolder):
    """Takes a course object that has a list of students in it. Then read some attendance data csv files
     and make a report showing each student with his attendance or not in every lecture time. If someone
     attended the class without being a formal student in the course he will be directed to a nonvalid report
            Parameters
            ----------
            linuxData : ENCS3130
                the course object to be used as a data.

            outFolder: str
                path to output folder
            """

    # making new folders to store outputs in
    attendReports = make_directory(f"{outFolder}\\Attendance Reports")
    attendReportsNV = make_directory(f"{outFolder}\\Attendance Reports NV")

    # making a list of files inside attendance report destination that ends with AR.csv and has course name
    files = glob.glob(f"{str(options.Ar_sheet)}\\*AR.csv")
    files = file_name_check(files, linuxData.get_courseName())
    dateOfLecture = []
    for f in files:
        date = f.split('\\')
        dateOfLecture.append(date[1][-17:-7])

    # invalid attendance will go in this list
    invalid = []

    numberOfFiles = len(files)  # will be used in later compares
    minimum_duration = int(options.P)  # minimum duration allowed to be considered as attended

    # looping on all students registered in the course to check their state
    index = -1
    count = 0
    for k in linuxData.get_studentsList():
        index += 1
        for f in files:
            csvFile = pd.read_csv(f)
            j = 0
            count += 1
            absentFlag = 0
            for _ in csvFile.values:
                if j <= len(csvFile):
                    flag = 0
                    flag3 = 0

                    # reading name and duration and id number if available
                    regex2 = re.compile('[^0-9]')
                    substring = str(csvFile['Name (Original Name)'][j])
                    duration = int(csvFile['Total Duration (Minutes)'][j])
                    checkNumber = regex2.sub('', substring)
                    if checkNumber == '':
                        checkNumber = '0'

                    # taking first and last names of student and make them lower case to compare
                    namesRegex = re.compile('[^a-zA-Z ]')
                    namesRegex = namesRegex.sub('', substring)
                    namesRegex = namesRegex.lower()
                    names = namesRegex.split()
                    if len(names) < 2:
                        names.append('')
                    regex1 = re.compile('[^a-zA-Z ]')
                    name1 = regex1.sub('', k.get_name())
                    name1 = name1.lower()
                    checkName = name1.split()

                    # check using id number
                    if str(k.get_id()) == checkNumber:
                        linux.get_student(index).add_attend('x')
                        absentFlag = -1
                        flag3 = -1

                    # check using the name
                    elif (nltk.edit_distance(names[0], checkName[0]) <= (
                            int(len(checkName[0]) * 0.4)) and (nltk.edit_distance(names[1], checkName[1]) <= (
                            int(len(checkName[1]) * 0.4)) or (nltk.edit_distance(names[1], checkName[2]) <= (
                            int(len(checkName[2]) * 0.4))) or (nltk.edit_distance(names[1], checkName[-1]) <= (
                            int(len(checkName[-1]) * 0.4))))) and absentFlag == 0 and duration > minimum_duration:
                        linux.get_student(index).add_attend('x')
                        absentFlag = -1
                        flag3 = -1
                    if flag3 == 0:
                        for st in linuxData.get_studentsList():
                            checkName = st.get_name().split()
                            checkName[-1] = checkName[-1].lower()
                            if nltk.edit_distance(checkName[-1], names[1]) <= (
                                    int(len(checkName[-1]) * 0.4)) or checkNumber == str(st.get_id()):
                                flag = -1
                                break

                        # check for invalid students
                    if flag != -1 and flag3 != -1 and count <= numberOfFiles:
                        fullname = names[0] + " " + names[1] + "," + str(duration)
                        invalid.append(fullname.split(","))
                j = j + 1

            # make Non Valid report
            if count <= numberOfFiles:
                filename = f"{course_name}-{dateOfLecture[count - 1]}-AR-NV.csv"
                header = ("Name (Original Name)", "Total Duration (Minutes)")
                with open(f"{attendReportsNV}\\{filename}", 'w', newline='') as f:
                    write = csv.writer(f)
                    write.writerow(header)
                    write.writerows(invalid)
                invalid.clear()

            # check if absent flag did not change, which means student is absent we add 'a' to his record
            if absentFlag == 0:
                linux.get_student(index).add_attend('a')

    # making final attendance report
    # column represent the header
    column = ["Student ID", "Student Name"]
    # adding dates to header column
    for dateX in dateOfLecture:
        column.append(dateX)

    # making final array of students records and put it in final report
    attendReportArray = []
    for v in linux.get_studentsList():
        attendReportArray.append(v.toArray())

    reportAR = pd.DataFrame(attendReportArray, columns=column)
    reportAR.to_csv(f"{attendReports}\\{course_name}-AR.csv", index=False)
    return


def participation_report(linuxData, outFolder):
    """Takes a course object that has a list of students in it. Then read some participation data txt files
    and make a report showing each student with his number of participations in every lecture time. If someone
    the class without being a formal student in the course he will be directed to a nonvalid report.
                Parameters
                ----------
                linuxData : ENCS3130
                    the course object to be used as a data.

                outFolder: str
                    the path to output folder.
                """

    # making new folders to store outputs in
    participReports = make_directory(f"{outFolder}\\Participation Reports")
    participReportsNV = make_directory(f"{outFolder}\\Participation Reports NV")

    # making a list of files inside attendance report destination that ends with AR.csv and has course name
    files = glob.glob(f"{str(options.Pr_sheet)}\\*PR.txt")
    files = file_name_check(files, linuxData.get_courseName())

    message = ""
    count = 0
    dateOfLecture = []
    students_Participation_NV = []

    for f in files:
        date = f.split('\\')
        dateOfLecture.append(date[1][-17:-7])

    numberOfFiles = len(files)
    index = -1
    for k in linuxData.get_studentsList():
        index += 1
        for txt in files:
            counter = 0
            count += 1
            contents = open(txt, encoding="utf-8")
            lineList = contents.readlines()
            x = len(lineList) - 1
            while x >= 0:
                if not re.match(r"^[0-9]{2}:[0-9]*", lineList[x]):
                    lineList[x - 1] = ''.join([lineList[x - 1], lineList[x]])
                    lineList.remove(lineList[x])
                x = x - 1

            firstTime = time_control(lineList[0].split(" "), option=options.Tb, flag=0)
            lastTime = time_control(lineList[-1].split(" "), option=options.Te, flag=1)

            contents = open(txt, encoding="utf-8")
            line = contents.readline().strip("\n")
            while True:
                Nv_line = line
                flag3 = 0
                if line.find("From") >= 0 and line.find("to") >= 0:
                    flag = -1
                    flag44 = 0
                    start = line.find("From") + len("From")
                    end = line.find("to")
                    substring = line[start:end]
                    name_of_student = substring
                    time = line.split(" ")
                    time = time[0].split(":")
                    messageTime = dt.timedelta(hours=float(time[0]), minutes=float(time[1]),
                                               seconds=float(time[2]))
                    reseiver = line.split("to")
                    reseiver = reseiver[1].split(":")
                    for i in range(len(reseiver[1:])):
                        if len(reseiver[1:]) >= 2:
                            message += reseiver[i + 1] + ":"
                            flag = 1
                        else:
                            message += reseiver[i + 1]
                    if flag == 1:
                        message = message[:-1]
                    regex = re.compile('[^a-zA-Z ]')
                    regex1 = re.compile('[^a-zA-Z ]')
                    regex2 = re.compile('[^0-9]')
                    regex = regex.sub('', name_of_student.strip("\n"))
                    names1 = regex.split()
                    names1[0] = names1[0].lower()
                    names1[-1] = names1[-1].lower()
                    fullname = regex1.sub('', k.get_name())
                    fullname = fullname.lower()
                    fullname = fullname.split()
                    checkNumber = regex2.sub('', name_of_student.strip("\n"))
                    if checkNumber == '':
                        checkNumber = '0'
                    if str(k.get_id()) == checkNumber or (nltk.edit_distance(names1[0], fullname[0]) <= (
                            int(len(fullname[0]) * 0.4)) and (nltk.edit_distance(names1[-1], fullname[-1]) <= (
                            int(len(fullname[-1]) * 0.4)) or nltk.edit_distance(names1[-1], fullname[1]) <= (
                                                                      int(len(
                                                                          fullname[1]) * 0.4)) or nltk.edit_distance(
                        names1[-1], fullname[2]) <= (
                                                                      int(len(fullname[2]) * 0.4)))):

                        if firstTime <= messageTime <= lastTime:
                            linux.get_student(index).add_participate()
                            counter += 1
                            flag3 = -1

                    if flag3 == 0:
                        for student in linuxData.get_studentsList():
                            checkname = student.get_name().split()
                            checkname[-1] = checkname[-1].lower()
                            if nltk.edit_distance(checkname[-1], names1[-1]) <= (
                                    int(len(checkname[-1]) * 0.4)) or checkNumber == str(student.get_id()):
                                flag44 = -1
                                break
                        if flag44 != -1 and flag3 != -1 and count <= numberOfFiles:
                            students_Participation_NV.append(Nv_line.strip().strip("\n").split(": "))
                line = contents.readline().strip("\n")
                if line.find("From") < 0 and line.find("to") < 0:
                    message = line.rstrip("\n") + message
                if not line:
                    break
                message = ""
            if count <= numberOfFiles:
                filename = f"{course_name}-{dateOfLecture[count - 1]}-PR-NV.txt"
                with open(f"{participReportsNV}\\{filename}", 'w', encoding="utf-8", newline='') as f:
                    write = csv.writer(f, delimiter=' ')
                    write.writerows(students_Participation_NV)
                f.close()
                students_Participation_NV.clear()
            linux.get_student(index).set_final_participate()

    column = ["Student ID", "Student Name"]
    for dateX in dateOfLecture:
        column.append(dateX)

    participReportArray = []
    for v in linux.get_studentsList():
        participReportArray.append(v.toArray2())

    reportAR = pd.DataFrame(participReportArray, columns=column)
    reportAR.to_csv(f"{participReports}\\{course_name}-PR.csv", index=False)
    return


if __name__ == '__main__':
    # making output files directory
    outputFolder = make_directory(str(options.out_sheet))

    linux = ENCS3130()  # make a new linux course object
    name = str(options.List_sheet)
    course_name = name.split('-')
    course_name = course_name[0]
    new_path = pd.read_csv(str(name))
    df = pd.DataFrame()
    for i in range(len(new_path)):
        linux.add_student(Student((int(new_path['Student ID'][i])), str(new_path[' Student Name'][i])))
    attendance_report(linux, outputFolder)
    participation_report(linux, outputFolder)
    print("Thank you all Result in files !")
