'''This script run tempo2 pulsar software on the .tim and .par files to generate timing residuals and DM measurements'''

#### NOTE You may have to run: export TEMPO2=/fred/oz005/tabbott/utils/T2runtime ####

import os
import subprocess

def run_tempo2(
    band, 
    nchans,
    tim_file,
    parfile,
    fit,
    nobs = 30000,
    nofit = True, 
    plot = False,
    save_output = False,
    ):
    '''
    This function runs tempo2 on the provided .tim and .par files to generate timing residuals and DM measurements.
    
    Parameters:
    -----------
    band : str
        The observing band (e.g., "L-band", "UHF").
    nchans : int
        The number of channels (e.g., 4, 8, 16, 32).
    parfile : str
        Path to the .par file for the pulsar.
    tim_file : str
        Path to the .tim file for the pulsar.
    nobs : int
        Maximum number of observations per pulsar to process. Default is 30000.
    fit : str
        Parameter to fit for.
    nofit : bool
        If True, disable all fit parameters except those specified in 'fit'.
    plot : bool
        If True, generate plots of the timing residuals. Default is False.
    save_output : bool
        If True, save the tempo2 output to a text file for each pulsar. Default is False.
    
    Returns:
    --------
    None
    '''
        
    # Create the tempo2 command and return the terminal output
    tempo2_cmd = f"tempo2 -f {parfile} {tim_file}"
    if nofit:
        tempo2_cmd += " -nofit"
    if fit:
        tempo2_cmd += f" -fit {fit}"
    if nobs:
        tempo2_cmd += f" -nobs {nobs}"
    if plot:
        tempo2_cmd += " -gr plk"
        
    print(f"Running command: {tempo2_cmd}")
    process = subprocess.Popen(tempo2_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if save_output:
        # save the output to a text file
        output_file = f'/fred/oz005/tabbott/examine_toas/tempo2_output/{os.path.basename(tim_file).replace(".tim", "")}_{nchans}ch_{band}_tempo2_output.txt'
        with open(output_file, 'w') as f:
            f.write(stdout.decode())
            f.write('\n')
            f.write(stderr.decode())
            f.write('\n')
            f.write(f'.tim file: {tim_file}')
        print(f"Saved tempo2 output for {os.path.basename(tim_file).replace('.tim', '')} to {output_file}")
    
    return stdout.decode(), stderr.decode()