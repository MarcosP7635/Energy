function  read_tendl_file(file_path)
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

function make_tendl_url(elem, mass, projectile, mt)
  zero_filled_mass = lpad(String(mass), "0", 3)
  elem = upper(elem[1]) + elem[2:end]
  url = "https://www-nds.iaea.org/dataexplorer/libraries/" * projectile * "/" 
  url = url * elem * zero_filled_mass * "/tendl.2019/tables/xs/" * projectile * "-"
  url = url * zero_filled_mass * "-MT" * lpad(String(mt), "0", 3) * ".tendl.2019"
  return url
end
