**Linux philosophy:**

- **Open collaboration:** Developers worldwide build and maintain it over the Internet, led by Linus Torvalds. Anyone with skills and a willingness to contribute can join.
- **Free and accessible:** It was created as a free, open-source alternative to expensive Unix systems, bringing a Unix-like environment to ordinary personal computers.
- **Built on Unix principles:** It follows Unix's design ideas and architecture without being Unix itself.
- **Everything is a file:** A single filesystem tree starts at root (`/`), and devices, processes and network connections are treated like files, so the same tools work on all of them.
- **Multiuser and multitasking:** Many users can run many processes at the same time on one system.
- **Built for networking:** Networking is built in, and background services called daemons handle system and network tasks.

**One line:** Linux brings Unix's proven design to everyone, for free, and is built openly by a global community.




**Common Linux terms, made simple:**

| Term | Easy explanation | Examples |
|---|---|---|
| **Kernel** | The brain of the OS. It controls the hardware and lets applications talk to it. | Linux kernel (from kernel.org) |
| **Distribution (Distro)** | The kernel plus a bundle of programs, which together make a complete, ready-to-use OS. | Ubuntu, Fedora, Red Hat Enterprise Linux, Gentoo |
| **Boot loader** | The first program that runs when you power on. It loads the OS. | GRUB, ISOLINUX |
| **Service (daemon)** | A program that runs quietly in the background. | httpd (web server), ntpd (time sync), nfsd, ftpd, named (DNS) |
| **Filesystem** | The method Linux uses to store and organize files on disk. | ext3, ext4, XFS, Btrfs, FAT |
| **X Window System** | The base layer that makes graphical screens possible (windows, mouse, display). | X11 (Wayland is the modern replacement) |
| **Desktop environment** | The full graphical interface you see and click on, built on top of the OS. | GNOME, KDE, Xfce, Fluxbox |
| **Terminal** | The window or app that displays the command line. | GNOME Terminal, iTerm, an SSH window |
| **Command line** | The text *interface* where you type commands instead of clicking. | The prompt, like `user@server:~$` |
| **Shell** | The *program* behind the command line. It reads what you type and tells the OS what to do. | bash, zsh, tcsh |

**Command line vs shell:**
The command line is *where* you type. The shell is *who* understands it. When you type `ls -l`, the command line receives the text, and the shell (bash) runs the `ls` program and shows the result.
Analogy: the command line is the phone, and the shell is the person on the other end who listens and acts.

**The full chain:**
**Terminal** (window) → **command line** (where you type) → **shell** (bash/zsh, interprets it) → **kernel** (does the actual work)

**Easy way to remember (house analogy):**
- **Kernel** is the foundation and wiring
- **Distro** is the full house, furnished and ready
- **Boot loader** is the key that opens the front door
- **Services** are the appliances running in the background (fridge, water pump)
- **Filesystem** is the cupboards and shelves where things are kept
- **Desktop environment** is the interior design you see
- **Shell / command line** is talking directly to the house manager





# Linux Startup Process

**Flow:** Power on → BIOS/UEFI → MBR or EFI partition → Boot loader (GRUB) → Kernel + initramfs → `/sbin/init` (systemd) → Login shell (getty) → GUI (X / Wayland)

## Each step in short

**1. Power on → BIOS / UEFI**
Firmware on the motherboard wakes up, runs the **POST** (Power-On Self-Test) to check RAM, CPU and disks, and then looks for a bootable device.
*Example:* the beep or the logo you see when a PC starts. Modern machines use **UEFI**, the newer replacement for BIOS.

**2. MBR or EFI partition**
This is where the firmware finds the boot loader.
- **MBR:** the first 512 bytes of the disk (old BIOS style)
- **EFI System Partition:** a small FAT partition holding `.efi` files (UEFI style)

**3. Boot loader (GRUB)**
GRUB shows the OS menu, then loads **two files into RAM**: the kernel (`vmlinuz`) and the initramfs (`initrd.img`). It then hands control to the kernel.
*Example:* the menu where you choose "Ubuntu" or "Advanced options."

**4. Kernel**
The kernel takes control of the hardware. It sets up memory management and the CPU scheduler, and loads basic drivers. But it has a problem: the real root filesystem may sit on a disk that needs special drivers (RAID, LVM, encryption, NVMe), and those drivers live *on* that disk.

**5. Initial RAM disk (initramfs)**
This solves that problem. The initramfs is a small temporary filesystem in RAM that holds the needed drivers and scripts. It:
- loads the storage drivers
- finds and mounts the **real root filesystem** (`/`)
- switches to it and starts `/sbin/init`

*Example:* if your disk is encrypted, the password prompt at boot comes from the initramfs.

**6. /sbin/init (PID 1)**
This is the first user-space process and the parent of every other process. It starts services, mounts the remaining filesystems, and brings the system to a usable state. On modern distros, `/sbin/init` is actually **systemd**.

**7. getty → command shell**
init starts **getty** on the text consoles, which shows the `login:` prompt. After you log in, your shell (bash) starts.
*Example:* pressing Ctrl+Alt+F3 on a desktop gives you this text login.

**8. Graphical interface (X Window / Wayland)**
On desktop systems, a display manager (like GDM) starts the graphical login and the desktop environment. Servers usually skip this step, as your EC2 instances do.

## How kernel and initramfs work together

GRUB loads **both** into memory. The kernel starts first and unpacks the initramfs as a temporary root. The initramfs prepares the real disk and then steps aside. The kernel keeps running for the entire life of the system, while the initramfs is thrown away once the real root is mounted.

**Analogy:** the kernel is a new manager arriving at an office. The initramfs is a small toolkit they carry in to unlock the main building. Once inside, the toolkit isn't needed anymore.

## SysVinit vs systemd

**SysVinit (old)**
- Started services one by one, in order, using shell scripts in `/etc/init.d/`
- Used numbered **runlevels** (3 = multi-user text, 5 = graphical)
- Slow, because each service waited for the previous one to finish

**systemd (new)**
- Now the default on Ubuntu, Fedora, RHEL, Debian, and most other distros
- Manages services through **unit files**, controlled with `systemctl`
- Uses **targets** instead of runlevels (`multi-user.target`, `graphical.target`)

## Core advantages of systemd

**1. Parallelization**
Independent services start at the same time instead of one after another, so the system boots faster.
*Example:* nginx, Prometheus and the SSH server can all start together if they don't depend on each other.

**2. Declarative configuration**
Instead of writing a shell script that says *how* to start a service, you write a short unit file that says *what* you want, and systemd handles the rest.

```ini
[Unit]
Description=My FastAPI App
After=network.target

[Service]
ExecStart=/usr/bin/gunicorn app:main
Restart=always

[Install]
WantedBy=multi-user.target
```

That `Restart=always` line gives you automatic restart on crash, with no extra scripting.

**3. Dependency handling**
`After=`, `Requires=` and `Wants=` define the order and relationships between services, so systemd knows exactly what to start and when.

**4. Unified management and logging**
One tool controls everything (`systemctl start/stop/status/enable`), and logs are collected centrally through `journalctl`.

**5. On-demand starting**
Services can start only when they're needed (for example, when a connection arrives on a socket), which saves resources.

## One-line summary

Firmware finds the boot loader, the boot loader loads the kernel and initramfs, the initramfs prepares the real disk, systemd (PID 1) starts all services in parallel, and you get a login prompt or a desktop.


## Common Linux filesystem types: Conventional disk filesystems, flash storage filesystems, special purpose filesystems, database filesystems


## Linux Filesystem hierarchy Standard: /, /home, /root, /etc, /bin and /usr/bin, /sbin and /usr/sbin, 
## /bin and /usr/lib, /var, /tmp, /dev, /proc, /sys, /boot, /run

key subdirectories of /usr

/usr/bin,/usr/bin, /usr/lib, /usr/share, /usr/local


A partition is a logical part of the disk.

By dividing the hard disk into partitions, data can be grouped and separated as needed. When a failure or mistake occurs, only the data in the affected partition will be damaged, while the data on the other partitions will likely survive.

Determining the appropriate distribution to deploy requires that you match your specific system needs to the capabilities of the different distributions.