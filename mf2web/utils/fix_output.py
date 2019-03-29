import numpy as np


def get_times_list(binout):
    """
    Method to get a times list from binary
    output.

    Parameters
    ----------
        binout : fp.binarayfile class instance

    Returns
    -------
        list of times
    """
    return sorted([float("{0:15.6f}".format(t)) for t in
                   binout.recordarray["totim"]])


def create_nprs_entry_file(nprs_file, times):
    """

    Parameters
    ----------
    nprs_file : str
        filename to write a nprs file for seawat
    times : list
        list of output times

    Returns
    -------
        None
    """
    if len(times) == 0:
        return

    with open(nprs_file, 'w') as foo:
        times = sorted(list(set(times)))
        nprs = len(times)
        foo.write("{:10d}  # NPRS  \n".format(nprs))

        t = []
        t0 = []
        for ix in range(nprs):
            if (ix + 1) % 8 == 0:
                t0.append(times[ix])
                t.append(t0)
                t0 = []
            else:
                t0.append(times[ix])

        if t0:
            t.append(t0)

        # write timprs
        fmt = "  {:8.1f}"
        for line in t:
            sfmt = fmt * len(line) + "\n"
            foo.write(sfmt.format(*line))

