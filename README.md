
# openvpn-cmd
A Linux wrapper for OpenVPN to simplify starting/stopping/managing VPN connections

It runs openvpn inside a "screen" window.
Download the .ovpn files to the 'cfg' directory.
It was made to use with KeepSolid VPN but could be used with any
VPN provider for which you have OpenVPN configuration files.
For convenience run through sudo or add openvpn to the sudoers file.

It runs on Linux and relies on OS tools such as openvpn, screen and dig.
It integrates well with my [OpenVPN controller](https://github.com/jrmdev/plugin.video.openvpn-controller) Kodi Add-On, to manage your VPN 
connections from your media center, for example for streaming foreign content.

To install, make the script executable and symlink to it.

    chmod a+x openvpn-cmd.py
    ln -s /full/path/to/openvpn-cmd.py /usr/local/bin/vpn
