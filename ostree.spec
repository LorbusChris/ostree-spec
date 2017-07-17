# Currently libcurl for 27+; we will likely expand this
# to 26/25 soon.  See https://bugzilla.redhat.com/show_bug.cgi?id=1430489
%if 0%{?fedora} > 25
# This is supported by upstream currently, so we'll expose it as well,
# even though (main) Fedora doesn't use bconds.
%bcond_without curl
%else
%bcond_with curl
%endif

Summary: Tool for managing bootable, immutable filesystem trees
Name: ostree
Version: 2017.8
Release: 3%{?dist}
Source0: https://github.com/ostreedev/%{name}/releases/download/v%{version}/libostree-%{version}.tar.xz
# https://bugzilla.redhat.com/show_bug.cgi?id=1451458
Source1: 91-ostree.preset
License: LGPLv2+
URL: https://ostree.readthedocs.io/en/latest/

BuildRequires: git
# We always run autogen.sh
BuildRequires: autoconf automake libtool
# For docs
BuildRequires: gtk-doc
# Core requirements
BuildRequires: pkgconfig(zlib)
%if %{with curl}
BuildRequires: pkgconfig(libcurl)
BuildRequires: pkgconfig(openssl)
%endif
# The tests still require soup
BuildRequires: pkgconfig(libsoup-2.4)
BuildRequires: libattr-devel
# Extras
BuildRequires: pkgconfig(libarchive)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libselinux)
BuildRequires: pkgconfig(mount)
BuildRequires: pkgconfig(fuse)
BuildRequires: pkgconfig(e2p)
BuildRequires: libcap-devel
BuildRequires: gpgme-devel
BuildRequires: pkgconfig(libsystemd)
BuildRequires: /usr/bin/g-ir-scanner
BuildRequires: dracut
BuildRequires:  bison

# Runtime requirements
Requires: dracut
%if !%{with curl}
# To ensure we have TLS
Requires: glib-networking
%endif
Requires: /usr/bin/gpgv2
Requires: systemd-units

%description
OSTree is a tool for managing bootable, immutable, versioned
filesystem trees. While it takes over some of the roles of tradtional
"package managers" like dpkg and rpm, it is not a package system; nor
is it a tool for managing full disk images. Instead, it sits between
those levels, offering a blend of the advantages (and disadvantages)
of both.

%package libs
Summary: Development headers for %{name}
Group: Development/Libraries

%description libs
The %{name}-libs provides shared libraries for %{name}.

%package devel
Summary: Development headers for %{name}
Group: Development/Libraries
Requires: %{name}-libs =  %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
The %{name}-devel package includes the header files for the %{name} library.

%ifnarch s390 s390x %{arm}
%package grub2
Summary: GRUB2 integration for OSTree
Group: Development/Libraries
%ifnarch aarch64
Requires: grub2
%else
Requires: grub2-efi
%endif
Requires: ostree

%description grub2
GRUB2 integration for OSTree
%endif

%prep
%autosetup -Sgit -n libostree-%{version}

%build
env NOCONFIGURE=1 ./autogen.sh
%configure --disable-silent-rules \
	   --enable-gtk-doc \
	   --with-selinux \
%if %{with curl}
    --with-curl \
    --with-openssl \
%endif
	   --with-dracut=yesbutnoconf
%make_build

%install
%make_install INSTALL="install -p -c"
find %{buildroot} -name '*.la' -delete
install -D -m 0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/systemd/system-preset/91-ostree.preset
# Right now we aren't doing installed tests here
rm -f %{buildroot}%{_libexecdir}/libostree/ostree-trivial-httpd

%post
%systemd_post ostree-remount.service

%preun
%systemd_preun ostree-remount.service

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc README.md
%{_bindir}/ostree
%{_bindir}/rofiles-fuse
%{_datadir}/ostree/trusted.gpg.d
%dir %{_prefix}/lib/dracut/modules.d/98ostree
%{_prefix}/lib/systemd/system/ostree*.service
%{_prefix}/lib/dracut/modules.d/98ostree/*
%{_mandir}/man*/*.gz
%{_prefix}/lib/systemd/system-generators/ostree-system-generator
%{_prefix}/lib/systemd/system-preset/91-ostree.preset
%exclude %{_sysconfdir}/grub.d/*ostree
%exclude %{_libexecdir}/libostree/grub2*
%{_prefix}/lib/ostree/ostree-prepare-root
%{_prefix}/lib/ostree/ostree-remount
# Moved in git master
%{_libexecdir}/libostree/*

%files libs
%{_sysconfdir}/ostree
%{_libdir}/*.so.1*
%{_libdir}/girepository-1.0/OSTree-1.0.typelib

%files devel
%{_libdir}/lib*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*
%dir %{_datadir}/gtk-doc/html/ostree
%{_datadir}/gtk-doc/html/ostree
%{_datadir}/gir-1.0/OSTree-1.0.gir

%ifnarch s390 s390x %{arm}
%files grub2
%{_sysconfdir}/grub.d/*ostree
%{_libexecdir}/libostree/grub2*
%endif

%changelog
* Mon Jul 17 2017 Colin Walters <walters@verbum.org> - 2017.8-3
- Switch to libcurl for F26+
  I think it works well; to recap the arguments below:
  It has various advantages like HTTP2, plus now that NetworkManager
  switched we are the last thing left in Fedora Atomic Host depending
  on libsoup.

* Thu Jul 06 2017 Colin Walters <walters@verbum.org> - 2017.8-2
- New upstream version

* Mon Jun 19 2017 Colin Walters <walters@verbum.org> - 2017.7-2
- Update to new upstream

* Fri Jun 02 2017 Colin Walters <walters@verbum.org> - 2017.6-4
- Fix previous commit to actually work

* Thu May 18 2017 Colin Walters <walters@verbum.org> - 2017.6-3
- Enable curl+openssl on f27+
  It has various advantages like HTTP2, plus now that NetworkManager
  switched we are the last thing left in Fedora Atomic Host depending
  on libsoup.

* Wed May 17 2017 Colin Walters <walters@verbum.org> - 2017.6-2
- New upstream version

* Wed Apr 19 2017 Colin Walters <walters@verbum.org> - 2017.5-2
- New upstream version

* Wed Apr 12 2017 Colin Walters <walters@verbum.org> - 2017.4-2
- New upstream version

* Fri Mar 10 2017 Colin Walters <walters@verbum.org> - 2017.3-2
- New upstream version

* Fri Mar 03 2017 Colin Walters <walters@redhat.com> - 2017.2-4
- Add patch for ppc64le grub2

* Thu Feb 23 2017 Colin Walters <walters@verbum.org> - 2017.2-3
- Backport libmount unref patch

* Tue Feb 14 2017 Colin Walters <walters@verbum.org> - 2017.2-2
- New upstream version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2017.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Feb 07 2017 Jonathan Lebon <jlebon@redhat.com> - 2017.1-4
- Make ostree-grub2 require ostree

* Tue Feb 07 2017 Colin Walters <walters@verbum.org> - 2017.1-3
- Split off ostree-libs.  This is the inverse of upstream
  https://github.com/ostreedev/ostree/pull/659
  but renaming the package would be hard for low immediate gain.
  With this at least, flatpak could theoretically depend just on libostree.
  And similarly for rpm-ostree compose tree (when that gets split out).

* Mon Jan 23 2017 Colin Walters <walters@verbum.org> - 2017.1-2
- New upstream version

* Wed Jan 18 2017 Colin Walters <walters@verbum.org> - 2016.15-2
- Enable libmount for /boot readonly

* Mon Dec 12 2016 walters@redhat.com - 2016.15-1
- New upstream version

* Sat Dec 10 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 2016.14-3
- Rebuild for gpgme 1.18

* Tue Nov 29 2016 Kalev Lember <klember@redhat.com> - 2016.14-2
- Backport a patch to remove an accidental print statement

* Wed Nov 23 2016 walters@redhat.com - 2016.14-1
- New upstream version

* Tue Nov 15 2016 walters@redhat.com - 2016.13-2
- New upstream version
- Require glib-networking to fix https://pagure.io/pungi-fedora/pull-request/103

* Sun Oct 23 2016 walters@verbum.org - 2016.12-1
- New upstream release

* Fri Oct 07 2016 walters@redhat.com - 2016.11-1
- New upstream version

* Tue Sep 20 2016 walters@redhat.com - 2016.10-8
- Backport another patch for systemd journal
  Resolves: #1265295

* Fri Sep 16 2016 walters@verbum.org - 2016.10-6
- Set --with-dracut=yesbutnoconf
  Resolves: #1331369

* Thu Sep 15 2016 walters@verbum.org - 2016.10-4
- Backport patch to fix bug#1265295

* Mon Sep 12 2016 Kalev Lember <klember@redhat.com> - 2016.10-3
- pull: Do allow executing deltas when mirroring into bare{,-user}

* Fri Sep 09 2016 Kalev Lember <klember@redhat.com> - 2016.10-2
- Drop libgsystem dependency

* Thu Sep 08 2016 walters@redhat.com - 2016.10-1
- New upstream version

* Wed Aug 31 2016 Colin Walters <walters@verbum.org> - 2016.9-1
- New upstream version

* Tue Aug 09 2016 walters@redhat.com - 2016.8-1
- New upstream version

* Tue Aug 09 2016 Colin Walters <walters@verbum.org> - 2016.7-4
- Add pending patch to fix date-based pruning

* Fri Jul 08 2016 walters@redhat.com - 2016.7-1
- New upstream version

* Mon Jun 20 2016 Colin Walters <walters@redhat.com> - 2016.6-1
- New upstream version

* Sun May  8 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2016.5-3
- aarch64 only has grub2-efi
- Use %%license

* Fri Apr 15 2016 Colin Walters <walters@redhat.com> - 2016.5-2
- New upstream version

* Wed Mar 23 2016 Colin Walters <walters@redhat.com> - 2016.4-2
- New upstream version

* Fri Feb 26 2016 Colin Walters <walters@redhat.com> - 2016.3-1
- New upstream version

* Tue Feb 23 2016 Colin Walters <walters@redhat.com> - 2016.2-1
- New upstream version

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2016.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 12 2016 Colin Walters <walters@redhat.com> - 2016.1-2
- New upstream version

* Fri Dec 04 2015 Colin Walters <walters@redhat.com> - 2015.11-2
- New upstream version

* Sun Nov 22 2015 Colin Walters <walters@redhat.com> - 2015.10-1
- New upstream version

* Thu Nov 12 2015 Matthew Barnes <mbarnes@redhat.com> - 2015.9-3
- Add ostree-tmp-chmod.service to fix /tmp permissions on existing installs.
  Resolves: #1276775

* Fri Oct 30 2015 Colin Walters <walters@redhat.com> - 2015.9-2
- Add patch to fix permissions of /tmp
  Resolves: #1276775

* Wed Sep 23 2015 Colin Walters <walters@redhat.com> - 2015.9-1
- New upstream version

* Wed Aug 26 2015 Colin Walters <walters@redhat.com> - 2015.8-1
- New upstream version

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2015.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 02 2015 Colin Walters <walters@redhat.com> - 2015.7-1
- New upstream version

* Thu May 28 2015 Colin Walters <walters@redhat.com> - 2015.6-4
- Add patch to ensure reliable bootloader ordering
  See: #1225088

* Thu Apr 30 2015 Colin Walters <walters@redhat.com> - 2015.6-3
- Close sysroot fd in finalize to fix Anaconda
  https://bugzilla.redhat.com/show_bug.cgi?id=1217578

* Fri Apr 17 2015 Colin Walters <walters@redhat.com> - 2015.6-2
- New upstream release

* Sun Apr 12 2015 Colin Walters <walters@redhat.com> - 2015.5-4
- (Really) Handle null epoch as well; this was injected for https://github.com/cgwalters/rpmdistro-gitoverlay

* Tue Apr 07 2015 Colin Walters <walters@redhat.com> - 2015.5-2
- New upstream release

* Mon Mar 30 2015 Dan Horák <dan[at]danny.cz> - 2015.4-5
- ExcludeArch is a build restriction and is global, switching to %%ifnarch

* Fri Mar 27 2015 Colin Walters <walters@redhat.com> - 2015.4-4
- Have grub2 subpackage match ExcludeArch with grub2

* Fri Mar 27 2015 Colin Walters <walters@redhat.com> - 2015.4-3
- Handle null epoch as well; this was injected for https://github.com/cgwalters/rpmdistro-gitoverlay

* Wed Mar 25 2015 Colin Walters <walters@redhat.com> - 2015.4-2
- New upstream release

* Mon Feb 16 2015 Colin Walters <walters@redhat.com> - 2015.3-3
- Require latest libgsystem to ensure people have it

* Fri Jan 23 2015 Colin Walters <walters@redhat.com> - 2015.3-2
- New upstream release

* Thu Jan 08 2015 Colin Walters <walters@redhat.com> - 2015.2-1
- New upstream release

* Sun Jan 04 2015 Colin Walters <walters@redhat.com> - 2014.13-2
- Add patch to ensure correct xattrs on modified config files
  Fixes: #1178208

* Wed Dec 17 2014 Colin Walters <walters@redhat.com> - 2014.13-1
- New upstream release

* Wed Nov 26 2014 Colin Walters <walters@redhat.com> - 2014.12-1
- New upstream version

* Thu Oct 30 2014 Colin Walters <walters@redhat.com> - 2014.11-1
- New upstream release

* Wed Oct 29 2014 Colin Walters <walters@redhat.com> - 2014.10.1.gedc3b9a-1
- New upstream release

* Fri Oct 24 2014 Colin Walters <walters@redhat.com> - 2014.9-2
- New upstream release

* Thu Oct 16 2014 Colin Walters <walters@redhat.com>
- New upstream release

* Mon Sep 08 2014 Colin Walters <walters@redhat.com> - 2014.6-1
- New upstream release

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2014.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 22 2014 Kalev Lember <kalevlember@gmail.com> - 2014.5-4
- Rebuilt for gobject-introspection 1.41.4

* Wed Jun 25 2014 Colin Walters <walters@verbum.org>
- Rebuild to pick up new libsoup

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

