# nvidia-more-battery
> [!CAUTION]
> This approach does not seem to work with older or newer NVIDIA GPUs.
> 
> In addition, it is tightly coupled to `systemd` via its use of the `tmpfiles.d` feature.
> 
> Also, the reloading of PCI devices without reboot is unstable in practice. Just don't try to rely upon it.
> 
> As such, I have archived this repo.

Get battery time back by making usage of nvidia GPU optional for systems with Optimus

[![Tests](https://github.com/klmcwhirter/nvidia-more-battery/actions/workflows/tests.yml/badge.svg)](https://github.com/klmcwhirter/nvidia-more-battery/actions/)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-green.svg)](https://github.com/pycqa/flake8)
[![Code Analysis: mypy](https://img.shields.io/badge/code%20analysis-mypy-blue.svg)](https://github.com/python/mypy)
![Tox Versions](https://img.shields.io/badge/tox-v4-yellowgreen)
![NVIDIA](https://img.shields.io/badge/nvidia-optimus-76B900?logo=NVIDIA)
![systemd](https://img.shields.io/badge/linux-systemd-FCC624?logo=Linux)
![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fklmcwhirter%2Fnvidia-more-battery%2Fmaster%2Fpyproject.toml&logo=Python)

## Simply disable dGPU

### References
* [Linux on the ASUS ROG Zephyrus G14 2021](https://blog.nil.im/?7b)
  - [Optional: Actually secure boot on Fedora](https://blog.nil.im/?7a)
  - [Optional - Actually secure boot on Fedora 39](https://blog.nil.im/?80)
* [tmpfiles.d man page](https://www.freedesktop.org/software/systemd/man/latest/tmpfiles.d.html)
* [Configuration of Temporary Files with systemd-tmpfiles](https://www.baeldung.com/linux/systemd-tmpfiles-configure-temporary-files)

### Nvidia Driver References
* [How to Install NVIDIA Drivers on Fedora 39, 38 Linux](https://www.linuxcapable.com/how-to-install-nvidia-drivers-on-fedora-linux/)
* [NVIDIA XFree86 README](http://us.download.nvidia.com/XFree86/Linux-x86_64/550.67/README/index.html)
* [Chapter 17. Using the NVIDIA Driver with Optimus Laptops](http://us.download.nvidia.com/XFree86/Linux-x86_64/550.67/README/optimus.html)
* [Chapter 35. PRIME Render Offload](http://us.download.nvidia.com/XFree86/Linux-x86_64/550.67/README/primerenderoffload.html)
* [archwiki PRIME](https://wiki.archlinux.org/title/PRIME)
* [archwiki NVIDIA](https://wiki.archlinux.org/title/NVIDIA)

### Run it

First install `pdm`. See https://pdm-project.org/latest/#recommended-installation-method.

```
$ pdm create

$ pdm enable  # create the tmpfiles.d file to "enable" the feature; reboot required
$ pdm disable  # remove the tmpfiles.d file and cause the pci bus to be rescanned; NO reboot required
$ pdm has_nvidia
```

## Approach

The approach taken by the code in this project is outlined in the [Linux on the ASUS ROG Zephyrus G14 2021](https://blog.nil.im/?7b) blog post linked to above.

It is based on some work by the ASUS Linux project.

Instead of blacklisting drivers, it leverages the systemd tmpfiles.d infrastructure to disable the hardware by setting a 1 value in the "remove" file for each device as appropriate.

> Note there are other ways to accomplish this on Linux without systemd, but it needs to happen early enough in the boot process to influence kernel behavior.

The thing that is so nice about this is that the items deconfigured from the PCIe bus can be brought back at runtime, from within user space and without a reboot. Nice.

JS writes:
> If you want to get the dGPU back, for example to pass it into a VM, simply rescan the PCIe bus:

`echo 1 | sudo tee /sys/bus/pci/rescan`

## Monitor Power Draw

Since my persoinal goal is improvement of battery life, I thought it important to have a simple way to monitor power drain and battery time remaining.

There is a script ([nvidia_more_battery/power_mon.py](nvidia_more_battery/power_mon.py)) to capture some power consumption metrics. It can be executed by:

```bash
$ pdm power  # output to stdout

$ pdm power start  # output to /run/no-nvidia/battery_test_start.txt
$ pdm power stop   # output to /run/no-nvidia/battery_test_stop.txt

```

If your battery is other than BAT1, then specify the full path to the uevent file on your system.

```bash
$ pdm power stdout /sys/class/power_supply/BAT0/uevent # output to stdout

$ pdm power start /sys/class/power_supply/BAT0/uevent  # output to /run/no-nvidia/battery_test_start.txt
$ pdm power stop /sys/class/power_supply/BAT0/uevent   # output to /run/no-nvidia/battery_test_stop.txt

```

### Sample output

```json
{
  "timestamp": "2024-03-10T06:04:39.220894",
  "source": "/sys/class/power_supply/BAT1/uevent",
  "target": "/run/no-nvidia/battery_test_start.txt",
  "power": "1.54 W",
  "energy": "0.38 Ah",
  "draw": "0.09 A",
  "charging": false,
  "capacity": "99%",
  "time_rem": "(252.69) 4 hr(s) 12 mins"
}
```
> Note that I am consistently getting 4 to 4-1/2 hr battery life using this approach.

## Scripts

```
╭────────────┬───────────┬─────────────────────────────────────────────────────────────────╮
│ Name       │ Type      │ Description                                                     │
├────────────┼───────────┼─────────────────────────────────────────────────────────────────┤
│ disable    │ shell     │ Disable nvidia limiting feature and rescan PCI bus; no reboot   │
│ enable     │ shell     │ Enable nvidia limiting feature; reboot is required              │
│ has_nvidia │ composite │ report nvidia is available or not - outputs nvidia or no-nvidia │
│ power      │ cmd       │ python -m ${NVB}.power_mon                                      │
╰────────────┴───────────┴─────────────────────────────────────────────────────────────────╯
```

## TODO
- [X] Remove nvidia devices from PCI bus
- ~~[-] Fan profile~~
- ~~[-] Battery charge threshold~~
