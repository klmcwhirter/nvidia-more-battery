# NOTES.md

## Simply disable dGPU

### References
* [Linux on the ASUS ROG Zephyrus G14 2021](https://blog.nil.im/?7b)
  - [Optional: Actually secure boot on Fedora](https://blog.nil.im/?7a)
  - [Optional - Actually secure boot on Fedora 39](https://blog.nil.im/?80)
* [tmpfiles.d man page](https://www.freedesktop.org/software/systemd/man/latest/tmpfiles.d.html)
* [Configuration of Temporary Files with systemd-tmpfiles](https://www.baeldung.com/linux/systemd-tmpfiles-configure-temporary-files)

### Run it

To run this use sudo but NOT as a login !

```
$ sudo su
enter creds, etc.
$ pdm start enable --verbose
```

### New adapter method

```python

    NO_NVIDIA_TMPFILE = '/etc/tmpfiles.d/acer_no_gpu.conf'

    @staticmethod
    def delete_no_nvidia():
        os.remove(CachedConfig.NO_NVIDIA_TMPFILE)
        logging.debug(f'Removed {CachedConfig.NO_NVIDIA_TMPFILE}')

    ...

    def write_no_nvidia(self):
        # see find /sys/devices -type d -name '0000:01:00*'
        # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/remove - - - - 1\n',
        # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.1/remove - - - - 1\n',
        tmpfile_content = [
            'd /run/no-nvidia 0755 klmcw klmcw\n',
            'f /run/no-nvidia/in-effect 0644 klmcw klmcw - 1\n'
        ]

        for id in find_nvidia_ids_from_lspci():
            # logging.debug(f'Processing nvidia id={id}')
            for dir in find_nvidia_sys_device_dirs(id):
                tmpfile_content.append(f'w {dir}/remove - - - - 1\n')

        tmpfile_content.append('\n')

        with open(CachedConfig.NO_NVIDIA_TMPFILE, 'w') as f:
            f.writelines(tmpfile_content)
        logging.debug(f'Created {CachedConfig.NO_NVIDIA_TMPFILE}')


def find_nvidia_sys_device_dirs(nvidia_lspci_id):
    output = subprocess.check_output(['find', '/sys/devices', '-type', 'd', '-name', f'{nvidia_lspci_id}.*']).decode('utf-8')
    dirs = [dir for dir in output.splitlines() if 'virtual' not in dir]
    return dirs


def find_nvidia_ids_from_lspci():
    lspci_output = subprocess.check_output(['lspci']).decode('utf-8')
    ids = {line.split('.')[0]
           for line in lspci_output.splitlines()
           if 'NVIDIA' in line}
    return ids
```
