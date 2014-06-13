Summary: Git for operating system binaries
Name: ostree
Version: 2014.5
Release: 2%{?dist}
#VCS: git:git://git.gnome.org/ostree
Source0: http://ftp.gnome.org/pub/GNOME/sources/ostree/%{version}/ostree-%{version}.tar.xz
Source1: 91-ostree.preset
License: LGPLv2+
URL: http://live.gnome.org/OSTree

# We always run autogen.sh
BuildRequires: autoconf automake libtool
# For docs
BuildRequires: gtk-doc
# Core requirements
BuildRequires: pkgconfig(libgsystem)
BuildRequires: pkgconfig(libsoup-2.4)
BuildRequires: libattr-devel
# Extras
BuildRequires: pkgconfig(libarchive)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libselinux)
BuildRequires: pkgconfig(e2p)
BuildRequires: gpgme-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: /usr/bin/g-ir-scanner
BuildRequires: dracut

# Runtime requirements
Requires: dracut
Requires: /usr/bin/gpgv2
Requires: systemd-units

%description
OSTree is a tool for managing bootable, immutable, versioned
filesystem trees. While it takes over some of the roles of tradtional
"package managers" like dpkg and rpm, it is not a package system; nor
is it a tool for managing full disk images. Instead, it sits between
those levels, offering a blend of the advantages (and disadvantages)
of both.

%package devel
Summary: Development headers for %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The %{name}-devel package includes the header files for the %{name} library.

%prep
%setup -q -n ostree-%{version}

%build
env NOCONFIGURE=1 ./autogen.sh
%configure --disable-silent-rules \
	   --enable-gtk-doc \
	   --with-selinux \
	   --with-dracut
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p -c"
find $RPM_BUILD_ROOT -name '*.la' -delete
install -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT/%{_prefix}/lib/systemd/system-preset/91-ostree.preset

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post ostree-remount.service

%preun
%systemd_preun ostree-remount.service

%files
%doc COPYING README.md
%{_bindir}/ostree
%{_sbindir}/ostree-prepare-root
%{_sbindir}/ostree-remount
%{_datadir}/ostree/trusted.gpg.d
%{_sysconfdir}/ostree
%{_sysconfdir}/dracut.conf.d/ostree.conf
%dir %{_prefix}/lib/dracut/modules.d/98ostree
%{_prefix}/lib/systemd/system/ostree*.service
%{_prefix}/lib/dracut/modules.d/98ostree/*
%{_libdir}/*.so.1*
%{_libdir}/girepository-1.0/OSTree-1.0.typelib
%{_mandir}/man*/*.gz
%{_prefix}/lib/systemd/system-preset/91-ostree.preset

%files devel
%{_libdir}/lib*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*
%dir %{_datadir}/gtk-doc/html/ostree
%{_datadir}/gtk-doc/html/ostree
%{_datadir}/gir-1.0/OSTree-1.0.gir

%changelog
* Fri Jun 13 2014 Colin Walters <walters@verbum.org> - 2014.4-2
- Include /etc/ostree, even though it is empty

* Mon Jun 09 2014 Colin Walters <walters@verbum.org> - 2014.4-1
- New upstream release

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2014.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Apr 13 2014 Colin Walters <walters@verbum.org> - 2014.4-1
- New upstream release

* Mon Mar 31 2014 Colin Walters <walters@verbum.org>
- New git snapshot for rpm-ostree

* Fri Mar 21 2014 Colin Walters <walters@verbum.org> - 2014.3-1
- New upstream release

* Fri Mar 14 2014 Colin Walters <walters@verbum.org> - 2014.2-3
- Move trusted.gpg.d to main runtime package, where it should be

* Fri Mar 07 2014 Colin Walters <walters@verbum.org> - 2014.2-2
- Depend on gpgv2 
- Resolves: #1073813

* Sat Mar 01 2014 Colin Walters <walters@verbum.org> - 2014.2-1
- New upstream release
- Depend on libselinux
- Explicitly depend on libarchive too, we were actually failing
  to disable it before

* Fri Jan 24 2014 Colin Walters <walters@verbum.org> - 2014.1-1
- New upstream release

* Mon Jan 13 2014 Colin Walters <walters@verbum.org> - 2013.7-2
- Add preset file so ostree-remount is enabled by default, since
  it needs to be.

* Tue Oct 15 2013 Colin Walters <walters@verbum.org> - 2013.7-1
- New upstream release
- Now LGPLv2+ only
- Enable libarchive since it might be useful for people
- Enable new gpgme dependency

* Thu Sep 12 2013 Colin Walters <walters@verbum.org> - 2013.6-3
- Enable introspection

* Mon Sep 09 2013 Colin Walters <walters@verbum.org> - 2013.6-2
- Tweak description

* Mon Sep 09 2013 Colin Walters <walters@verbum.org> - 2013.6-1
- New upstream release

* Sat Aug 25 2013 Colin Walters <walters@verbum.org> - 2013.5-3
- And actually while we are here, drop all the embedded dependency
  goop from this spec file; it may live on in the EPEL branch.

* Sat Aug 25 2013 Colin Walters <walters@verbum.org> - 2013.5-2
- Drop requirement on linux-user-chroot
  We now require triggers to be processed on the build server
  by default, so ostree does not runtime-depend on linux-user-chroot.

* Sat Aug 17 2013 Colin Walters <walters@verbum.org> - 2013.5-1
- New upstream release
- Add devel package

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2013.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 16 2013 Colin Walters <walters@verbum.org> - 2013.4-1
- New upstream release

* Sun Jul 07 2013 Colin Walters <walters@verbum.org> - 2013.3-1
- New upstream release

* Mon Apr 01 2013 Colin Walters <walters@verbum.org> - 2013.1-1
- New upstream release

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2012.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Dec 23 2012 Colin Walters <walters@verbum.org> - 2012.13-1
- New upstream release

* Tue Dec 18 2012 Colin Walters <walters@verbum.org> - 2012.12-2
- Explicitly enable grub2 hook; otherwise we pick up whatever
  the buildroot has, which is not what we want.

* Mon Nov 19 2012 Colin Walters <walters@verbum.org> - 2012.12-1
- Initial import; thanks to Michel Alexandre Salim for review
  https://bugzilla.redhat.com/show_bug.cgi?id=819951

