# -*- coding: utf-8 -*-
"""read_exfor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1l3z5lEE7I6krVknNYGJ9COIYWyvn035A
"""

using Unitful #https://painterqubits.github.io/Unitful.jl/stable/
#quantity * @u_str("unit abbreviation") 
using Symbolics #https://symbolics.juliasymbolics.org/dev/
#cite https://doi.org/10.48550/arXiv.2105.03949
using Latexify
using Test
#1 * @u_str("mA") is 1 milliamp
using CSV, DataFrames
using PlotlyJS
using SymPy
using Interpolations
using Plots
using Interact
using Statistics
using PyCall
#plotlyjs()
data_dir = "C:\\Cross-Section-Data\\EXFOR\\"

"""#Design

    Looping check_line() through each line in the file detects where each dataset begins. 

    Reading the line above each output of check_line() gives the number of rows in each dataset.

    make_spacing_dict() gets the names of the columns and the instructions for how to read each dataset.

    read_dataset() reads each and constructs a dictionary from each dataset.
    
    read_exfor_file() runs all of the above in order to return a single DataFrame of all the data stored at a given file path.
     
"""

replace("Refer (YY)", " " => "", "(" => "", ")" => "")

function check_line(line, start)
    if length(line) > length(start) - 1
        return (line[1:length(start)] == start)
    end
    return false
end

function make_spacing_dict(line1, line2)
    spacing_ends = [collect(out)[1] for out in findall(">", line2)]
    spacing_starts = append!([1], [collect(out)[1] for out in findall("<", line2)])
    #Find where some of the spacings begin and end based on the arrows
    if length(spacing_ends) != length(spacing_starts)
        print("Error: improper formatting")
        return 
    end
    indices_with_gaps = [index for index in  1:length(spacing_ends)-1 if 
                    spacing_ends[index] != spacing_starts[index+1]-1]
    #Some of the spacings are instead denoted by the letter o instead of arrows
    missing_spacings = [spacing_ends[index]+1:spacing_starts[index+1]-1 for index in indices_with_gaps]
    spacings = append!(missing_spacings, 
    [spacing_starts[i]:spacing_ends[i] for i in 1:length(spacing_ends)])
    spacing_dict = Dict([])
    replace_dict = 
    #Make a dictionary where the keys are name for each column and the values are the indices of the columns
    spacing_names = [spacing_dict[replace(strip(line1[spacing], [' ', '#']),
                     " " => "", "(" => "", ")" => "")] = 
                        spacing for spacing in spacings]
    return spacing_dict
end

function read_datum(datum)
    #Reads a single datum from a line of data
    datum = strip(datum, [' '])
    out = tryparse(Float64, datum)
    if out == nothing
        return datum 
    end
    return out
end

function check_spacings(file_path)
    #Reads an EXFOR file and returns a dictionary of data
    file_as_vector = readlines(file_path)
    spacing_specifiers = [index for index in 1:length(file_as_vector) 
                        if check_line(file_as_vector[index], "# Prj")]
    if spacing_specifiers == []
        print("Error: no data found")
        return
    end
    list_spacing_dict = [make_spacing_dict(file_as_vector[spacing_specifier], 
                                            file_as_vector[spacing_specifier+1])
                        for spacing_specifier in spacing_specifiers]
    #check if the spacing dicts are the same
    for index in 2:length(spacing_specifiers)
        if list_spacing_dict[index] != list_spacing_dict[1]
            return false
        end
    end
    return true
end

subdirs = [content * "\\" for content in readdir(data_dir) if isdir(data_dir * "\\" * content)]
for subdir in subdirs
    files = readdir(data_dir * subdir)
    test = [check_spacings(data_dir * subdir * file) for file in files]
    println("It is ", all(test),
     " that the spacings in each file are all self consistent for the subdirectory ", subdir)
end

"""So I only need to retrieve the spacings of the data once for each file. """

function get_MT(spacing_specifier, file_as_vector)
    for lines_above in 1:10
        if file_as_vector[spacing_specifier - lines_above][1:3] == "#MT"
            return tryparse(Int64, 
                    file_as_vector[spacing_specifier - lines_above][4:end])
        end
    end
    return nothing 
end

function read_exfor_file(file_path, filter_by_MTs = false, MTs=[])
    #Reads an EXFOR file and returns a dictionary of data
    file_as_vector = readlines(file_path)
    if filter_by_MTs
        spacing_specifiers = [index for index in 1:length(file_as_vector) 
                            if check_line(file_as_vector[index], "# Prj")
                                && get_MT(index, file_as_vector) in MTs]
    else
        spacing_specifiers = [index for index in 1:length(file_as_vector) 
                            if check_line(file_as_vector[index], "# Prj")]
    end
    #The MT line doesn't have a fixed location but is generally < 10 lines above the spacing specifier
    if spacing_specifiers == []
        print("Error: no data found")
        return
    end
    dataset_rows = [tryparse(Int64, split(file_as_vector[index - 1], [' '])[end])
                            for index in spacing_specifiers]
    #Each dataset should have the same column names
    spacing_dict = make_spacing_dict(file_as_vector[spacing_specifiers[1]], 
                    file_as_vector[spacing_specifiers[1] + 1])
    #make an empty dataframe to fill up with the data
    df = DataFrame([Vector{Union{Missing, Float64, String, SubString{String}}}(
                missing, sum(dataset_rows)) 
                   for _ in 1:length(keys(spacing_dict))], 
                   [key for key in keys(spacing_dict)])
    #make a nested vector, then flatten it to populate the dataframe.
    _ = [df[:,key] = collect(Iterators.flatten([[read_datum(
                    file_as_vector[line_num][spacing_dict[key]]) 
                    for line_num in spacing_specifiers[index] + 2: 
                            spacing_specifiers[index] + 1 + dataset_rows[index]]
                            for index in 1:length(spacing_specifiers)]))
                    for key in keys(spacing_dict)]           
    return df
end

boron_df = read_exfor_file(data_dir * "gammas\\005_B_010.c4", true, [103])

function read_irregular_datum(datum, symbol)
    if typeof(datum) == Float64
        return datum
    end
    arr = split(datum, symbol)
    if symbol == "-"
        return parse(Float64, arr[1]) / 10^parse(Int64, arr[2])
    elseif symbol == "+"
        return parse(Float64, arr[1]) * 10^parse(Int64, arr[2])
    end
end
boron_df[!,"Data"] = [read_irregular_datum(element, "-") for element in boron_df[!,"Data"]]
boron_df[!,"Energy"] = [read_irregular_datum(element, "+") for element in boron_df[!,"Energy"]]
fig = PlotlyJS.plot(boron_df, x=:Energy, y=:Data, color=:MT, text=:ReferYY,
                mode="markers", Layout(yaxis_type="log", xaxis_type="log"))

"""Click the legend to view different MTs :) """

file_path = data_dir * "neutrons\\092_U_238.c4"
df = read_exfor_file(file_path, [1, 2, 102])
fig = PlotlyJS.plot(df, x=:Energy, y=:Data, color=:MT, text=:ReferYY,
                mode="markers", Layout(yaxis_type="log", xaxis_type="log"))

fig.show()

"""Why are these extra MTs here? """

function upload_plot(fig, plot_name)
    open("./" * plot_name * ".html", "w") do io

        PlotlyBase.to_html(io, fig.plot)

    end
end

upload_plot(fig, "example")

"""Write script that adds the correct URL in urls.py, makes a new entry to the list on index.html, and a function views.py to render the plot. 
Or just write a script that adds it to the Github pages repo :)

https://marcosp7635.github.io/plots/neutrons_U238.html

https://interactive-data-mp7635.herokuapp.com/neutrons-U238
"""