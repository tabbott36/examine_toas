import re
import os

# for plotting 
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from datetime import datetime


def parse_tempo2_output(observing_band, tempo2_output_dir="/home/tabbott/meerkat-timing/tempo2_output/"):
    
    dm_dict = {}
    tempo2_output_files = [f for f in os.listdir(tempo2_output_dir) if f.endswith(f"_{observing_band}_tempo2_output.txt")]
    list_all_psrs = [f.split("_")[0] for f in tempo2_output_files]

    for psr in list_all_psrs:
        dm_dict[psr] = {'OBS_TIME' : [], 'DM': [], 'DM_err': []}

    for tempo2_output_file in tempo2_output_files:
        # split the file name with "_" and take the first term (pulsar name)
        psr = tempo2_output_file.split("_")[0]
        obs_time = tempo2_output_file.split("_")[1]
        
        with open(os.path.join(tempo2_output_dir, tempo2_output_file)) as f:
            for line in f:
                # Match only the main DM row (not DM1/DM2)
                if re.match(r"^DM\s+\(cm\^-3 pc\)", line):
                    parts = line.split()
                    # parts:
                    # 0 = DM
                    # 1 = (cm^-3
                    # 2 = pc)
                    # 3 = pre-fit
                    # 4 = post-fit
                    # 5 = uncertainty
                    dm_post = float(parts[4])
                    dm_unc = float(parts[5])
                    dm_dict[psr]['DM'].append(dm_post)
                    dm_dict[psr]['DM_err'].append(dm_unc)
                    dm_dict[psr]['OBS_TIME'].append(obs_time)
                    break
                
    return dm_dict


def plot_dm_series(observing_band, dm_dict, psr_list, include_outliers=False):

    if include_outliers:
        for psr in psr_list:
            obs_times = [datetime.strptime(t, "%Y-%m-%d-%H:%M:%S") for t in dm_dict[psr]['OBS_TIME']]
            dms = dm_dict[psr]['DM']
            dm_errs = dm_dict[psr]['DM_err']
            
            plt.errorbar(obs_times, dms, yerr=dm_errs, fmt='o', label=psr)
            plt.title(f"DM Variation for {psr}")
            plt.xlabel("Observation Date")
            plt.ylabel("Dispersion Measure (cm^-3 pc)")
            plt.grid()
            plt.legend()
            ax = plt.gca()  # get current axis
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
            plt.tight_layout()
            plt.savefig(f"/home/tabbott/meerkat-timing/plots/{psr}_{observing_band}_dm_variation.png")
            plt.clf()
            print(f"Saved DM variation plot for {psr} as {psr}_{observing_band}_dm_variation.png")
            
    else:
        for psr in psr_list:
            # Calculate mean and std dev
            dms = dm_dict[psr]['DM']
            mean_dm = sum(dms) / len(dms)
            std_dm = (sum((x - mean_dm) ** 2 for x in dms) / len(dms)) ** 0.5
            
            # Filter out outliers
            filtered_obs_times = []
            filtered_dms = []
            filtered_dm_errs = []
            for i, dm in enumerate(dms):
                if abs(dm - mean_dm) <= 5 * std_dm:
                    filtered_obs_times.append(datetime.strptime(dm_dict[psr]['OBS_TIME'][i], "%Y-%m-%d-%H:%M:%S"))
                    filtered_dms.append(dm)
                    filtered_dm_errs.append(dm_dict[psr]['DM_err'][i])
            
            plt.errorbar(filtered_obs_times, filtered_dms, yerr=filtered_dm_errs, fmt='o', label=psr)
            plt.title(f"DM Variation for {psr} (Outliers Removed)")
            plt.xlabel("Observation Date")
            plt.ylabel("Dispersion Measure (cm^-3 pc)")
            plt.grid()
            plt.legend()
            ax = plt.gca()  # get current axis
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
            plt.tight_layout()
            plt.savefig(f"/home/tabbott/meerkat-timing/plots/{psr}_{observing_band}_dm_variation_no_outliers.png")
            plt.clf()
            print(f"Saved DM variation plot for {psr} as {psr}_{observing_band}_dm_variation_no_outliers.png")
            
            
uhf_dm_dict = parse_tempo2_output("UHF")
l_band_dm_dict = parse_tempo2_output("L-band")

psrs_to_plot = ['J1902-5105', 'J1036-8317', 'J0955-6150', 'J1903-7051', 'J2222-0137', 'J0101-6422']

plot_dm_series("UHF", uhf_dm_dict, psrs_to_plot, include_outliers=False)
plot_dm_series("L-band", l_band_dm_dict, psrs_to_plot, include_outliers=False)


def plot_both_bands(uhf_dm_dict, lband_dm_dict, psr_list, include_outliers=False):
    for psr in psr_list:
        # UHF data
        if include_outliers:
            
            uhf_obs_times = [datetime.strptime(t, "%Y-%m-%d-%H:%M:%S") for t in uhf_dm_dict[psr]['OBS_TIME']]
            uhf_dms = uhf_dm_dict[psr]['DM']
            uhf_dm_errs = uhf_dm_dict[psr]['DM_err']
            
            # L-band data
            lband_obs_times = [datetime.strptime(t, "%Y-%m-%d-%H:%M:%S") for t in lband_dm_dict[psr]['OBS_TIME']]
            lband_dms = lband_dm_dict[psr]['DM']
            lband_dm_errs = lband_dm_dict[psr]['DM_err']
            
            plt.errorbar(uhf_obs_times, uhf_dms, yerr=uhf_dm_errs, fmt='o', label='UHF Band', color='blue')
            plt.errorbar(lband_obs_times, lband_dms, yerr=lband_dm_errs, fmt='o', label='L Band', color='orange')
            
            plt.title(f"DM Variation for {psr} (Both Bands)")
            plt.xlabel("Observation Date")
            plt.ylabel("Dispersion Measure (cm^-3 pc)")
            plt.grid()
            plt.legend()
            ax = plt.gca()  # get current axis
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
            plt.tight_layout()
            plt.savefig(f"/home/tabbott/meerkat-timing/plots/{psr}_both_bands_dm_variation.png")
            plt.clf()
            print(f"Saved DM variation plot for {psr} as {psr}_both_bands_dm_variation.png")
        else:
            # Calculate mean and std dev for UHF
            uhf_dms = uhf_dm_dict[psr]['DM']
            mean_uhf_dm = sum(uhf_dms) / len(uhf_dms)
            std_uhf_dm = (sum((x - mean_uhf_dm) ** 2 for x in uhf_dms) / len(uhf_dms)) ** 0.5
            
            # Filter UHF outliers
            filtered_uhf_obs_times = []
            filtered_uhf_dms = []
            filtered_uhf_dm_errs = []
            for i, dm in enumerate(uhf_dms):
                if abs(dm - mean_uhf_dm) <= 5 * std_uhf_dm:
                    filtered_uhf_obs_times.append(datetime.strptime(uhf_dm_dict[psr]['OBS_TIME'][i], "%Y-%m-%d-%H:%M:%S"))
                    filtered_uhf_dms.append(dm)
                    filtered_uhf_dm_errs.append(uhf_dm_dict[psr]['DM_err'][i])
            
            # Calculate mean and std dev for L-band
            lband_dms = lband_dm_dict[psr]['DM']
            mean_lband_dm = sum(lband_dms) / len(lband_dms)
            std_lband_dm = (sum((x - mean_lband_dm) ** 2 for x in lband_dms) / len(lband_dms)) ** 0.5
            
            # Filter L-band outliers
            filtered_lband_obs_times = []
            filtered_lband_dms = []
            filtered_lband_dm_errs = []
            for i, dm in enumerate(lband_dms):
                if abs(dm - mean_lband_dm) <= 5 * std_lband_dm:
                    filtered_lband_obs_times.append(datetime.strptime(lband_dm_dict[psr]['OBS_TIME'][i], "%Y-%m-%d-%H:%M:%S"))
                    filtered_lband_dms.append(dm)
                    filtered_lband_dm_errs.append(lband_dm_dict[psr]['DM_err'][i])
            
            plt.errorbar(filtered_lband_obs_times, filtered_lband_dms, yerr=filtered_lband_dm_errs, fmt='o', label='L Band', color='orange')
            plt.errorbar(filtered_uhf_obs_times, filtered_uhf_dms, yerr=filtered_uhf_dm_errs, fmt='o', label='UHF Band', color='blue')
            plt.title(f"DM Variation for {psr} (Both Bands, Outliers Removed)")
            plt.xlabel("Observation Date")
            plt.ylabel("Dispersion Measure (cm^-3 pc)")
            plt.grid()
            plt.legend()
            ax = plt.gca()  # get current axis
            ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
            plt.tight_layout()
            plt.savefig(f"/home/tabbott/meerkat-timing/plots/{psr}_both_bands_dm_variation_no_outliers.png")
            plt.clf()
            print(f"Saved DM variation plot for {psr} as {psr}_both_bands_dm_variation_no_outliers.png")
        
        
# plot_dm_series(observing_band="UHF", dm_dict=uhf_dm_dict, psr_list=psrs_to_plot, include_outliers=False)
plot_both_bands(uhf_dm_dict, l_band_dm_dict, psrs_to_plot, include_outliers=False)


# def parse_tempo2_rms(tempo2_file, ):
#     '''
#     This function runs tempo2 on the provided .tim and .par files to generate timing residuals and DM measurements.
    
#     Parameters:
#     -----------
#     tempo2_file : str
#         Path to the tempo2 output file.
#     params_to_parse : list of str
#         List of parameters to parse from the tempo2 output.
        
#     Returns:
#     --------
#     None
#     '''
    
#     # load the tempo2_output file
#     with open(tempo2_file, 'r') as f:
#         lines = f.readlines()
    
#     prefit_vals = []
#     postfit_vals = []
    
#     # run tempo2 fitting only for DM
    
        
#     for line in stdout.decode().split('\n'):
#         if 'RMS pre-fit residual' in line:
#             parts = line.split(',')
#             prefit_part = parts[0].strip()
#             postfit_part = parts[1].strip()
            
#             prefit_rms_value = prefit_part.split('=')[1].strip().split(' ')[0]
#             postfit_rms_value = postfit_part.split('=')[1].strip().split(' ')[0]
            
#             prefit_rms.append(float(prefit_rms_value))
#             postfit_rms.append(float(postfit_rms_value))
#             parse_success = True

    
#     # write the prefit and postfit RMS to a text file
#     with open(os.path.join(plot_dir, f'tempo2_{band}_rms.txt'), 'w') as f:
#         f.write('Pulsar\tPre-fit RMS (us)\tPost-fit RMS (us)\n')
#         for i, psr in enumerate(burst_dict.keys()):
#             f.write(f"{psr}\t{prefit_rms[i]}\t{postfit_rms[i]}\n")
            