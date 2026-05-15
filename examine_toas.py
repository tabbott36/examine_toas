
import json
import os
from scripts import obs_dict, timing, plot_results

nchans = 8
observing_band = "UHF"

with open("/fred/oz005/tabbott/meerkat-timing/UHF_obs_dict.json", "r") as f:
        uhf_observations = json.load(f)
with open("/fred/oz005/tabbott/meerkat-timing/L-band_obs_dict.json", "r") as f:
        lband_observations = json.load(f)
        
print("Stage 4: Running tempo2...")
for psr in uhf_observations:
    for obs in uhf_observations[psr]:
        # if the output.txt file already exists, skip this step
        if os.path.exists(f"/fred/oz005/tabbott/examine_toas/tempo2_output/{psr}_{obs}_{nchans}ch_{observing_band}_tempo2_output.txt"):
            print(f"Tempo2 output for {psr} observation {obs} already exists. Skipping this step.")
        else:
            timing.run_tempo2(
                band=observing_band,
                nchans=nchans,
                tim_file=f"/fred/oz005/tabbott/meerkat-timing/toas/{nchans}ch_{observing_band}_tim_files/{psr}_{obs}.tim",
                parfile=f"/fred/oz005/tabbott/meerkat-timing/parfiles/{psr}.par",
                fit="DM",
                save_output=True)

print("Stage 5: Generating plots...")
plot_results.plot_obs(uhf_observations, band=observing_band)
plot_results.plot_templates(uhf_observations, nchans=nchans, band=observing_band)
# plot_results.plot_toas(uhf_observations, nchans=nchans, band=observing_band)
# # plot_results.plot_rms()
# plot_results.plot_multiband_toas(uhf_observations, lband_observations, nchans=nchans)