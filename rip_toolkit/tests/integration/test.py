# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
import rip_toolkit as ript

image_path = "RIP_legacy/ripdocker_latest.sif"

######################################################################################
######################################################################################

wrfout_dir = "RIP_legacy/Sample/WRFData"
output_dir = "tests/integration/results/Sample"
file_tag = "Sample"

mt = ript.get_model_times(wrfout_dir)
ript.print_model_times(mt)
dmt = ript.utils.date_model_times(mt)

ripdp = ript.preprocess(
    wrfout_dir=wrfout_dir,
    output_dir=output_dir,
    file_tag=file_tag,
    image_path=image_path,
)

pt_y = ript.point_trajectory(
    wrfout_dir=wrfout_dir,
    output_dir=output_dir,
    ripdp_data=ripdp,
    traj_tag="yucatan_t=0-12_900_hPa",
    traj_x=48,
    traj_y=17,
    traj_z=900,
    traj_t_0=dmt["2005-08-28_00:00:00"],
    traj_t_f=dmt["2005-08-28_12:00:00"],
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
    image_path=image_path,
)

pt_f = ript.point_trajectory(
    wrfout_dir=wrfout_dir,
    output_dir=output_dir,
    ripdp_data=ripdp,
    traj_tag="florida_t=0-12_900_hPa",
    traj_x=80,
    traj_y=40,
    traj_z=900,
    traj_t_0=12,
    traj_t_f=0,
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
    image_path=image_path,
)

st = ript.swarm_trajectories(
    wrfout_dir=wrfout_dir,
    output_dir=output_dir,
    ripdp_data=ripdp,
    traj_tag="gulf_of_mexico_t=0-6",
    traj_x=[50, 65],
    traj_y=[30, 45],
    traj_z=[900, 600],
    traj_t_0=0,
    traj_t_f=6,
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
    image_path=image_path,
)

pl = ript.plot_trajectories(
    output_dir=output_dir,
    ripdp_data=ripdp,
    traj_tags_colors={
        "yucatan_t=0-12_900_hPa": "light.blue",
        "florida_t=0-12_900_hPa": "blue",
        **st,
    },
    plot_tag="Sample_plot",
    image_path=image_path,
    format="pdf",
)

######################################################################################
######################################################################################

os.environ["IMAGE_PATH"] = image_path
os.environ["WRFOUT_DIR"] = wrfout_dir
os.environ["OUTPUT_DIR"] = "tests/integration/results/SampleEnv"

mt = ript.get_model_times(wrfout_dir)
ript.print_model_times(mt)
dmt = ript.utils.date_model_times(mt)

ripdp = ript.preprocess(
    file_tag=file_tag,
)

os.environ["RIPDP_DATA"] = ripdp

pt_y = ript.point_trajectory(
    traj_tag="yucatan_t=0-12_900_hPa",
    traj_x=48,
    traj_y=17,
    traj_z=900,
    traj_t_0=dmt["2005-08-28_00:00:00"],
    traj_t_f=dmt["2005-08-28_12:00:00"],
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
)

pt_f = ript.point_trajectory(
    traj_tag="florida_t=0-12_900_hPa",
    traj_x=80,
    traj_y=40,
    traj_z=900,
    traj_t_0=12,
    traj_t_f=0,
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
)

st = ript.swarm_trajectories(
    traj_tag="gulf_of_mexico_t=0-6",
    traj_x=[50, 65],
    traj_y=[30, 45],
    traj_z=[900, 600],
    traj_t_0=0,
    traj_t_f=6,
    traj_dt=1200,
    hydrometeor=0,
    traj_diagnostics=ript.diagnostic_groups("base"),
)

pl = ript.plot_trajectories(
    traj_tags_colors={
        "yucatan_t=0-12_900_hPa": "light.blue",
        "florida_t=0-12_900_hPa": "blue",
        **st,
    },
    plot_tag="Sample_plot",
    format="pdf",
)

######################################################################################
######################################################################################


# wrfout_dir = "/home/francisco/Documents/SpanishPlumeAnalysis/tests/wrfdata/arwen_1"
# output_dir = "tests/integration/results/Arwen"
# file_tag = "Arwen"

# print("Model times available in wrfout_dir:")
# print(f"{ript.get_model_times(wrfout_dir)}".replace(",", "\n"))
# print()

# ripdp = ript.preprocess(
#     wrfout_dir=wrfout_dir,
#     output_dir=output_dir,
#     file_tag=file_tag,
#     image_path=image_path,
# )

# ripdp = "tests/integration/results/Arwen/RIPDP/rdp_Arwen"

# st = ript.stack_trajectories(
#     wrfout_dir=wrfout_dir,
#     output_dir=output_dir,
#     ripdp_data=ripdp,
#     traj_tag="NorthSea",
#     traj_x=230,
#     traj_y=200,
#     traj_z=[900, 800, 700, 600, 500],
#     traj_t_0=43,
#     traj_t_f=45.66667,
#     traj_dt=300,
#     hydrometeor=0,
#     traj_diagnostics=ript.diagnostic_groups("base"),
#     image_path=image_path,
# )
# pl = ript.plot_trajectories(
#     output_dir=output_dir,
#     ripdp_data=ripdp,
#     traj_tags_colors={**st},
#     plot_tag="Arwen_plot",
#     image_path=image_path,
#     format="pdf",
# )

######################################################################################
######################################################################################

# image_path="RIP_legacy/ripdocker_latest.sif"
# wrfout_dir="RIP_legacy/Sample/WRFData"
# output_dir="tests/integration/results/CLI"
# rip_toolkit_cli --task preprocess --wrfout_dir $wrfout_dir --output_dir $output_dir --tag "cli_sample" --image_path $image_path
#   ripdp_data=tests/integration/results/CLI/RIPDP/rdp_cli_sample
# rip_toolkit_cli --task point_trajectory --wrfout_dir $wrfout_dir --output_dir $output_dir --ripdp_data $ripdp_data --tag "cli_yucatan_t=0-12_900_hPa" --traj_x 48 --traj_y 17 --traj_z 900 --traj_t_0 0 --traj_t_f 12 --traj_dt 1200 --hydrometeor 0 --traj_diagnostic_group base --image_path $image_path
#   point_traj=tests/integration/results/CLI/BTrajectories/cli_yucatan_t=0-12_900_hPa_traj_point.traj
# rip_toolkit_cli --task swarm_trajectories --wrfout_dir $wrfout_dir --output_dir $output_dir --ripdp_data $ripdp_data --tag "cli_yucatan_t=0-12_900_hPa" --traj_x 50,65 --traj_y 30,45 --traj_z 600,900 --traj_t_0 0 --traj_t_f 12 --traj_dt 1200 --hydrometeor 0 --traj_diagnostic_group base --image_path $image_path
#   traj_tags=cli_yucatan_t=0-12_900_hPa_-_50_30_-_600_hPa,cli_yucatan_t=0-12_900_hPa_-_65_30_-_600_hPa,cli_yucatan_t=0-12_900_hPa_-_50_45_-_600_hPa,cli_yucatan_t=0-12_900_hPa_-_65_45_-_600_hPa,cli_yucatan_t=0-12_900_hPa_-_50_30_-_900_hPa,cli_yucatan_t=0-12_900_hPa_-_65_30_-_900_hPa,cli_yucatan_t=0-12_900_hPa_-_50_45_-_900_hPa,cli_yucatan_t=0-12_900_hPa_-_65_45_-_900_hPa
#   traj_cols=magenta,light.magenta,red.coral,red,orange,mustard,green,dark.green
# rip_toolkit_cli --task plot_trajectories --output_dir $output_dir --ripdp_data $ripdp_data --traj_tags cli_yucatan_t=0-12_900_hPa,$traj_tags --traj_cols blue,$traj_cols --tag "cli_sample_plot" --image_path $image_path

######################################################################################
######################################################################################

# export IMAGE_PATH="RIP_legacy/ripdocker_latest.sif"
# export WRFOUT_DIR="RIP_legacy/Sample/WRFData"
# export OUTPUT_DIR="tests/integration/results/CLI"
# rip_toolkit_cli -t preprocess -T "cli_short_sample"
#   export RIPDP_DATA=tests/integration/results/CLI/RIPDP/rdp_cli_short_sample
# rip_toolkit_cli -t point_trajectory -T "cli_short_yucatan_t=0-12_900_hPa" -x 48 -y 17 -z 900 -t0 0 -tf 12 -dt 1200 -H 0 -g base
#   point_traj=tests/integration/results/CLI/BTrajectories/cli_short_yucatan_t=0-12_900_hPa_traj_point.traj
# rip_toolkit_cli -t swarm_trajectories -T "cli_short_yucatan_t=0-12_900_hPa" -x 50,65 -y 30,45 -z 600,900 -t0 0 -tf 12 -dt 1200 -H 0 -g base
#   traj_tags=cli_short_yucatan_t=0-12_900_hPa_-_50_30_-_600_hPa,cli_short_yucatan_t=0-12_900_hPa_-_65_30_-_600_hPa,cli_short_yucatan_t=0-12_900_hPa_-_50_45_-_600_hPa,cli_short_yucatan_t=0-12_900_hPa_-_65_45_-_600_hPa,cli_short_yucatan_t=0-12_900_hPa_-_50_30_-_900_hPa,cli_short_yucatan_t=0-12_900_hPa_-_65_30_-_900_hPa,cli_short_yucatan_t=0-12_900_hPa_-_50_45_-_900_hPa,cli_short_yucatan_t=0-12_900_hPa_-_65_45_-_900_hPa
#   traj_cols=magenta,light.magenta,red.coral,red,orange,mustard,green,dark.green
# rip_toolkit_cli -t plot_trajectories --traj_tags cli_short_yucatan_t=0-12_900_hPa,$traj_tags --traj_cols blue,$traj_cols -T "cli_short_sample_plot"
