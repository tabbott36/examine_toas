'''For every MPTA pulsar, scan their data directories for observations in the specified band and compile a dictionary of observation parameters for each.'''

import os 
import json # to save the results
import re # to parse the header file


def generate_obs_dict(psrs, band):
    '''
    Generate a dictionary of observations for each pulsar.
    
    Parameters:
    -----------
    psrs : list
        List of pulsar names to scan for MeerKAT observations.
    band : str
        Observing band to filter for. Either "UHF" or "L-band".

    Returns:
    --------
    obs_dict : dict
        Dictionary where keys are pulsar names and values are dictionaries of observation dates and parameters.
        
    '''
    
    # convert band to a frequency (rounded to nearest int): 
    band_dict = {"UHF" : 815, "L-band" : 1283}

    obs_dict = {}
    progress = 0
    for psr in psrs:
        # verify the pulsar data directory exists
        parent_dir = "/fred/oz005/timing_processed/"
        psr_dir = os.path.join(parent_dir, psr)
        if not os.path.exists(psr_dir):
            raise FileNotFoundError(f"Pulsar {psr} cannot be found at {psr_dir}!")
        # scan each directory within the pulsar's data directory
        obs_for_psr = {}          
        obs_dates = [dir for dir in os.listdir(psr_dir) if dir[0:2]=="20"]
        for obs_date in obs_dates:
            obs_path = os.path.join(psr_dir, obs_date)
            # find all subdirs within an observation (should be /1/, /2/, /3/, or /4/ with all the data inside (header, TOAs, decimated archives, etc))
            # I'm just doing this because I want to be sure there is a header file (to determine the observing band)
            subdirs = []
            for root, dirs, files in os.walk(obs_path):
                for dir_name in dirs:
                    subdirs.append(os.path.join(root, dir_name))
            # pinpoint the header location
            header_location = None
            for subdir in subdirs:
                header_path = os.path.join(subdir, "obs.header")
                if os.path.exists(header_path):
                    header_location = header_path
            # if the header exists, read it to determine the observing band
            if header_location:
                with open(header_location, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("FREQ"):
                            # Use regex to extract the frequency number
                            freq_match = re.search(r'FREQ\s+(\d+\.\d+)', line)
                            obs_freq = float(freq_match.group(1))
                            if int(obs_freq) == int(band_dict[band]): # done because the freq can vary by ~0.1 MHz, so just match the integer part
                                print(f"Found {band} observation for {psr} on {obs_date} at frequency {obs_freq} MHz.")
                                data_path = os.path.dirname(header_location)
                                obs_for_psr[obs_date] = [data_path] # making it a list in case we want to add more obs details later 
                                
                                # also grab the observation length (to be used as a weight in the timing analysis)
                                psrstat_cmd = f'psrstat -c "length" {data_path}/*_zap.ar'
                                # output should look like: J2222-0137_2025-03-22-08:56:09_zap.ar length=248
                                # grab the value after "length="
                                psrstat_output = os.popen(psrstat_cmd).read()
                                length_match = re.search(r'length=(\d+)', psrstat_output)
                                if length_match:
                                    obs_length = int(length_match.group(1))
                                    obs_for_psr[obs_date].append(obs_length)
                                else: 
                                    raise ValueError(f"Could not extract observation length from psrstat output for {psr} on {obs_date}!")                     
            # if the header does not exist, we have a problem!
            else: 
                raise FileNotFoundError(f"Pulsar {psr} header file not found in observation {obs_date}!")
            # update the obs_dict if we found any observations for this pulsar in the given band              
            obs_dict[psr] = obs_for_psr
        # update the progress bar
        progress += 1
        print(f"Processing {psr} ({progress}/{len(psrs)})")
    with open(f"{band}_obs_dict.json", "w") as json_file:
        json.dump(obs_dict, json_file, indent=4)
        
    return obs_dict