# Since RHEL-5, QEMU is restricted to x86_64 only
# As Boxes don't really handle the !qemu case very well (untested, the 'box
# creation' UI would still be there but non-functional, ...), better to
# only build Boxes on platforms where qemu/qemu-kvm are available
%if 0%{?rhel}
ExclusiveArch:        x86_64
%endif


# The following qemu_kvm_arches/with_qemu_kvm defines come from
# libvirt.spec
%if 0%{?fedora}
    %global qemu_kvm_arches %{ix86} x86_64 %{power64} s390x %{arm} aarch64
    %global distributor_name fedora
    %global distributor_version %{fedora}
%endif

%if 0%{?rhel} >= 7
    %global qemu_kvm_arches    x86_64 %{power64}
    %global distributor_name rhel
    %global distributor_version %{rhel}
%endif

%ifarch %{qemu_kvm_arches}
    %global with_qemu_kvm      1
%else
    %global with_qemu_kvm      0
%endif

%global url_ver	%%(echo %{version}|cut -d. -f1,2)

Name:                 gnome-boxes
Version:              3.36.5
Release:              8%{?dist}.openela.0.1
Summary:              A simple GNOME 3 application to access remote or virtual systems

License:              LGPLv2+
URL:                  https://wiki.gnome.org/Apps/Boxes
Source0:              http://download.gnome.org/sources/%{name}/%{url_ver}/%{name}-%{version}.tar.xz

# https://bugzilla.redhat.com/1851089
Patch0:               gnome-boxes-download-from-url.patch
# https://bugzilla.redhat.com/1851043
Patch1:               gnome-boxes-dont-be-critical.patch
# https://bugzilla.redhat.com/1856717
Patch2:               gnome-boxes-disable-3d-acceleration.patch
Patch3:               gnome-boxes-download-on-activate-signal.patch
# https://bugzilla.redhat.com/1639163
Patch4:               gnome-boxes-fix-mixing-vm-widgets.patch
# https://bugzilla.redhat.com/1152037
Patch5:               gnome-boxes-pass-discard-unmap-to-disk.patch
Patch6:               add-openela-logo-and-update-recommended-list.patch

BuildRequires:        gettext >= 0.19.8
BuildRequires:        meson
BuildRequires:        vala >= 0.36.0
BuildRequires:        yelp-tools
BuildRequires:        pkgconfig(clutter-gtk-1.0)
BuildRequires:        pkgconfig(freerdp2)
BuildRequires:        pkgconfig(glib-2.0) >= 2.52
BuildRequires:        pkgconfig(gobject-introspection-1.0)
BuildRequires:        pkgconfig(gtk+-3.0) >= 3.22.20
BuildRequires:        pkgconfig(gtk-vnc-2.0)
BuildRequires:        pkgconfig(libarchive)
BuildRequires:        pkgconfig(json-glib-1.0)
BuildRequires:        pkgconfig(libsecret-1)
BuildRequires:        pkgconfig(libvirt-gobject-1.0)
BuildRequires:        pkgconfig(libvirt-gconfig-1.0)
BuildRequires:        pkgconfig(libxml-2.0)
BuildRequires:        pkgconfig(gudev-1.0)
BuildRequires:        pkgconfig(libosinfo-1.0) >= 1.2.0
BuildRequires:        pkgconfig(libsoup-2.4) >= 2.44
BuildRequires:        pkgconfig(libusb-1.0)
BuildRequires:        pkgconfig(tracker-sparql-2.0)
BuildRequires:        pkgconfig(vte-2.91)
BuildRequires:        pkgconfig(webkit2gtk-4.0)
BuildRequires:        spice-gtk3-vala
BuildRequires:        libosinfo-vala
BuildRequires:        desktop-file-utils

# See https://bugzilla.redhat.com/1052945
Recommends:           openssh-askpass

# Pulls in libvirtd + KVM, but no NAT / firewall configs
%if %{with_qemu_kvm}
Requires:             libvirt-daemon-kvm
%else
Requires:             libvirt-daemon-qemu
%endif

# Pulls in the libvirtd NAT 'default' network
# Original request: https://bugzilla.redhat.com/show_bug.cgi?id=1081762
#
# However, the 'default' network does not mix well with the Fedora livecd
# when it is run inside a VM. The whole saga is documented here:
#
#   boxes: https://bugzilla.redhat.com/show_bug.cgi?id=1164492
#   libvirt: https://bugzilla.redhat.com/show_bug.cgi?id=1146232
#
# Until a workable solution has been determined and implemented, this
# dependency should stay disabled in rawhide and fedora development
# branches so it does not end up on the livecd. Once a Fedora GA is
# released, a gnome-boxes update can be pushed with this dependency
# re-enabled. crobinso will handle this process, see:
#
#    https://bugzilla.redhat.com/show_bug.cgi?id=1164492#c71
Requires:             libvirt-daemon-config-network

# Needed for unattended installations
Requires:             mtools
Requires:             genisoimage

Requires:             adwaita-icon-theme

%description
gnome-boxes lets you easily create, setup, access, and use:
  * remote machines
  * remote virtual machines
  * local virtual machines
  * When technology permits, set up access for applications on
    local virtual machines

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
%meson \
%if %{?distributor_name:1}%{!?distributor_name:0}
    -D distributor_name=%{distributor_name} \
%endif
%if 0%{?distributor_version}
    -D distributor_version=%{distributor_version} \
%endif

%meson_build

%install
%meson_install
%find_lang %{name} --with-gnome

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.gnome.Boxes.desktop

%files -f %{name}.lang
%license COPYING
%doc AUTHORS README.md NEWS
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_includedir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/org.gnome.Boxes.desktop
%{_datadir}/glib-2.0/schemas/org.gnome.boxes.gschema.xml
%{_datadir}/icons/hicolor/*/apps/org.gnome.Boxes.svg
%{_datadir}/icons/hicolor/symbolic/apps/org.gnome.Boxes-symbolic.svg
%{_libexecdir}/gnome-boxes-search-provider
%{_datadir}/dbus-1/services/org.gnome.Boxes.SearchProvider.service
%{_datadir}/dbus-1/services/org.gnome.Boxes.service
%dir %{_datadir}/gnome-shell
%dir %{_datadir}/gnome-shell/search-providers
%{_datadir}/gnome-shell/search-providers/org.gnome.Boxes.SearchProvider.ini
%{_datadir}/metainfo/org.gnome.Boxes.appdata.xml

%changelog
* Thu Jan 25 2024 Release Engineering <releng@openela.org> - 3.36.5.openela.0.1
- Add OpenELA logo and update recommended list

* Mon Nov 02 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-8
- Pass discard "unmap" to supported disk drivers
- Related: #1152037

* Mon Nov 02 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-7
- Fix mixing VM widgets
- Related: #1639163

* Mon Aug 10 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-6
- Start downloads on the Assistant when pressing ENTER
- Related: #1851089

* Mon Jul 13 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-5
- Disable 3D acceleration
- Related: #1856717

* Tue Jun 30 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-4
- Don't create a tooltip if the URL for the OS is null
- Related: #1851043

* Wed Jun 24 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-3
- Allow pasting URLs in the Assistant "Download an OS" search
- Related: #1851089

* Mon Jun 22 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-2
- Recommend openssh-askpass
- Related: #1052945

* Thu Jun 11 2020 Felipe Borges <feborges@redhat.com> - 3.36.5-1
- Rebase to 3.36.5

* Tue Jan 21 2020 Felipe Borges <feborges@redhat.com> - 3.28.5-8
- Present undetected OSes
- Related: #1793413

* Thu Aug 15 2019 Felipe Borges <feborges@redhat.com> - 3.28.5-7
- Bump the release to 3.28.5-7
- Related: #1739897

* Thu Aug 15 2019 Felipe Borges <feborges@redhat.com> - 3.28.5-7
- Filter off unsupported architectures
- Related: #1739897

* Mon Jun 17 2019 Fabiano Fidêncio <fidencio@redhat.com> - 3.28.5-6
- Revert "Add 3D acceleration option (powered by virgl)"
- Related: #1647004

* Mon Jun 03 2019 Felipe Borges <feborges@redhat.com> - 3.28.5-5
- Add 3D acceleration option (powered by virgl)
- Resolves: #1647004

* Thu May 23 2019 Fabiano Fidêncio <fidencio@redhat.com> - 3.28.5-4
- Add rhel-8.0 logo & update logo for rhel-4.0 & update recommendations
- Resolves: #1713130

* Wed Dec 05 2018 Felipe Borges <feborges@redhat.com> - 3.28.5-3
- Pick our recommended downloads
- Related #1656446

* Mon Oct 15 2018 Felipe Borges <feborges@redhat.com> - 3.28.5-2
- Use q35 for machine type
- Related #1581422

* Fri Jun 08 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.28.5-1
- Update to 3.28.5

* Wed May 09 2018 Kalev Lember <klember@redhat.com> - 3.28.4-1
- Update to 3.28.4

* Tue May 08 2018 Kalev Lember <klember@redhat.com> - 3.28.3-1
- Update to 3.28.3

* Mon Apr 30 2018 Cole Robinson <crobinso@redhat.com> - 3.28.2-1.fc28.1
- Re-enable libvirt-daemon-config-network dep, see bz 1164492#c71

* Tue Apr 10 2018 Kalev Lember <klember@redhat.com> - 3.28.2-1
- Update to 3.28.2

* Mon Apr 09 2018 Kalev Lember <klember@redhat.com> - 3.28.1-1
- Update to 3.28.1

* Mon Mar 26 2018 Adam Williamson <awilliam@redhat.com> - 3.27.92-2.fc28.1
- Disable libvirt-daemon-config-network dep until GA (#1164492)

* Mon Mar 12 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.27.92-2
- Override the user agent for Fedora and RHEL

* Mon Mar 05 2018 Kalev Lember <klember@redhat.com> - 3.27.92-1
- Update to 3.27.92
- Switch to the meson build system

* Mon Feb 19 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.27.2-1
- Update to 3.27.2

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.27.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 08 2018 Björn Esser <besser82@fedoraproject.org> - 3.27.1-4
- Prefer %%global over %%define as indicated by guidelines

* Mon Jan 08 2018 Björn Esser <besser82@fedoraproject.org> - 3.27.1-3
- Add a patch making newly created VMs use VIRTIO
- Resolves: rhbz#1491320

* Fri Jan 05 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 3.27.1-2
- Remove obsolete scriptlets

* Tue Nov 21 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.27.1-1
- Update to 3.27.1

* Wed Nov 01 2017 Kalev Lember <klember@redhat.com> - 3.26.2-1
- Update to 3.26.2

* Thu Oct 12 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.26.1-2
- Add the RHEL Developer Suite patches (GNOME #786679)

* Sun Oct 08 2017 Kalev Lember <klember@redhat.com> - 3.26.1-1
- Update to 3.26.1

* Wed Sep 13 2017 Kalev Lember <klember@redhat.com> - 3.26.0-1
- Update to 3.26.0

* Wed Aug 23 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.25.91-1
- Update to 3.25.91

* Tue Aug 01 2017 Kalev Lember <klember@redhat.com> - 3.25.4-1
- Update to 3.25.4

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.25.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Jun 25 2017 Kalev Lember <klember@redhat.com> - 3.25.3-1
- Update to 3.25.3

* Mon Jun 12 2017 Kalev Lember <klember@redhat.com> - 3.25.2-1
- Update to 3.25.2

* Tue Mar 21 2017 Kalev Lember <klember@redhat.com> - 3.24.0-1
- Update to 3.24.0

* Tue Feb 28 2017 Richard Hughes <rhughes@redhat.com> - 3.23.91-1
- Update to 3.23.91

* Mon Feb 06 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.23.4.1-1
- Update to 3.23.4.1

* Thu Nov 24 2016 Kalev Lember <klember@redhat.com> - 3.23.2-1
- Update to 3.23.2

* Sat Nov 05 2016 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-1
- Update to 3.22.2

* Fri Nov 04 2016 Kalev Lember <klember@redhat.com> - 3.22.1-2
- Re-add libvirt-daemon-config-network dep (#1164492)

* Wed Oct 12 2016 Kalev Lember <klember@redhat.com> - 3.22.1-1
- Update to 3.22.1

* Thu Sep 22 2016 Kalev Lember <klember@redhat.com> - 3.22.0-2
- BR vala instead of obsolete vala-tools subpackage

* Wed Sep 21 2016 Kalev Lember <klember@redhat.com> - 3.22.0-1
- Update to 3.22.0

* Fri Sep 16 2016 Kalev Lember <klember@redhat.com> - 3.21.92-1
- Update to 3.21.92
- Drop unrecognized configure options
- Don't set group tags

* Wed Jun 22 2016 Richard Hughes <rhughes@redhat.com> - 3.21.3-1
- Update to 3.21.3

* Wed Jun 22 2016 Marc-André Lureau <mlureau@redhat.com> - 3.20.2-4
- Rebuild to pick spice-gtk 0.32 ABI break

* Mon Jun 13 2016 Christophe Fergeau <cfergeau@redhat.com> - 3.20.2-3
- Added upstream patch to avoid showing privilege elevation dialog at
  every Boxes startup (it's only needed if one wants to import system
  VMs)

* Wed May 25 2016 Kalev Lember <klember@redhat.com> - 3.20.2-2
- Temporarily remove libvirt-daemon-config-network dep (#1164492)

* Mon May 09 2016 Kalev Lember <klember@redhat.com> - 3.20.2-1
- Update to 3.20.2

* Tue Mar 22 2016 Kalev Lember <klember@redhat.com> - 3.20.0-1
- Update to 3.20.0

* Wed Mar 16 2016 Kalev Lember <klember@redhat.com> - 3.19.92-1
- Update to 3.19.92

* Fri Mar 04 2016 Kalev Lember <klember@redhat.com> - 3.19.91-1
- Update to 3.19.91

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Kalev Lember <klember@redhat.com> - 3.19.4-1
- Update to 3.19.4

* Thu Dec 17 2015 Kalev Lember <klember@redhat.com> - 3.19.3-1
- Update to 3.19.3

* Wed Oct 28 2015 Kalev Lember <klember@redhat.com> - 3.19.1-1
- Update to 3.19.1

* Mon Oct 12 2015 Kalev Lember <klember@redhat.com> - 3.18.1-1
- Update to 3.18.1

* Tue Sep 22 2015 Kalev Lember <klember@redhat.com> - 3.18.0-1
- Update to 3.18.0
- Update URL

* Tue Sep 01 2015 Kalev Lember <klember@redhat.com> - 3.17.91-1
- Update to 3.17.91

* Tue Aug 18 2015 Kalev Lember <klember@redhat.com> - 3.17.90-1
- Update to 3.17.90
- Use make_install macro

* Tue Jun 30 2015 Kalev Lember <klember@redhat.com> - 3.17.3-1
- Update to 3.17.3

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.17.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 28 2015 Zeeshan Ali <zeenix@redhat.com> - 3.17.2-1
- Update to 3.17.2
- Update dependencies.

* Fri May 01 2015 Kalev Lember <kalevlember@gmail.com> - 3.17.1-1
- Update to 3.17.1
- Include the symbolic icon

* Thu Apr 16 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.1-1
- Update to 3.16.1

* Tue Mar 24 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.0-1
- Update to 3.16.0

* Tue Mar 17 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.92-1
- Update to 3.15.92

* Tue Mar 03 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.91-1
- Update to 3.15.91
- Use the %%license macro for the COPYING file

* Thu Feb 19 2015 Richard Hughes <rhughes@redhat.com> - 3.15.90-1
- Update to 3.15.90

* Thu Jan 22 2015 Richard Hughes <rhughes@redhat.com> - 3.15.4-1
- Update to 3.15.4

* Fri Dec 19 2014 Richard Hughes <rhughes@redhat.com> - 3.15.3-1
- Update to 3.15.3

* Tue Nov 25 2014 Kalev Lember <kalevlember@gmail.com> - 3.15.2-1
- Update to 3.15.2

* Wed Nov 12 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.2-1
- Update to 3.14.2

* Tue Nov 04 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1.2-1
- Update to 3.14.1.2

* Wed Oct 15 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1.1-1
- Update to 3.14.1.1

* Mon Oct 13 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1-1
- Update to 3.14.1

* Thu Oct  2 2014 Zeeshan Ali <zeenix@redhat.com> 3.14.0-3
- Remove now unneeded deps on fuseiso and genisoimage.

* Wed Sep 24 2014 Peter Robinson <pbrobinson@fedoraproject.org> 3.14.0-2
- Update KVM arches

* Tue Sep 23 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.0-1
- Update to 3.14.0

* Tue Sep 16 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.92-1
- Update to 3.13.92
- Adapt packaging for the desktop file rename

* Wed Sep 03 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.91-1
- Update to 3.13.91

* Tue Aug 26 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.90-1
- Update to 3.13.90

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.13.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jul 21 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.4-1
- Update to 3.13.4

* Fri Jun 27 2014 Bastien Nocera <bnocera@redhat.com> 3.13.3-2
- Don't run update-mime-database in post, we don't ship mime XML
  files anymore

* Wed Jun 25 2014 Richard Hughes <rhughes@redhat.com> - 3.13.3-1
- Update to 3.13.3

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.12.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon May 26 2014 Matthias Clasen <mclasen@redhat.com> - 3.12.2-2
- Require adwaita-icon-theme. Its the default

* Thu May 15 2014 Kalev Lember <kalevlember@gmail.com> - 3.12.2-1
- Update to 3.12.2

* Wed Apr 16 2014 Kalev Lember <kalevlember@gmail.com> - 3.12.1-1
- Update to 3.12.1

* Mon Mar 31 2014 Zeeshan Ali <zeenix@redhat.com> - 3.12.0-2
- Add dep on libvirt-daemon-config-network to fix rhbz#1081762.

* Mon Mar 24 2014 Richard Hughes <rhughes@redhat.com> - 3.12.0-1
- Update to 3.12.0

* Wed Mar 19 2014 Richard Hughes <rhughes@redhat.com> - 3.11.92-1
- Update to 3.11.92

* Tue Mar 04 2014 Richard Hughes <rhughes@redhat.com> - 3.11.91-1
- Update to 3.11.91

* Thu Feb 20 2014 Kalev Lember <kalevlember@gmail.com> - 3.11.90.1-2
- Rebuilt for cogl soname bump

* Wed Feb 19 2014 Richard Hughes <rhughes@redhat.com> - 3.11.90.1-1
- Update to 3.11.90.1

* Tue Feb 18 2014 Richard Hughes <rhughes@redhat.com> - 3.11.90-1
- Update to 3.11.90

* Mon Feb 10 2014 Peter Hutterer <peter.hutterer@redhat.com> - 3.11.5.1-2
- Rebuild for libevdev soname bump

* Thu Feb 06 2014 Kalev Lember <kalevlember@gmail.com> - 3.11.5.1-1
- Update to 3.11.5.1

* Wed Feb 05 2014 Kalev Lember <kalevlember@gmail.com> - 3.11.5-2
- Rebuilt for cogl soname bump

* Wed Feb 05 2014 Richard Hughes <rhughes@redhat.com> - 3.11.5-1
- Update to 3.11.5

* Wed Jan 15 2014 Richard Hughes <rhughes@redhat.com> - 3.11.4-1
- Update to 3.11.4

* Tue Dec 17 2013 Richard Hughes <rhughes@redhat.com> - 3.11.3-1
- Update to 3.11.3

* Wed Dec 04 2013 Christophe Fergeau <cfergeau@redhat.com> 3.11.2-2
- Rebuild against new libgovirt release

* Mon Nov 25 2013 Richard Hughes <rhughes@redhat.com> - 3.11.2-1
- Update to 3.11.2

* Thu Nov 14 2013 Richard Hughes <rhughes@redhat.com> - 3.10.2-1
- Update to 3.10.2

* Wed Sep 25 2013 Kalev Lember <kalevlember@gmail.com> - 3.10.0-1
- Update to 3.10.0

* Wed Sep 18 2013 Kalev Lember <kalevlember@gmail.com> - 3.9.92-1
- Update to 3.9.92

* Mon Sep 09 2013 Zeeshan Ali <zeenix@redhat.com> - 3.9.91.1-1
- Update to 3.9.91.1
- Fix vala and gtk+ dependency

* Tue Sep 03 2013 Kalev Lember <kalevlember@gmail.com> - 3.9.91-1
- Update to 3.9.91

* Fri Aug 09 2013 Kalev Lember <kalevlember@gmail.com> - 3.9.3-4
- Rebuilt for cogl 1.15.4 soname bump

* Wed Aug 07 2013 Christophe Fergeau <cfergeau@redhat.com> 3.9.3-3
- Add Requires on dconf and gnome-themes-standard, fixes rhbz#978727

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 16 2013 Richard Hughes <rhughes@redhat.com> - 3.9.3-1
- Update to 3.9.3

* Tue May 28 2013 Zeeshan Ali <zeenix@redhat.com> - 3.9.2-1
- Update to 3.9.2.

* Mon May 27 2013 Kalev Lember <kalevlember@gmail.com> 3.8.2-5
- Only pull in qemu on non-kvm arches

* Fri May 24 2013 Christophe Fergeau <cfergeau@redhat.com> 3.8.2-4
- ... and remove again the ExclusiveArch on fedora. If libvirt-daemon-qemu
  is available, this means we can create (very slow) x86 boxes regardless
  of the arch

* Thu May 23 2013 Christophe Fergeau <cfergeau@redhat.com> 3.8.2-3
- Readd ExclusiveArch as Boxes is not really functional on non-x86
  arch even if it can be built. Also, libvirt-daemon-kvm is not
  available on every arch, causing rhbz#962325

* Thu May 16 2013 Christophe Fergeau <cfergeau@redhat.com> 3.8.2-2
- Add upstream patch for rhbz#963464

* Tue May 14 2013 Zeeshan Ali <zeenix@redhat.com> - 3.8.2-1
- Update to 3.8.2.

* Thu Apr 18 2013 Christophe Fergeau <cfergeau@redhat.com> 3.8.1.2-1
- Update to 3.8.1.2

* Tue Apr 16 2013 Richard Hughes <rhughes@redhat.com> - 3.8.1-1
- Update to 3.8.1

* Tue Apr 02 2013 Christophe Fergeau <cfergeau@redhat.com> 3.8.0-2
- Enable smartcard support and oVirt support

* Tue Mar 26 2013 Richard Hughes <rhughes@redhat.com> - 3.8.0-1
- Update to 3.8.0

* Wed Mar 20 2013 Richard Hughes <rhughes@redhat.com> - 3.7.92-1
- Update to 3.7.92

* Fri Mar  8 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.91-1
- Update to 3.7.91

* Thu Feb 21 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.90-2
- Rebuilt for cogl soname bump

* Thu Feb 21 2013 Christophe Fergeau <cfergeau@redhat.com> 3.7.90-1
- Update do 3.7.90

* Wed Feb 06 2013 Richard Hughes <rhughes@redhat.com> - 3.7.5-1
- Update to 3.7.5

* Sun Jan 27 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.4-3
- Rebuilt for tracker 0.16 ABI

* Fri Jan 25 2013 Peter Robinson <pbrobinson@fedoraproject.org> 3.7.4-2
- Rebuild for new cogl

* Tue Jan 15 2013 Zeeshan Ali <zeenix@redhat.com> - 3.7.4-1
- Update to 3.7.4.

* Thu Dec 20 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.7.3-1
- Update to 3.7.3

* Tue Nov 20 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.7.2-2
- Reenable USB redirection (it's disabled by default, packagers must
  enable it if appropriate)

* Tue Nov 20 2012 Zeeshan Ali <zeenix@redhat.com> - 3.7.2-1
- Update to 3.7.2.

* Tue Nov 13 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.6.2-2
- Update to 3.6.2

* Tue Oct 16 2012 Zeeshan Ali <zeenix@redhat.com> - 3.6.1.1-2
- Enable USB redirection in new domains.

* Tue Oct 16 2012 Zeeshan Ali <zeenix@redhat.com> - 3.6.1.1-1
- Update to 3.6.1.1

* Mon Oct 15 2012 Zeeshan Ali <zeenix@redhat.com> - 3.6.1-1
- Update to 3.6.1

* Tue Sep 25 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.6.0-1
- Update to 3.6.0

* Wed Sep 19 2012 Richard Hughes <hughsient@gmail.com> - 3.5.92-1
- Update to 3.5.92

* Thu Sep  6 2012 Matthias Clasen <mclasen@redhat.com> - 3.5.91-2
- Rebuild against new spice

* Tue Sep 04 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.5.91-1
- Update do 3.5.91

* Wed Aug 22 2012 Richard Hughes <hughsient@gmail.com> - 3.5.90-1
- Update to 3.5.90

* Tue Aug 07 2012 Richard Hughes <hughsient@gmail.com> - 3.5.5-1
- Update to 3.5.5

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.5.4.1-1
- Update to 3.5.4.1

* Mon Jul 16 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.5.4-1
- Update to 3.5.4
- Update some BuildRequires min version

* Tue Jun 26 2012 Richard Hughes <hughsient@gmail.com> - 3.5.3-1
- Update to 3.5.3

* Thu Jun 07 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.5.2-2
- enable logos after getting confirmation this has been approved by
  fedora-legal and the Fedora board

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 3.5.2-1
- Update to 3.5.2

* Wed May 16 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.4.2-2
- Remove ExclusiveArch now that spice-gtk is built on all arch

* Tue May 15 2012 Zeeshan Ali <zeenix@redhat.com> - 3.4.2-1
- Update to 3.4.2

* Thu Apr 26 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.4.1-2
- Backport a few upstream patches:
  - asynchronously fetch domain information from libvirt, this makes Boxes
    much more responsive
  - make the file chooser dialog modal
  - fix f17 unattended installation

* Tue Apr 17 2012 Richard Hughes <hughsient@gmail.com> - 3.4.1-1
- Update to 3.4.1

* Sat Mar 31 2012 Daniel P. Berrange <berrange@redhat.com> - 3.4.0.1-2
- Only pull in libvirtd + KVM drivers, without default configs (bug 802475)

* Sat Mar 31 2012 Zeeshan Ali <zeenix@redhat.com> - 3.4.0.1-1
- Update to 3.4.0.1

* Mon Mar 26 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.4.0-1
- Update to 3.4.0

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> - 3.3.92-2
- set ExclusiveArch equal to spice-gtk

* Tue Mar 20 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.92-1
- Update to 3.3.92

* Tue Mar  6 2012 Matthias Clasen <mclasen@redhat.com> - 3.3.91-1
- Update to 3.3.91

* Sun Feb 26 2012 Matthias Clasen <mclasen@redhat.com> - 3.3.90-1
- Update to 3.3.90

* Wed Feb 08 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.5.1-1
- Update to 3.3.5.1

* Wed Jan 25 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.4.1-1
- Update to minor 3.3.4.1 release

* Fri Jan 20 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.4-4
- call desktop-file-validate in %%install. gnome-boxes upstream installs
  a .desktop file on its own so desktop-file-validate is enough, no need
  to call desktop-file-install.

* Fri Jan 20 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.4-3
- Fix %%global use (%%url_ver got expanded to 3.3.4 instead of 3.3 in
  -2)

* Tue Jan 17 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.4-2
- Remove use of BuildRoot
- Remove use of defattr
- Use %%global instead of %%define

* Tue Jan 17 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.4-1
- Update to 3.3.4 release

* Thu Jan 05 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.3-3
- Escape %%{buildroot} in changelog
- Remove empty %%pre section

* Wed Jan 04 2012 Christophe Fergeau <cfergeau@redhat.com> - 3.3.3-2
- Use %%{buildroot} instead of $RPM_BUILD_ROOT
- Remove unneeded patch
- Add missing dependency on fuseiso

* Fri Dec 23 2011 Christophe Fergeau <cfergeau@redhat.com> - 3.3.3-1
- Initial import

