# SPDX-FileCopyrightText: 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import os
import imageio as iio
import numpy as np
from PIL import Image, ImageChops, ImageDraw


def ConcatNDiff(
    file1,
    file2,
    dir1="./",
    dir2="./",
    label1="",
    label2="",
    difflabel="",
    outfile="vs_f1-f2",
    outdir="./",
    cleandiff=1,
):
    ##Input check
    # Directories
    if dir1[-1] != "/":
        dir1 = dir1 + "/"
    if dir2[-1] != "/":
        dir2 = dir2 + "/"
    if outdir[-1] != "/":
        outdir = outdir + "/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    dirs = [dir1, dir2, outdir]
    # File extensions
    file1 = file1.replace(".mp4", "")
    file2 = file2.replace(".mp4", "")
    if outfile == "vs_f1-f2":
        outfile = "vs_" + file1 + "-" + file2
    files = [file1, file2, "diff_" + outfile]
    file1 = file1 + ".mp4"
    file2 = file2 + ".mp4"
    outfile = outfile.replace(".mp4", "")
    difffile = outdir + "diff_" + outfile + ".mp4"
    # Labels
    labels = [label1, label2, difflabel]

    #
    print("Comparing MP4 files:", dir1 + file1, " & ", dir2 + file2)
    if "".join(labels) == "":
        print("No labels are being added.")
    else:
        print("With labels:\n\t", "\n\t ".join(labels))
    print("Output will be saved as ", outdir + outfile + ".mp4\n")

    # Loads images from mp4 files
    MP4_1 = iio.mimread(dir1 + file1, memtest=False)
    MP4_2 = iio.mimread(dir2 + file2, memtest=False)
    frames = len(MP4_1)
    if frames != len(MP4_2):
        print("The mp4 files dont have the same number of frames.")
    else:
        with iio.get_writer(
            difffile,
            format="mp4",
            mode="I",
        ) as writer:
            # Initializes diff image
            for i in range(frames):
                # Loads frames  into PIL.Image format
                im1 = Image.fromarray(MP4_1[i])
                im2 = Image.fromarray(MP4_2[i])
                # Computes pixel by pixel absolute value difference of frames
                farme_diff = ImageChops.difference(im1, im2)
                # farme_diff.show()
                MP4_D = np.array(farme_diff)
                if difflabel != "":
                    imD = Image.fromarray(MP4_D)
                    draw = ImageDraw.Draw(imD)
                    draw.text((10, 10), difflabel, fill=(255, 255, 255))
                    MP4_D = np.array(imD)
                # Saves temporary mp4 with mp4 diff
                writer.append_data(MP4_D)
        # Concatenates MP4 original files and diff file in a single row
        ConcatNxM(
            files,
            dirs=dirs,
            labels=labels,
            N=1,
            M=3,
            outfile=outfile,
            outdir=outdir,
        )

        # Remove diff mp4 file
        if cleandiff:
            print("Deleting diff mp4 file...")
            os.remove(difffile)
            print("All done.")


def ConcatNxM(
    files,
    dirs=["./", "./"],
    labels=["", ""],
    N=1,
    M=1,
    outfile="Concat_NxM",
    outdir="./",
):
    ##Input check
    nfiles = len(files)
    if N * M < nfiles:
        print(
            f"Number of files ({nfiles}) is greater than {N}x{M} space."
            f" Increasing columns to fit files."
        )
        M = int((nfiles + N - 1) / N)
    if len(dirs) < nfiles:
        print(
            "Number of directories is less than number of files. Searching for files in",
            dirs[0],
        )
        dirs = dirs + [dirs[0]] * (nfiles - len(dirs))
    labels = labels or []
    if len(labels) < nfiles:
        print(
            f"WARNING: Length of labels ({len(labels)}) does not match length of files ({len(files)})."
            f" Labels will be used for the first {len(labels)} files, and the rest will be unlabelled."
        )
        labels = labels + [""] * (nfiles - len(labels))

    # Directories and file extensions
    for i in range(nfiles):
        files[i] = files[i].replace(".mp4", "")
        files[i] = files[i] + ".mp4"
        if dirs[i][-1] != "/":
            dirs[i] = dirs[i] + "/"
    if outdir[-1] != "/":
        outdir = outdir + "/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if outfile == "Concat_NxM":
        outfile = "Concat_" + str(N) + "x" + str(M)
    outfile = outdir + outfile.replace(".mp4", "")
    outfile = outfile + ".mp4"
    files = np.char.add(dirs, files)

    # Verbose
    print("Stitching", nfiles, "MP4 files on", N, "by", M, "grid.")
    print("Source files:\n\t", "\n\t ".join(files))
    if "".join(labels) == "":
        print("No labels are being added.")
    else:
        print("With labels=\n\t", "\n\t ".join(labels))
    print("Output will be saved as ", outfile, "\n")

    # Loads images from mp4 files
    MP4files = [None] * nfiles
    frames = [None] * nfiles
    for i in range(nfiles):
        MP4files[i] = iio.mimread(files[i], memtest=False)
        frames[i] = len(MP4files[i])
    # Only continues if all files have equal number of frames
    if not all(nf == frames[0] for nf in frames):
        print("The mp4 files don't have the same number of frames.")
    else:
        # Processes MP4 files
        blankfile = np.ones(np.shape(MP4files[0][0]), dtype=np.uint8) * 255
        height = np.shape(MP4files[0])[1]
        width = np.shape(MP4files[0])[2]
        with iio.get_writer(
            outfile,
            format="mp4",
            mode="I",
        ) as writer:
            for idx in range(frames[0]):
                # Stitches MP4 files in NxM grid
                for row in range(N):
                    R = MP4files[row * M][idx] if row * M < nfiles else blankfile
                    for col in range(1, M):
                        file = row * M + col
                        if file < nfiles:
                            R = np.concatenate((R, MP4files[file][idx]), axis=1)
                        else:
                            R = np.concatenate((R, blankfile), axis=1)
                    if row == 0:
                        Sframe = R
                    else:
                        Sframe = np.concatenate((Sframe, R), axis=0)

                # Adds labels if present
                if "".join(labels) != "":
                    imS = Image.fromarray(Sframe)
                    draw = ImageDraw.Draw(imS)
                    for row in range(N):
                        for col in range(M):
                            if row * M + col < nfiles:
                                draw.text(
                                    (10 + col * width, 10 + row * height),
                                    labels[row * M + col],
                                    fill=(0, 0, 0),
                                )
                    Sframe = np.array(imS)

                # Saves mp4 with stitched frames
                writer.append_data(Sframe)
