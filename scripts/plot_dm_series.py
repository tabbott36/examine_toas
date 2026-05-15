import re
import os

# for plotting 
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from datetime import datetime
# get timedelta
from datetime import timedelta


def parse_tempo2_output(observing_band, burst_dict, tempo2_output_dir="/home/tabbott/meerkat-timing/tempo2_output/"):
    
    dm_dict = {}
    tempo2_output_files = [f for f in os.listdir(tempo2_output_dir) if f.endswith(f"_{observing_band}_tempo2_output.txt")]
    list_all_psrs = [f.split("_")[0] for f in tempo2_output_files]

    for psr in list_all_psrs:
        dm_dict[psr] = {'OBS_TIME' : [], 'DM': [], 'DM_err': [], 'OBS_LENGTH': []}

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
                    # dm_dict[psr]['DM_err'].append(dm_unc)
                    dm_dict[psr]['OBS_TIME'].append(obs_time)
                # get psr and obs time from the tim file name (line looks like: ".tim file: /home/tabbott/meerkat-timing/toas/J1902-5105_2024-05-15-01:54:45_16ch_L-band.tim") 
                if re.match(r"^\.tim file:", line):
                    tim_file_path = line.split(": ")[1].strip()
                    tim_file_name = os.path.basename(tim_file_path)
                    obs_timestamp = tim_file_name.split("_")[1]
                    obs_length = burst_dict[psr][obs_timestamp][1]
                    dm_dict[psr]['OBS_LENGTH'].append(obs_length)
                    # scale the DM uncertainty by the square root of the observation length to a 1   hour observation (assuming DM uncertainty scales with sqrt of observation length)
                    dm_dict[psr]['DM_err'].append(dm_unc * (3600 / obs_length) ** 0.5)
                
    return dm_dict





# Calculate mean and std dev
dm_dict = parse_tempo2_output("L-band")
dms = dm_dict["J0955-6150"]['DM']
mean_dm = sum(dms) / len(dms)
std_dm = (sum((x - mean_dm) ** 2 for x in dms) / len(dms)) ** 0.5

# Filter out outliers
filtered_obs_times = []
filtered_dms = []
filtered_dm_errs = []
for i, dm in enumerate(dms):
    if abs(dm - mean_dm) <= 5 * std_dm:
        filtered_obs_times.append(datetime.strptime(dm_dict["J0955-6150"]['OBS_TIME'][i], "%Y-%m-%d-%H:%M:%S"))
        filtered_dms.append(dm)
        filtered_dm_errs.append(dm_dict["J0955-6150"]['DM_err'][i])
        
# also plot the DM taylor series with the par file DM value       
# DMEPOCH        56983.016795999999999       
# DM             160.89405886344682257       
# DM1            0.0029955709752436083397  
# DM2            -0.00055961547315915515184 
dm_epoch = 56983.016795999999999
dm_value = 160.89405886344682257
dm1 = 0.0029955709752436083397
dm2 = -0.00055961547315915515184
# Convert DM epoch from MJD to datetime
dm_epoch_datetime = datetime.strptime("2014-01-01", "%Y-%m-%d") + timedelta(days=dm_epoch - 56658)  # MJD 56658 is 2013-12-31
# Create a function to calculate DM from the Taylor series
def dm_taylor_series(t):
    delta_days = (t - dm_epoch_datetime).total_seconds() / 86400  # convert to days
    delta_years = delta_days / 365.25
    return dm_value + dm1 * delta_years + 0.5 * dm2 * (delta_years ** 2)
# Generate DM values from the Taylor series for the filtered observation times
taylor_dms = [dm_taylor_series(t) for t in filtered_obs_times]
# Plot filtered DM values with error bars
plt.errorbar(filtered_obs_times, filtered_dms, yerr=filtered_dm_errs, fmt='o', label="Observed DM")
# Plot Taylor series DM values
plt.scatter(filtered_obs_times, taylor_dms, c='r', label="DM Taylor Series")
plt.title(f"DM Variation for J0955-6150 (Outliers Removed) with Par File DM")
plt.xlabel("Observation Date")
plt.ylabel("Dispersion Measure (cm^-3 pc)")
plt.grid()
plt.legend()
ax = plt.gca()  # get current axis
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
plt.tight_layout()
plt.savefig(f"/home/tabbott/meerkat-timing/plots/J0955-6150_dm_variation_with_par.png")
plt.clf()
print(f"Saved DM variation plot for J0955-6150 as J0955-6150_dm_variation_with_par.png")



# plt.errorbar(filtered_obs_times, filtered_dms, yerr=filtered_dm_errs, fmt='o', label="J0955-6150")
# plt.title(f"DM Variation for J0955-6150 (Outliers Removed)")
# plt.xlabel("Observation Date")
# plt.ylabel("Dispersion Measure (cm^-3 pc)")
# plt.grid()
# plt.legend()
# ax = plt.gca()  # get current axis
# ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
# plt.tight_layout()
# plt.savefig(f"/home/tabbott/meerkat-timing/plots/J0955-6150_dm_variation_with_par.png")
# plt.clf()
# print(f"Saved DM variation plot for J0955-6150 as J0955-6150_dm_variation_with_par.png")
            
            
uhf_dm_dict = parse_tempo2_output("UHF")
l_band_dm_dict = parse_tempo2_output("L-band")

psrs_to_plot = ["J1902-5105", "J1036-8317", "J0955-6150"]