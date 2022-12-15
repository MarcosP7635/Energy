import subprocess
running_on_colab = not "JupyterNotebooks" in subprocess.os.getcwd()
if running_on_colab:
    running_on_colab = True
    parent_dir, export_data_dir, import_data_dir = "/content/", "/content/", "/content/"
else:
    parent_dir = subprocess.os.getcwd().split("JupyterNotebooks")[0]
    sep_char = parent_dir.split("Energy")[-1]
    import_data_dir =  parent_dir + "ImportedData" + sep_char 
    export_data_dir =  parent_dir + "ExportedData" + sep_char
print(parent_dir, import_data_dir, export_data_dir)
