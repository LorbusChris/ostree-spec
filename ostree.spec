# Define this if we want to build with embedded dependencies
# for e.g. RHEL6
%define enable_embedded_dependencies 0

%if 0%{?enable_embedded_dependencies}
%define build_name ostree-embeddeps
%else
%define build_name ostree
%endif

%if 0%{?rhel}
# HACK to fix building on RHEL6; find_debuginfo is crashing, not sure
# why
%define debug_package %{nil}
%endif

Summary: Linux-based operating system develop/build/deploy tool
Name: ostree
Version: 2013.4
Release: 2%{?dist}
#VCS: git:git://git.gnome.org/ostree
Source0: http://ftp.gnome.org/pub/GNOME/sources/ostree/%{version}/%{build_name}-%{version}.tar.xz
# The libostree.so (currently private) shared library, and almost all
# of the utilities are licensed under the LGPLv2+.  Only at present
# one utility program (ostree-switch-root) is forked from util-linux under
# the GPL.
# The BSD is there basically just for some random scripts, nothing
# important.
# As always, consult the upstream COPYING file, and individual source
# files for the canonical license status.
License: LGPLv2+ and GPLv2+ and BSD
URL: http://live.gnome.org/OSTree
# We always run autogen.sh
BuildRequires: autoconf automake libtool
# Too bad there isn't a pkg-config file =(
BuildRequires: libattr-devel
# For docs
BuildRequires: gtk-doc
BuildRequires: dracut

Requires: linux-user-chroot
Requires: dracut

# Embedded GLib dependencies
%if 0%{?enable_embedded_dependencies}
BuildRequires: glibc-devel
BuildRequires: pkgconfig(libffi)
BuildRequires: python-devel
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(libselinux)

# Embedded libsoup dependencies
BuildRequires: gnome-common
BuildRequires: intltool
BuildRequires: pkgconfig(libxml-2.0)
%else
BuildRequires: pkgconfig(gio-unix-2.0)
BuildRequires: pkgconfig(libsoup-2.4)
%endif

%description
See http://live.gnome.org/OSTree

%prep
%setup -q -n %{build_name}-%{version}

%build
env NOCONFIGURE=1 ./autogen.sh
%if 0%{?enable_embedded_dependencies}
%define embedded_dependencies_option --enable-embedded-dependencies
%else
%define embedded_dependencies_option %{nil}
%endif

%configure --disable-silent-rules \
	   --enable-documentation \
	   --disable-libarchive \
	   --with-dracut \
	   %{embedded_dependencies_option}
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p -c"

%clean
rm -rf $RPM_BUILD_ROOT

%files
%doc COPYING README.md
%{_bindir}/ostree
%{_sbindir}/ostree-prepare-root
%{_sbindir}/ostree-remount
%{_sysconfdir}/dracut.conf.d/ostree.conf
%dir %{_prefix}/lib/dracut/modules.d/98ostree
%{_prefix}/lib/systemd/system/ostree*.service
%{_prefix}/lib/systemd/system/*.target.wants/ostree*.service
%{_prefix}/lib/dracut/modules.d/98ostree/*
%dir %{_libdir}/ostree
%{_libdir}/ostree/*.so
%if 0%{?enable_embedded_dependencies}
%{_libdir}/ostree/libglib*.so*
%{_libdir}/ostree/libgmodule*.so*
%{_libdir}/ostree/libgobject*.so*
%{_libdir}/ostree/libgthread*.so*
%{_libdir}/ostree/libgio*.so*
%{_libdir}/ostree/libsoup*.so*
%endif
%{_mandir}/man1/*.gz

%changelog
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

