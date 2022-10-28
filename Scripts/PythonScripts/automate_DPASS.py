'''
Note that this must be executed from the same directory as the DPASS files.
'''
from automate_local_typing import *
if __name__ == '__main__':
    output_dir = "C:\\Users\\engin\\Documents\\GitHub\\Energy\\ImportedData\\DPASS_Output"
    images_dir = "C:\\Users\engin\\Downloads\\DPASS_icons"
    program_path = ["C:\\Users\\engin\\Downloads\\DPASS2106\\DPASS2106\\DPASS.exe"]
    pool = Pool(processes=3)              # start 4 worker processes
    result = pool.apply_async(os.system, program_path)
    result2 = pool.apply_async(find_image_centers, (images_dir, output_dir))    
    #will overwrite existing files if any name conflicts
    result2.get()    #run the function asynchronously
    result.get()                  

