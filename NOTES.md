# NOTES.md

## Simply disable dGPU

### References
* [Linux on the ASUS ROG Zephyrus G14 2021](https://blog.nil.im/?7b)
  - [Optional: Actually secure boot on Fedora](https://blog.nil.im/?7a)
  - [Optional - Actually secure boot on Fedora 39](https://blog.nil.im/?80)
* [tmpfiles.d man page](https://www.freedesktop.org/software/systemd/man/latest/tmpfiles.d.html)
* [Configuration of Temporary Files with systemd-tmpfiles](https://www.baeldung.com/linux/systemd-tmpfiles-configure-temporary-files)

### TODO
- [X] Remove nvidia devices from PCI bus
- [ ] Fan profile ?
- [ ] Battery charge threshold ?

### Run it

To run this use sudo but NOT as a login !

```
$ pdm install
$ sudo su
enter creds, etc.
$ pdm start enable --verbose
```

## Approach

The approach taken by the code in this project is outlined in the Linux on the ASUS ROG Zephyrus G14 2021 blog post linked to above.

It is based on some work by the ASUS Linux project.

Instead of blacklisting drivers, it instead leverages the tmpfiles.d infrastructure to disable the hardware by setting a 1 value in the "remove" file for each device as appropriate.

The thing that is so nice about this is that they can be brought back at runtime, from within user space and without a reboot. Nice.

JS writes:
> If you want to get the dGPU back, for example to pass it into a VM, simply rescan the PCIe bus:

`echo 1 | sudo tee /sys/bus/pci/rescan`

