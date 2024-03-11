# nvidia-more-battery
Get battery time back by making usage of nvidia GPU optional for systems with Optimus


## Simply disable dGPU

### References
* [Linux on the ASUS ROG Zephyrus G14 2021](https://blog.nil.im/?7b)
  - [Optional: Actually secure boot on Fedora](https://blog.nil.im/?7a)
  - [Optional - Actually secure boot on Fedora 39](https://blog.nil.im/?80)
* [tmpfiles.d man page](https://www.freedesktop.org/software/systemd/man/latest/tmpfiles.d.html)
* [Configuration of Temporary Files with systemd-tmpfiles](https://www.baeldung.com/linux/systemd-tmpfiles-configure-temporary-files)

### Run it

```
$ pdm create

$ sudo python -m nvidia_more_battery enable --verbose
$ sudo python -m nvidia_more_battery disable --verbose
$ pdm has_nvidia
```

## Approach

The approach taken by the code in this project is outlined in the Linux on the ASUS ROG Zephyrus G14 2021 blog post linked to above.

It is based on some work by the ASUS Linux project.

Instead of blacklisting drivers, it instead leverages the tmpfiles.d infrastructure to disable the hardware by setting a 1 value in the "remove" file for each device as appropriate.

The thing that is so nice about this is that they can be brought back at runtime, from within user space and without a reboot. Nice.

JS writes:
> If you want to get the dGPU back, for example to pass it into a VM, simply rescan the PCIe bus:

`echo 1 | sudo tee /sys/bus/pci/rescan`

## Monitor Power Draw

There is a script in the `etc` directory ([etc/power_mon](etc/power_mon)) to capture some power consumption metrics. It can be executed by:

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

## Scripts

```
╭────────────┬───────┬────────────────────────────────────────────╮
│ Name       │ Type  │ Description                                │
├────────────┼───────┼────────────────────────────────────────────┤
│ start      │ cmd   │ python -m nvidia_more_battery              │
│ has_nvidia │ cmd   │ python -m nvidia_more_battery has_nvidia   │
│ power      │ cmd   │ python -m nvidia_more_battery.power_mon    │
╰────────────┴───────┴────────────────────────────────────────────╯
```

## TODO
- [X] Remove nvidia devices from PCI bus
- ~~[-] Fan profile~~
- ~~[-] Battery charge threshold~~
