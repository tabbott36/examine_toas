# Examine Pulsar Time-of-Arrivals (TOAs)
A repo consisting of tools to plot/examine pulsar time-of-arrival (TOA) files


print("Stage 4: Running tempo2...")
timing.run_tempo2(observations, band=observing_band)

print("Stage 5: Generating plots...")
plot_results.plot_obs(observations, band=observing_band)
plot_results.plot_toas(observations, band=observing_band)
plot_results.plot_rms()
lband_observations = obs_dict.generate_obs_dict(mpta_psrs, band="L-band")
uhf_observations = obs_dict.generate_obs_dict(mpta_psrs, band="UHF")
plot_results.plot_multiband_toas(uhf_observations, lband_observations)