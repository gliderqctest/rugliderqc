#!/usr/bin/env python

import numpy as np
import pandas as pd
import xarray as xr
import os
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})


def plot_qartod_flags(axis, dataset, cond_varname):
    # Iterate through the other QARTOD variables and plot flags
    colors = ['cyan', 'blue', 'mediumseagreen', 'deeppink', 'purple']
    flag_defs = dict(suspect=dict(value=3, marker='x'),
                     fail=dict(value=4, marker='^'))
    for ci, qv in enumerate([x for x in dataset.data_vars if f'{cond_varname}_qartod' in x]):
        for fd, info in flag_defs.items():
            cond_flag = dataset[qv].values
            qv_idx = np.where(cond_flag == info['value'])[0]
            if len(qv_idx) > 0:
                axis.scatter(dataset[cond_varname].values[qv_idx], dataset.pressure.values[qv_idx],
                             color=colors[ci], s=60, marker=info['marker'], label=f'{qv}-{fd}', zorder=11)


def main(deploy, fname):
    glider = deploy.split('-')[0]

    ds = xr.open_dataset(fname)
    ds = ds.swap_dims({'row': 'time'})
    ds = ds.sortby(ds.time)

    savedir = os.path.join('/Users/garzio/Documents/rucool/gliders/qartod_qc/from_erddap/plots', deploy)
    os.makedirs(savedir, exist_ok=True)

    profiletimes = np.unique(ds.profile_time.values)

    plot_sections = np.arange(0, len(profiletimes), 20)
    plot_sections = np.append(plot_sections, len(profiletimes))

    ctd_vars = ['conductivity', 'temperature', 'salinity', 'density']

    flag_defs = dict(unknown=dict(value=2, color='cyan'),
                     suspect=dict(value=3, color='orange'),
                     fail=dict(value=4, color='red'))

    markers = ['x', '^', 's', '*', 'D']

    for ps_idx, ps in enumerate(plot_sections):
        if ps_idx > 0:
            if ps_idx == 1:
                ii = 0
            else:
                ii = plot_sections[ps_idx - 1] + 1
            ptimes = profiletimes[ii:ps]
            ptimes_idx = np.where(np.logical_and(ds.profile_time >= ptimes[0], ds.profile_time <= ptimes[-1]))[0]
            time0 = np.nanmin(ds.time.values[ptimes_idx])
            time1 = np.nanmax(ds.time.values[ptimes_idx])
            dss = ds.sel(time=slice(time0, time1))
            t0str = pd.to_datetime(np.nanmin(dss.profile_time.values)).strftime('%Y-%m-%dT%H:%M')
            t1str = pd.to_datetime(np.nanmax(dss.profile_time.values)).strftime('%Y-%m-%dT%H:%M')
            t0save = pd.to_datetime(np.nanmin(dss.profile_time.values)).strftime('%Y%m%dT%H%M')
            t1save = pd.to_datetime(np.nanmax(dss.profile_time.values)).strftime('%Y%m%dT%H%M')
            for cv in ctd_vars:
                save_filename = f'{cv}_qc_{t0save}-{t1save}.png'

                data = dss[cv]
                pressure = dss.pressure
                fig, ax = plt.subplots(figsize=(8, 10))

                # iterate through each profile and plot the profile lines
                for pt in ptimes:
                    pt_idx = np.where(dss.profile_time.values == pt)[0]
                    non_nans = np.where(np.invert(np.isnan(pressure[pt_idx])))[0]
                    ax.plot(data[pt_idx][non_nans], pressure[pt_idx][non_nans], color='k')  # plot lines

                # add points
                ax.scatter(data, pressure, color='k', s=20, zorder=5)

                # find the qc variables
                qc_vars = [x for x in ds.data_vars if f'{cv}_' in x]
                if 'conductivity' in cv:
                    qc_vars.append('instrument_ctd_hysteresis_test')

                for qi, qv in enumerate(qc_vars):
                    try:
                        flag_vals = dss[qv].values
                    except KeyError:
                        continue
                    for fd, info in flag_defs.items():
                        qc_idx = np.where(flag_vals == info['value'])[0]
                        if len(qc_idx) > 0:
                            ax.scatter(data[qc_idx], pressure[qc_idx], color=info['color'], s=40,
                                       marker=markers[qi],
                                       label=f'{qv}-{fd}', zorder=10)

                # add legend if necessary
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                if len(handles) > 0:
                    ax.legend(by_label.values(), by_label.keys(), loc='best')

                ax.invert_yaxis()
                ax.set_ylabel('Pressure (dbar)')
                ax.set_xlabel(f'{cv}')
                ttl = f'{glider} {t0str} to {t1str}'
                ax.set_title(ttl)

                sfile = os.path.join(savedir, save_filename)
                plt.savefig(sfile, dpi=300)
                plt.close()


if __name__ == '__main__':
    deployment = 'ru30-20210503T1929'
    f = '/Users/garzio/Documents/rucool/gliders/qartod_qc/from_erddap/ru30-20210503T1929-profile-sci-rt-qc3.nc'
    main(deployment, f)
