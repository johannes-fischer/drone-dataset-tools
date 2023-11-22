import argparse
import os
import sys

from loguru import logger

logger.info(os.getcwd())

from track_visualizer import TrackVisualizer, DataError
from tracks_import import read_from_csv



def create_args():
    # FILEDIR = os.path.dirname(__file__)
    FILEDIR = "/home/fischer/dev/jl/DroneDatasetAnalysis/drone-dataset-tools/src"

    cs = argparse.ArgumentParser(description="Dataset Tracks Visualizer")
    # --- Input ---
    cs.add_argument('--dataset_dir',
                    help="Path to directory that contains the dataset csv files.", type=str)
    cs.add_argument('--dataset_storage_dir', default="/home/fischer/datasets",
                    help="Path to directory that contains the dataset csv files.", type=str)
    cs.add_argument('--dataset', default="exid",
                    help="Name of the dataset. Needed to apply dataset specific visualization adjustments and to load correct dataset_dir.",
                    type=str)
    cs.add_argument('--recording', default="26",
                    help="Name of the recording given by a number with a leading zero.", type=str)
    cs.add_argument('--visualizer_params_dir', default=os.path.join(FILEDIR, "..", "data", "visualizer_params"),
                    help="Directory of visualization parameter file.", type=str)
    cs.add_argument('--assets_dir', default=os.path.join(FILEDIR, "..", "assets"),
                    help="Directory of GUI asset files.", type=str)

    # --- Visualization settings ---
    cs.add_argument('--playback_speed', default=4,
                    help="During playback, only consider every nth frame. This option also applies to the outer"
                         "backward/forward jump buttons.",
                    type=int)
    cs.add_argument('--suppress_track_window', default=False,
                    help="Do not show the track window when clicking on a track. Only surrounding vehicle colors are"
                         " displayed.",
                    type=str2bool)
    cs.add_argument('--show_bounding_box', default=True,
                    help="Plot the rotated bounding boxes of all vehicles. Please note, that for vulnerable road users,"
                         " no bounding box is given.",
                    type=str2bool)
    cs.add_argument('--show_orientation', default=False,
                    help="Indicate the orientation of all vehicles by triangles.",
                    type=str2bool)
    cs.add_argument('--show_trajectory', default=False,
                    help="Show the trajectory up to the current frame for every track.",
                    type=str2bool)
    cs.add_argument('--show_future_trajectory', default=False,
                    help="Show the remaining trajectory for every track.",
                    type=str2bool)
    cs.add_argument('--annotate_track_id', default=True,
                    help="Annotate every track by its id.",
                    type=str2bool)
    cs.add_argument('--annotate_class', default=False,
                    help="Annotate every track by its class label.",
                    type=str2bool)
    cs.add_argument('--annotate_speed', default=False,
                    help="Annotate every track by its current speed.",
                    type=str2bool)
    cs.add_argument('--annotate_orientation', default=False,
                    help="Annotate every track by its current orientation.",
                    type=str2bool)
    cs.add_argument('--annotate_age', default=False,
                    help="Annotate every track by its current age.",
                    type=str2bool)
    cs.add_argument('--show_maximized', default=False,
                    help="Show the track Visualizer maximized. Might affect performance.",
                    type=str2bool)

    return vars(cs.parse_args())


def main():
    config = create_args()

    dataset_name = config["dataset"]

    dataset_dir = config["dataset_dir"]
    if dataset_dir == None:
        base_dir = config["dataset_storage_dir"]
        if dataset_name == "exid":
            dataset_dir = os.path.join(base_dir, "exiD_dataset", "data")
        elif dataset_name == "round":
            dataset_dir = os.path.join(base_dir, "rounD_dataset", "data")
        elif dataset_name == "ind":
            dataset_dir = os.path.join(base_dir, "inD_dataset", "data")
        elif dataset_name == "highd":
            dataset_dir = os.path.join(base_dir, "highD_dataset", "data")
        config["dataset_dir"] = dataset_dir

    recording = config["recording"]

    if recording is None:
        logger.error("Please specify a recording!")
        sys.exit(1)

    recording = "{:02d}".format(int(recording))

    logger.info("Loading recording {} from dataset {}", recording, dataset_name)

    # Create paths to csv files
    tracks_file = os.path.join(dataset_dir, recording + "_tracks.csv")
    tracks_meta_file = os.path.join(dataset_dir, recording + "_tracksMeta.csv")
    recording_meta_file = os.path.join(dataset_dir, recording + "_recordingMeta.csv")

    # Load csv files
    logger.info("Loading csv files {}, {} and {}", tracks_file, tracks_meta_file, recording_meta_file)
    tracks, static_info, meta_info = read_from_csv(tracks_file, tracks_meta_file, recording_meta_file,
                                                   include_px_coordinates=True)

    # Load background image for visualization
    background_image_path = os.path.join(dataset_dir, recording + "_background.png")
    if not os.path.exists(background_image_path):
        logger.warning("Background image {} missing. Fallback to using a black background.", background_image_path)
        background_image_path = None
    config["background_image_path"] = background_image_path

    try:
        visualization_plot = TrackVisualizer(config, tracks, static_info, meta_info)
        visualization_plot.show()
    except DataError:
        sys.exit(1)


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    main()
