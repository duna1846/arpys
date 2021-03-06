from nexusformat.nexus import *
import numpy as np
import xarray as xr


def load_diamond_consolidated(filename):
    f = nxload(filename)
    counts = np.array(f.entry1.instrument.analyser.data)
    sapolar = np.array(f.entry1.instrument.manipulator.sapolar)
    energies = np.array(f.entry1.instrument.analyser.energies)
    slit_angle = np.array(f.entry1.instrument.analyser.angles)

    axis_labels = ['slit', 'energy']

    if len(sapolar) == 1:  # alternatively, if counts.shape[0] == 1
        vals = np.copy(counts[0, :, :])
        coords = {'slit': slit_angle, 'energy': energies}

    else:
        vals = np.copy(counts)
        coords = {'perp': sapolar, 'slit': slit_angle, 'energy': energies}
        # append perp label to beginning of axis_labels if the file is a fermi map
        axis_labels.insert(0, 'perp')

    metadata = read_metadata(f)
    return xr.DataArray(vals, dims=axis_labels, coords=coords, attrs=metadata)


def load_diamond_fermi(filename):
    f = nxload(filename)
    counts = np.array(f.entry1.instrument.analyser.data)
    sapolar = np.array(f.entry1.instrument.manipulator.sapolar)
    energies = np.array(f.entry1.instrument.analyser.energies)
    slit_angle = np.array(f.entry1.instrument.analyser.angles)

    axis_labels = ['perp', 'slit', 'energy']
    coords = {'perp': sapolar, 'slit': slit_angle, 'energy': energies}

    vals = np.copy(counts)

    return xr.DataArray(vals, dims=axis_labels, coords=coords)


def load_diamond_single(filename):
    f = nxload(filename)
    counts = np.array(f.entry1.instrument.analyser.data)
    sapolar = np.array(f.entry1.instrument.manipulator.sapolar)
    energies = np.array(f.entry1.instrument.analyser.energies)
    slit_angle = np.array(f.entry1.instrument.analyser.angles)

    axis_labels = ['slit', 'energy']
    coords = {'slit': slit_angle, 'energy': energies}

    vals = np.copy(counts[0, :, :])

    return xr.DataArray(vals, dims=axis_labels, coords=coords)


def read_metadata(nxobject):

    metadata = {}
    # Read manipulator positions first
    x = nxobject.entry1.instrument.manipulator.sax.nxvalue
    y = nxobject.entry1.instrument.manipulator.say.nxvalue
    z = nxobject.entry1.instrument.manipulator.saz.nxvalue
    tilt = nxobject.entry1.instrument.manipulator.satilt.nxvalue
    az = nxobject.entry1.instrument.manipulator.saazimuth.nxvalue
    polar = nxobject.entry1.instrument.manipulator.sapolar.nxvalue

    # Read Temperatures
    cryostat = nxobject.entry1.sample.cryostat_temperature.nxvalue
    shield = nxobject.entry1.sample.shield_temperature.nxvalue
    sample = nxobject.entry1.sample.temperature.nxvalue

    # monochromator/beam properties
    bl_energy = nxobject.entry1.instrument.monochromator.energy.nxvalue
    exit_slit_vert = nxobject.entry1.instrument.monochromator.exit_slit_size.nxvalue
    exit_slit_horiz = nxobject.entry1.instrument.monochromator.exit_slit_size_horizontal.nxvalue
    entrance_slit_vert = nxobject.entry1.instrument.monochromator.s2_vertical_slit_size.nxvalue
    entrance_slit_horiz = nxobject.entry1.instrument.monochromator.s2_horizontal_slit_size.nxvalue
    polarization = nxobject.entry1.instrument.insertion_device.beam.final_polarisation_label.nxvalue

    # date and time properties
    datetime = nxobject.entry1.end_time.nxvalue

    # exposure settings for conversion to count rate (probably not valid for fixed mode scans, use with caution)
    acq_mode = nxobject.entry1.instrument.analyser.acquisition_mode.nxvalue
    energy_region_size = nxobject.entry1.instrument.analyser.cps_region_size.nxvalue[1]
    dwell_time = nxobject.entry1.instrument.analyser.time_for_frames.nxvalue
    sweeps = nxobject.entry1.instrument.analyser.number_of_iterations.nxvalue

    metadata['x'] = x
    metadata['y'] = y
    metadata['z'] = z
    metadata['tilt'] = tilt
    metadata['az'] = az
    metadata['polar'] = polar
    metadata['cryostat T'] = cryostat
    metadata['shield T'] = shield
    metadata['sample T'] = sample
    metadata['BL Energy'] = bl_energy
    metadata['Polarization'] = polarization
    metadata['exit slit vert'] = exit_slit_vert
    metadata['exit slit horiz'] = exit_slit_horiz
    metadata['entrance slit vert'] = entrance_slit_vert
    metadata['entrance slit horiz'] = entrance_slit_horiz
    metadata['time'] = datetime
    metadata['Acquisition Mode'] = acq_mode
    metadata['Energy Region Size'] = energy_region_size
    metadata['Dwell Time'] = dwell_time
    metadata['Sweeps'] = sweeps

    return metadata


# Convert Diamond spectra counts (2d spectra only) to count rate
def convert_to_countrate(dataxarray):
    total_time = dataxarray.attrs['Dwell Time'] * dataxarray.attrs['Energy Region Size'] * dataxarray.attrs['Sweeps']
    count_rate_xarray = dataxarray / total_time
    return count_rate_xarray
