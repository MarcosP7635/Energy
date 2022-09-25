#Import a dictionary of MTs to know what data to download
using CSV, DataFrames, Downloads
MT_df = CSV.read("/content/MT_dict.csv", DataFrame, 
                 stringtype=String)
MT_dict = Dict([])
rows, cols = size(MT_df)
for row in 1:rows
  MT_df[row, 2] = String(MT_df[row, 2][2:end-1])
  MTs = [parse(Int64, n) for n in split(MT_df[row, 2], ",")]
  for MT in MTs
      MT_dict[MT] = MT_df[row, 1] 
  end
end
MT_list = [k for k in keys(MT_dict)]
nuclide_df = CSV.read("/content/df_list.csv", DataFrame, 
                 stringtype=String)
#This function gives an exact output for each datum
function read_rational_num(input_str)
    coeff, oom = split(input_str, "E")
    return parse(Float64, coeff) * Rational(10)^parse(Float64, oom)
end
#This function gives the mass and chemical symbol for each isotope
function get_mass_name(nuclide)
    index = 1
    while (tryparse(Int64, string(nuclide[index])) != nothing && index <= length(nuclide))
        index += 1
    end
    mass = tryparse(Int64, nuclide[1:index-1])
    name =  nuclide[index:end]
    name_1 = uppercase(name[1])
    if (length(name) > 1)
        name = name_1 * name[2]
    else 
      name = name_1
    end
    return mass, name
end
#This function gives the mass and chemical symbol for each isotope
function read_tendl_file(file_path)
    file_as_vector = readlines(file_path)
    reaction = split(file_as_vector[1], " ", keepempty = false)[end]
    authors = split(file_as_vector[2], " ", keepempty = false)[3]
    energies = split(file_as_vector[4], " ", keepempty = false)[end]
    energies = parse(Int64, energies)
    x_axis_label, y_axis_label = split(file_as_vector[5], " ", keepempty = false)[2:end]
    x_vals, y_vals = Vector{Float64}(undef, energies), Vector{Float64}(undef, energies)
    for row in 1:energies
        strs = split(file_as_vector[5+row], " ", keepempty=false)
        x_vals[row], y_vals[row] = read_rational_num(strs[1]), read_rational_num(strs[2]) 
    end
    return x_vals, y_vals, x_axis_label, y_axis_label, authors, reaction
end
#This function downloads and reads the data fro a given reaction
function tendl_data_from_url(elem, mass, projectile, mt)
    zero_filled_mass = lpad(string(mass), 3, "0")
    url = "https://www-nds.iaea.org/dataexplorer/libraries/" * projectile * "/" 
    url = url * elem * zero_filled_mass * "/tendl.2019/tables/xs/" * projectile * "-"
    url = url * elem * zero_filled_mass * "-MT" * lpad(string(mt), 3, "0") * ".tendl.2019"
    return read_tendl_file(Downloads.download(url))
end
projectile = "n"
for nuclide in nuclide_df[1:end, 1]
  mass, elem = get_mass_name(nuclide)
  for mt in MT_list
    try 
      x_vals, y_vals, x_axis_label, y_axis_label, authors, reaction = tendl_data_from_url(elem, mass, projectile, mt)
      df = DataFrame()
      df[!, x_axis_label] = x_vals
      df[!, y_axis_label] = y_vals
      mt_str, mass_str = lpad(string(mt), 3, "0"), lpad(string(mass), 3, "0")
      file_path = projectile * "-" * elem * mass_str * "-" * "MT" * mt_str * ".csv"
      CSV.write(file_path, df)
      println("nuclide = ", mass, elem, " MT = ", mt, " worked :)")
    catch 
      println("nuclide = ", mass, elem, " MT = ", mt, " did not work")
    end
  end
end