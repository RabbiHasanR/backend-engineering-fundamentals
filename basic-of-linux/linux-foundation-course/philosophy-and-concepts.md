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