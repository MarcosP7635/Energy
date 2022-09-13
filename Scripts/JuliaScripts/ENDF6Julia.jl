# Reference: https://github.com/DavidWalz/pyENDF6

slices = Dict(
    "MAT" => 67:71,
    "MF" => 72:74,
    "MT" => 75:78,
    "line" => 78:83,
    "content" => 1:67,
    "data" => [a-10:a for a in 11*collect(1:6)])


function read_float(v)
    #Convert ENDF6 string to float 
    a, b = [' '], "" 
    if (strip(v, a) == b)
        return 0.
    end
    try
        return parse(BigFloat, v)
    catch
        # ENDF6 may omit the e for exponent
        return parse(BigFloat,
            v[1] * replace(replace(v[2:end], "+" => "e+"), "-" => "e-"))  # don't replace leading negative sign
    end
end  

function read_line(l)
    #Read first 6*11 characters of a line as floats"""
    return [read_float(l[s]) for s in slices["data"]]
end
 
function read_table(lines)
    #=
    Parse tabulated data in a section
    https://t2.lanl.gov/nis/endf/intro07.html
    https://t2.lanl.gov/nis/endf/intro08.html
    https://t2.lanl.gov/nis/endf/intro09.html
    =#
    # header line 1: (100*Z+A), mass in [m_neutron]
    # [MAT, 3, MT/ ZA, AWR, 0, 0, 0, 0] HEAD

    # header line 2: Q-value and some counts
    # [MAT, 3, MT/ QM, QI, 0, LR, NR, NP/ EINT/ S(E)] TAB1
    f = read_line(lines[2])
    nS = Int64(f[5])  # number of interpolation sections
    nP = Int64(f[6])  # number of data points
    # header line 3: interpolation information
    # [MAT, 3, 0/ 0.0, 0.0, 0, 0, 0, 0] SEND
    # 1   y is constant in x (constant, histogram)
    # 2   y is linear in x (linear-linear)
    # 3   y is linear in ln(x) (linear-log)
    # 4   ln(y) is linear in x (log-linear)
    # 5   ln(y) is linear in ln(x) (log-log)
    # 6   y obeys a Gamow charged-particle penetrability law

    # data lines
    energy = []
    cross_section = []
    for l in lines[4:end]
        f = read_line(l)
        append!(energy, f[1], f[3], f[5])
        append!(cross_section, f[2], f[4], f[6])
    end
    return energy[1:nP], cross_section[1:nP]
end 

function find_section(lines, MF, MT)
    #"""Locate and return a certain section"""
    v = [l[71:75] for l in lines]
    cmpstr = "$(@sprintf("%2s", MF))$(@sprintf("%3s", MT))" # search string
    i0 = collect(findfirst(==(cmpstr), v))[1] # first occurrence
    i1 = collect(findlast(==(cmpstr), v))[1] # last occurrence
    return lines[i0: i1]
end