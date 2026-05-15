'''
This script is a bunch of functions to plot results from the timing pipeline. 
'''

import numpy as np
import matplotlib.pyplot as plt
import os

def plot_obs(obs_dict, npsrs=20, band="UHF", save_path="/fred/oz005/tabbott/examine_toas/plots/"):
    '''
    Plot diagnostic plots presenting the observation dictionary.
    
    Parameters
    ----------
    obs_dict : dict
        Dictionary containing observation information for the pulsars.
    npsrs : int
        Number of pulsars to plot in the histogram of most observed pulsars.
    band : str
        The observing band, either 'L-band' or 'UHF'. Default is 'UHF'.
    save_path : str
        Path to save the generated plots. If None, plots will not be saved.
        
    Returns
    -------
    None
    '''
    # plot a histogram of the npsrs pulsars with the largest number of observations
    pulsar_names = []
    num_observations = []
    temp_psr_dict = {}
    for pulsar in obs_dict.keys():
        num_obs = len(obs_dict[pulsar].keys())
        pulsar_names.append(pulsar)
        num_observations.append(num_obs)
        temp_psr_dict[pulsar] = num_obs
        
    # sort the lists
    sorted_indices = sorted(range(len(num_observations)), key=lambda k: num_observations[k], reverse=True)
    pulsar_names = [pulsar_names[i] for i in sorted_indices]
    num_observations = [num_observations[i] for i in sorted_indices]

    # plot the histogram
    plt.figure(figsize=(10, 6))
    plt.bar(pulsar_names[:npsrs], num_observations[:npsrs])
    plt.xlabel('Pulsar Name')
    plt.ylabel('Number of Observations')
    plt.title(f'Top {npsrs} Pulsars by Number of Observations')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.grid()
    if save_path:
        plt.savefig(f'{save_path}{npsrs}_most_obs_{band}_psrs.png')

    # plot a histogram of number of observations per pulsar with bins of size 1
    plt.figure(figsize=(10, 6))
    plt.hist(num_observations, bins=range(min(num_observations), max(num_observations) + 1))
    plt.xlabel('Number of Observations')
    plt.ylabel('Number of Pulsars')
    plt.title('Histogram of Number of Observations per Pulsar')
    plt.tight_layout()
    plt.grid()
    if save_path:
        plt.savefig(f'{save_path}obs_per_psr_{band}.png')

    #sort the temp_psr_dict by alphabetic order 
    temp_psr_dict = dict(sorted(temp_psr_dict.items()))
    for key in temp_psr_dict.keys():
        print(f'{key},{temp_psr_dict[key]}')
        
        
def plot_templates(obs_dict, nchans, band,
    template_dir="/fred/oz005/tabbott/meerkat-timing/templates/8ch_UHF_templates/", 
    save_dir="/fred/oz005/tabbott/examine_toas/plots/"):
    '''Plot the template for a given pulsar and observation date.'''
    for psr in obs_dict:
        # just plot the first observation for each pulsar
        obs = list(obs_dict[psr].keys())[0]
        plot_cmd = f"psrplot -p freq+ -D {save_dir}{psr}_template.png/PNG {template_dir}{psr}_template_{nchans}ch_{band}.stdD"
        print(f"Running: {plot_cmd}")
        os.system(plot_cmd)


def plot_toas(obs_dict, nchans, band='UHF', toa_format='tempo2', save_path="/fred/oz005/tabbott/examine_toas/plots/"):
    '''
    Plot the distribution of TOA errors from .tim files. Scales all TOA errors to a 1 hour observation. 
    
    Parameters
    ----------
    obs_dict : dict
        Dictionary containing observation information for the pulsars.
    nchans : int
        Number of frequency channels / time of arrivals to use in each observation.
    band : str
        The observing band, either 'L-band' or 'UHF'. Default is 'UHF'.
    toa_format : str
        Format of the .tim files ('IPTA' or 'tempo2').
        
    Returns
    -------
    None
    '''
    all_toas = []
    all_toa_errs = []
    progress = 0 # progress bar
    for psr in obs_dict.keys():
        psr_toas = []
        psr_toa_errs = []
        # locate and read the .tim file
        for obs in obs_dict[psr].keys():
            obs_length = obs_dict[psr][obs][1] # 1 to grab observation length in seconds
            obs_length_scaling_factor = np.sqrt(3600 / obs_length) # scale errors to 1 hour observation
            toa_file = f'/fred/oz005/tabbott/meerkat-timing/toas/{nchans}ch_{band}_toas/{psr}_{obs}_{nchans}ch_{band}.tim'
            if toa_format == 'IPTA': # read IPTA .tim files
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    psr_toas.append(float(line_comps[2]))
                    psr_toa_errs.append(float(line_comps[4]) * obs_length_scaling_factor)
                    all_toas.append(float(line_comps[2]))
                    all_toa_errs.append(float(line_comps[4]) * obs_length_scaling_factor)
            elif toa_format == 'tempo2': # read tempo2 .tim files
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    # skip lines that say "FORMAT 1"
                    if "FORMAT" in line_comps:
                        continue
                    else: 
                        psr_toas.append(float(line_comps[2]))
                        psr_toa_errs.append(float(line_comps[3]) * obs_length_scaling_factor)
                        all_toas.append(float(line_comps[2]))
                        all_toa_errs.append(float(line_comps[3]) * obs_length_scaling_factor)
        
        # plot the toa error distribution of each pulsar on a logarithmic scale
        plt.figure(figsize=(10, 6))
        log_bins = np.logspace(np.log10(min(psr_toa_errs)), np.log10(max(psr_toa_errs)), num=30)
        plt.hist(psr_toa_errs, bins=log_bins)
        plt.xscale('log')
        plt.xlabel('TOA Error (microseconds)')
        plt.ylabel('Number of TOAs')
        plt.title(f'Distribution of TOA Errors for {psr}')
        plt.tight_layout()
        plt.grid()
        if save_path:
            plt.savefig(f'{save_path}{psr}_toa_distribution_{nchans}ch_{band}.png')
        progress += 1
        print(f'Processed {progress} / {len(obs_dict.keys())} pulsars')
        plt.close()

    print(f'Minimum {band} TOA error: {min(all_toa_errs)} microseconds')
    print(f'Maximum {band} TOA error: {max(all_toa_errs)} microseconds')
    
def plot_multiband_toas(uhf_obs_dict, lband_obs_dict, nchans, toa_format='tempo2', save_path="/fred/oz005/tabbott/examine_toas/plots/"):
    '''
    Plot the distribution of TOA errors from UHF and L-band .tim files. Scales all TOA errors to a 1 hour observation. Plots the distributions on the same plot for easy comparison.
    
    Parameters
    ----------
    uhf_obs_dict : dict
        Dictionary containing observation information for the pulsars in UHF band.
    lband_obs_dict : dict
        Dictionary containing observation information for the pulsars in L-band.
    toa_format : str
        Format of the .tim files ('IPTA' or 'tempo2').
        
    Returns
    -------
    None
    '''

    # Read UHF TOA errors
    for psr in uhf_obs_dict.keys():
        uhf_toa_errs = []
        lband_toa_errs = []
        for obs in uhf_obs_dict[psr].keys():
            toa_file = f'/fred/oz005/tabbott/meerkat-timing/toas/{nchans}ch_UHF_toas/{psr}_{obs}_{nchans}ch_UHF.tim'
            obs_length = uhf_obs_dict[psr][obs][1] # 1 to grab observation length in seconds
            obs_length_scaling_factor = np.sqrt(3600 / obs_length) # scale errors to 1 hour observation
            if toa_format == 'IPTA':
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    uhf_toa_errs.append(float(line_comps[4]) * obs_length_scaling_factor)
            elif toa_format == 'tempo2':
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    if "FORMAT" in line_comps:
                        continue
                    else:
                        uhf_toa_errs.append(float(line_comps[3]) * obs_length_scaling_factor)
    

        for obs in lband_obs_dict[psr].keys():
            toa_file = f'/fred/oz005/tabbott/meerkat-timing/toas/{nchans}ch_L-band_toas/{psr}_{obs}_{nchans}ch_L-band.tim'
            obs_length = lband_obs_dict[psr][obs][1] # 1 to grab observation length in seconds
            obs_length_scaling_factor = np.sqrt(3600 / obs_length) # scale errors to 1 hour observation
            if toa_format == 'IPTA':
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    lband_toa_errs.append(float(line_comps[4]) * obs_length_scaling_factor)
            elif toa_format == 'tempo2':
                with open(toa_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    line_comps = line.split()
                    if "FORMAT" in line_comps:
                        continue
                    else: 
                        lband_toa_errs.append(float(line_comps[3]) * obs_length_scaling_factor)
        # Plot the normalized TOA error distributions
        plt.figure(figsize=(10, 6))
        log_bins = np.logspace(-1, 3, num=30)  #
        plt.hist(uhf_toa_errs, bins=log_bins, alpha=0.5, label='UHF', density=True)
        plt.hist(lband_toa_errs, bins=log_bins, alpha=0.5, label='L-band', density=True)
        plt.xscale('log')
        plt.xlabel('TOA Error (microseconds)')
        plt.ylabel('Normalized Number of TOAs')
        plt.title(f'Normalized TOA Error Distributions for {psr}')
        plt.legend()
        plt.tight_layout()
        plt.grid()
        if save_path:
            plt.savefig(f'{save_path}{psr}_toa_distribution_multiband_{nchans}ch.png')
            
        plt.close()

    
    
def plot_rms(plot_dir="/fred/oz005/tabbott/examine_toas/plots/", save_path="/fred/oz005/tabbott/examine_toas/plots/"):
    # load the *_rms.txt files from plot_dir
    # they have the format: 
    # 'Pulsar\tPre-fit RMS (us)\tPost-fit RMS (us)\n'
    lband_rms_file = os.path.join(plot_dir, 'tempo2_L-band_rms.txt')
    uhf_rms_file = os.path.join(plot_dir, 'tempo2_UHF_rms.txt')
    
    lband_prefit = []
    lband_postfit = []
    uhf_prefit = []
    uhf_postfit = []
    
    with open(lband_rms_file, 'r') as f:
        lines = f.readlines()[1:] # skip header
        for line in lines:
            comps = line.split()
            lband_prefit.append(float(comps[1]))
            lband_postfit.append(float(comps[2]))
    with open(uhf_rms_file, 'r') as f:
        lines = f.readlines()[1:] # skip header
        for line in lines:
            comps = line.split()
            uhf_prefit.append(float(comps[1]))
            uhf_postfit.append(float(comps[2]))
            
    # plot the L-band prefit vs UHF post-fit RMS
    plt.figure(figsize=(8, 8))
    plt.scatter(lband_prefit, uhf_postfit, color='blue')
    # also plot y=x line
    max_rms = max(max(lband_prefit), max(uhf_postfit)) * 1.1
    plt.plot([0, max_rms], [0, max_rms], color='k', linestyle='--')
    plt.xlabel('L-band RMS No Fit (us)')
    plt.ylabel('UHF RMS Post-DM Fit (us)')
    plt.title('RMS Comparison')
    plt.ylim(0, 50)
    plt.xlim(0, 50)
    plt.grid()
    if save_path:
        plt.savefig(f'{save_path}tempo2_rms_comparison.png')
        
    plt.close()