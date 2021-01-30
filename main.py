import requests
import numpy as np
import time
from openpyxl import Workbook
import xlsxwriter
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

START_YEAR = 1981
START_SEASON = 1  # winter=1,...,fall=4

END_YEAR = 2021
END_SEASON = 1

FIG_WIDTH = 25.6  # 2560x720
FIG_HEIGHT = 9.0


def season_picker(loop_number):
    if loop_number % 4 == 0:
        return "winter"
    if loop_number % 4 == 1:
        return "spring"
    if loop_number % 4 == 2:
        return "summer"
    if loop_number % 4 == 3:
        return "fall"


def round_up_to_nearest_power_of_ten(num, pow):
    return np.ceil(num/(10**pow))*(10**pow)


def digit_amount(num):
    return len(str(abs(num)))


def add_new_entry(i, year, type, response, entries_list, score_list, above_8, below_6):
    new_entry_list = []
    if type == "Season":
        new_entry_list.append(i + 1)
        new_entry_list.append(response["season_name"] + " " + str(response["season_year"]))
        print(sorted(score_list, reverse=True))
    if type == "Year":
        new_entry_list.append(str(int(year) - 1))
    if type == "Decade":
        new_entry_list.append(str(int(round_up_to_nearest_power_of_ten(int(year) - 11), 1)) + "s")

    new_entry_list.append(np.round(np.mean(score_list), 3))

    score_list_length = len(score_list)
    new_entry_list.append(score_list_length)

    new_entry_list.append(above_8)
    new_entry_list.append(np.round((above_8 / score_list_length * 100), 2))

    new_entry_list.append(below_6)
    new_entry_list.append(np.round((below_6 / score_list_length * 100), 2))

    entries_list.append(new_entry_list)
    print(new_entry_list)
    return entries_list


def xlsx_to_chart_list(xlsx):
    seasons_chart = pd.read_excel(xlsx, 'Seasons').drop("Index", axis=1)
    years_chart = pd.read_excel(xlsx, 'Years')
    decades_chart = pd.read_excel(xlsx, 'Decades')
    df_list = [seasons_chart, years_chart, decades_chart]
    return df_list


def create_graphs(xlsx):
    chart_list = xlsx_to_chart_list(xlsx)
    for chart in chart_list:
        create_mean_score_graphs(chart)
        create_total_shows_graphs(chart)


def create_mean_score_graphs(chart):
    x_axis=chart.iloc[:,0]

    chart_scores=chart["Mean Score"]

    plt.figure(2,figsize=(FIG_WIDTH, FIG_HEIGHT))
    p1 = plt.bar(x_axis, chart_scores, color=["#98F5FF", "#00CFE6"])

    graph_title = "Mean Score (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize' : 20})

    xlocs, xlabs = plt.xticks()
    plt.xticks(x_axis, fontsize=7, rotation=90)

    for i, v in enumerate(chart_scores):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 6}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")
    plt.ylim(6.25, 7.45)
    plt.yticks(np.arange(6.25, 7.45, 0.1))

    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()


def create_total_shows_graphs(chart):
    x_axis=chart.iloc[:,0]

    low_score_shows=chart["6.00- shows"]
    low_score_percent = chart ["6.00- %"]
    mid_score_shows=chart["Total Shows"] - chart["8.00+ shows"] - chart["6.00- shows"]
    mid_score_percent= 100 - chart["8.00+ %"] - chart["6.00- %"]
    high_score_shows=chart["8.00+ shows"]
    high_score_percent=chart["8.00+ %"]
    total_shows = chart["Total Shows"]

    plt.figure(3,figsize=(FIG_WIDTH, FIG_HEIGHT))

    p1 = plt.bar(x_axis, total_shows, color="#007fff")
    p2 = plt.bar(x_axis, low_score_shows + mid_score_shows, color="green")
    p3 = plt.bar(x_axis, low_score_shows, color="#FF1919")

    graph_title = "Total Shows - Amount (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize' : 20})

    xlocs, xlabs = plt.xticks()
    print(x_axis)
    plt.xticks(x_axis, fontsize=7, rotation=90)

    for i, v in enumerate(total_shows):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 8}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")

    plt.yticks(np.arange(0, 1.05* max(total_shows), round_up_to_nearest_power_of_ten(max(total_shows)/20,digit_amount(max(total_shows))-2)))

    blue_patch = mpatches.Patch(color='#007fff', label='8.00+ shows')
    green_patch = mpatches.Patch(color="green", label='6.00 - 8.00 shows')
    red_patch = mpatches.Patch(color="#FF1919", label="6.00- shows")
    plt.legend(handles=[red_patch, green_patch, blue_patch])

    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()

    plt.figure(4, figsize=(FIG_WIDTH, FIG_HEIGHT))

    p1 = plt.bar(x_axis, 100, color="#007fff")
    p2 = plt.bar(x_axis, low_score_percent + mid_score_percent, color="green")
    p3 = plt.bar(x_axis, low_score_percent, color="#FF1919")

    graph_title = "Total Shows - Percentage Spread (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize': 20})

    plt.xticks(x_axis,fontsize=7, rotation=90)
    plt.yticks(np.arange(0, 101, 5))

    plt.legend(handles=[red_patch, green_patch, blue_patch])

    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()

    create_low_score_graphs(x_axis, low_score_shows, low_score_percent, chart)
    create_high_score_graphs(x_axis, high_score_shows, high_score_percent, chart)


def create_low_score_graphs(x_axis, low_score_shows, low_score_percent, chart):
    plt.figure(5, figsize=(FIG_WIDTH, FIG_HEIGHT))
    print(x_axis)

    print(round_up_to_nearest_power_of_ten(max(low_score_shows)/20,digit_amount(max(low_score_shows))-1))
    plt.yticks(np.arange(0, 1.05 * max(low_score_shows), round_up_to_nearest_power_of_ten(max(low_score_shows)/20,digit_amount(max(low_score_shows))-2)))

    p1=plt.bar(x_axis, low_score_shows, color=["#FF1919", "#DD0707"])

    plt.xticks(x_axis, fontsize=7, rotation=90)
    graph_title = "Amount of shows under 6.00 (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize' : 20})
    plt.grid(axis='y')

    xlocs, xlabs = plt.xticks()

    for i, v in enumerate(low_score_shows):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 8}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()

    plt.figure(6, figsize=(FIG_WIDTH, FIG_HEIGHT))

    p1 = plt.bar(x_axis, low_score_percent, color=["#FF1919", "#DD0707"])
    plt.xticks(x_axis, fontsize=7, rotation=90)

    xlocs, xlabs = plt.xticks()

    for i, v in enumerate(low_score_percent):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 8}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")

    graph_title = "Percentage of shows under 6.00 (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize' : 20})
    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()


def create_high_score_graphs(x_axis, high_score_shows, high_score_percent, chart):
    plt.figure(7, figsize=(FIG_WIDTH, FIG_HEIGHT))
    p1 = plt.bar(x_axis, high_score_shows, color=["#007fff", "#005ddd"])

    plt.xticks(x_axis, fontsize=7, rotation=90)
    plt.yticks(np.arange(0, 1.05 * max(high_score_shows), round_up_to_nearest_power_of_ten(max(high_score_shows) / 20,digit_amount(max(high_score_shows)) - 2)))
    xlocs, xlabs = plt.xticks()

    for i, v in enumerate(high_score_shows):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 8}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")

    graph_title = "Amount of shows above 8.00 (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize' : 20})
    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()

    plt.figure(8, figsize=(FIG_WIDTH, FIG_HEIGHT))

    p1 = plt.bar(x_axis, high_score_percent, color=["#007fff", "#005ddd"])

    plt.xticks(x_axis, fontsize=7, rotation=90)
    #plt.yticks(np.arange(0, 100, 5))
    xlocs, xlabs = plt.xticks()

    for i, v in enumerate(high_score_percent):
        if len(x_axis)>20:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize' : 8}, ha="center")
        else:
            plt.text(p1[i].get_x() + p1[i].get_width()/2.0, v + 0.01, str(v), fontdict={'fontsize': 12}, ha="center")

    graph_title = "Percentage of shows above 8.00 (" + chart.columns[0] + "s)"
    plt.title(graph_title, fontdict={'fontsize': 20})
    plt.grid(axis='y')

    plt.savefig("Graphs/" + graph_title + ".png")
    plt.show()


def create_charts():
    season_headers = ["Index", "Season", "Mean Score", "Total Shows", "8.00+ shows", "8.00+ %", "6.00- shows", "6.00- %"]
    year_headers = ["Year", "Mean Score", "Total Shows", "8.00+ shows", "8.00+ %", "6.00- shows", "6.00- %"]
    decade_headers = ["Decade", "Mean Score", "Total Shows", "8.00+ shows", "8.00+ %", "6.00- shows", "6.00- %"]
    all_time_headers = ["Mean Score", "Total Shows", "8.00+ shows", "8.00+ %", "6.00- shows", "6.00- %"]

    seasons_list = [season_headers]
    years_list = [year_headers]
    decades_list = [decade_headers]
    all_times_list = [all_time_headers]

    years_score_list = []
    decades_score_list = []
    all_time_score_list = []

    year_above_8 = 0
    year_below_6 = 0

    decade_above_8 = 0
    decade_below_6 = 0

    all_time_above_8 = 0
    all_time_below_6 = 0

    loop_amount = (END_YEAR - START_YEAR) * 4 + END_SEASON - START_SEASON

    for i in range(loop_amount + 1):
        time.sleep(5)

        year = str(START_YEAR + int(np.floor(i / 4)))
        season = season_picker(i)
        url = "https://api.jikan.moe/v3/season/" + year + "/" + season

        print(url)
        response = requests.get(url).json()

        score_list = []
        above_8 = 0
        below_6 = 0
        season_list = []

        for anime in response["anime"]:
            if anime["type"] == "TV" and anime["continuing"] == False and anime["kids"] == False:
                score = anime["score"]
                if not score:
                    pass
                else:
                    score_list.append(score)
                    if score <= 6:
                        below_6 += 1
                    else:
                        if score >= 8:
                            above_8 += 1

        if len(score_list) >= 5:
            seasons_list = add_new_entry(i, year, "Season", response, seasons_list, score_list, above_8, below_6)

        if season == "winter" and i != 0:  # This means we moved on to the new year
            years_list = add_new_entry(i, year, "Year", response, years_list, years_score_list, year_above_8, year_below_6)

            year_above_8 = 0
            year_below_6 = 0
            years_score_list = []

            if int(year) % 10 == 1:  # This means we moved on to a new decade (decades count as 81-90, 91-00, etc to include 2020)
                decades_list = add_new_entry(i, year, "Decade", response, decades_list, decades_score_list, decade_above_8, decade_below_6)

                decade_above_8 = 0
                decade_below_6 = 0
                decades_score_list = []

        years_score_list.extend(score_list)
        decades_score_list.extend(score_list)
        all_time_score_list.extend(score_list)

        year_above_8 += above_8
        decade_above_8 += above_8
        all_time_above_8 += above_8

        year_below_6 += below_6
        decade_below_6 += below_6
        all_time_below_6 += below_6

    year = str(int(year) +1)
    years_list = add_new_entry(i, year, "Year", response, years_list, years_score_list, year_above_8, year_below_6)
    decades_list = add_new_entry(i, year, "Decade", response, decades_list, decades_score_list, decade_above_8, decade_below_6)
    all_times_list = add_new_entry(i, year, "AllTime", response, all_times_list, all_time_score_list, all_time_above_8, all_time_below_6)

    with xlsxwriter.Workbook('MALRatings.xlsx') as workbook:
        worksheet = workbook.add_worksheet('Seasons')
        for row_num, data in enumerate(seasons_list):
            worksheet.write_row(row_num, 0, data)

        worksheet = workbook.add_worksheet('Years')
        for row_num, data in enumerate(years_list):
            worksheet.write_row(row_num, 0, data)

        worksheet = workbook.add_worksheet('Decades')
        for row_num, data in enumerate(decades_list):
            worksheet.write_row(row_num, 0, data)

        worksheet = workbook.add_worksheet('AllTime')
        for row_num, data in enumerate(all_times_list):
            worksheet.write_row(row_num, 0, data)


#create_charts()
MALXlsx = pd.ExcelFile('MALRatings.xlsx')
create_graphs(MALXlsx)

