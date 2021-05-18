Name:           spotifyd
Version:        0.3.2
Release:        1
Summary:        spotifyd is an open source client library for Spotify.
License:        MIT
URL:            https://github.com/wdehoog/spotifyd
Source0:        %{name}-%{version}.tar.gz
Source1:        spotifyd.conf
Source2:        spotifyd.service

BuildRequires:  rust
BuildRequires:  rust-std-static
BuildRequires:  cargo
BuildRequires:  pkgconfig(openssl)
BuildRequires:  alsa-lib
BuildRequires:  pulseaudio-devel

Requires:       pulseaudio

%description
Spotifyd streams music just like the official client, but is more lightweight and supports more platforms. Spotifyd also supports the Spotify Connect protocol, which makes it show up as a device that can be controlled from the official clients.

Note: Spotifyd requires a Spotify Premium account.

%prep
%setup -q -n %{name}-%{version}

%build
%ifarch %arm
export SB2_RUST_TARGET_TRIPLE=armv7-unknown-linux-gnueabihf
%endif
%ifarch aarch64
export SB2_RUST_TARGET_TRIPLE=aarch64-unknown-linux-gnu
%endif
export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
export SB2_RUST_USE_REAL_EXECVP=Yes
export SB2_RUST_USE_REAL_FN=Yes
export PKG_CONFIG_ALLOW_CROSS=1

cargo build --verbose --release --target $SB2_RUST_TARGET_TRIPLE --features "pulseaudio_backend, dbus_mpris"

%install

mkdir -p %{buildroot}/%{_bindir}
install ./target/*/release/spotifyd %{buildroot}/%{_bindir}/spotifyd
mkdir -p %{buildroot}/%{_sysconfdir}/pulse/xpolicy.conf.d
install %SOURCE1 %{buildroot}/%{_sysconfdir}/pulse/xpolicy.conf.d/spotifyd.conf
mkdir -p %{buildroot}/%{_userunitdir}
install %SOURCE2 %{buildroot}/%{_userunitdir}/spotifyd.service

%preun
if [ "$1" = "0" ]; then
  systemctl-user stop spotifyd || true
  systemctl-user disable spotifyd || true
fi

# also restart pulseaudio to set audio permissions for spotifyd
%post
systemctl-user daemon-reload || true
systemctl-user enable spotifyd || true
systemctl-user try-restart pulseaudio || true

%pre
if [ "$1" = "2" ]; then
  systemctl-user stop spotifyd || true
  systemctl-user disable spotifyd || true
fi

%files
%defattr(-,root,root)
%{_bindir}/spotifyd
%{_userunitdir}/spotifyd.service
%{_sysconfdir}/pulse/xpolicy.conf.d/spotifyd.conf

