# without glusterfs dependency
# if you wish to exclude gluster handler in RPM, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without gluster
%{?_without_gluster:%global _without_gluster --with-gluster=no}

# without tirpc dependency
# if you wish to build without tirpc library, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without tirpc
%{?_without_tirpc:%global _without_tirpc --with-tirpc=no}

# without azblk dependency
# if you wish to build without azblk library, use below command
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without azblk
%{?_without_azblk:%global _without_azblk --with-azblk=no}

%if ( 0%{?fedora} && 0%{?fedora} <= 27 ) || ( 0%{?rhel} && 0%{?rhel} <= 7 )
%global _without_tirpc --with-tirpc=no
%endif

Name:          nbd-runner
Summary:       A daemon that handles the NBD device's IO requests in server side
License:       LGPLv2+
Version:       0.4
Release:       0%{?dist}
URL:           https://github.com/gluster/nbd-runner.git

Source0:       https://github.com/gluster/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires: gcc
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: kmod-devel
BuildRequires: libnl3-devel
BuildRequires: libevent-devel
BuildRequires: glib2-devel
BuildRequires: json-c-devel

%if ( 0%{!?_without_tirpc:1} )
BuildRequires: libtirpc-devel >= 1.0.0
BuildRequires: rpcgen
%endif

Requires:      kmod
Requires:      json-c
Requires:      rsyslog

%if ( 0%{!?_without_gluster:1} )
BuildRequires: glusterfs-api-devel
Requires:      glusterfs-api
Requires:      %{name} = %{version}-%{release}
%endif

%if ( 0%{!?_without_azblk:1} )
BuildRequires: libcurl-devel
BuildRequires: libuv-devel
%endif

%description
A daemon that handles the userspace side of the NBD(Network Block Device)
back-store.

%prep
%autosetup -p 1

%build
echo v%{version}-%{release} > VERSION
./autogen.sh
export CFLAGS="%build_cflags -fPIC"
export CPPFLAGS="%build_cxxflags -fPIC"
%configure %{?_without_tirpc} %{?_without_gluster} %{?_without_azblk}
%make_build

%install
%make_install
find %{buildroot}%{_libdir}/nbd-runner/ -name '*.a' -delete
find %{buildroot}%{_libdir}/nbd-runner/ -name '*.la' -delete

%post
%systemd_post nbd-runner.service

%preun
%systemd_preun nbd-runner.service

%postun
%systemd_postun_with_restart nbd-runner.service

%files
%{_sbindir}/nbd-runner
%{_sbindir}/nbd-cli
%{_unitdir}/nbd-runner.service
%{_mandir}/man8/nbd-*.8.*
%doc README.md
%license COPYING-GPLV2 COPYING-LGPLV3
%config(noreplace) %{_sysconfdir}/sysconfig/nbd-runner
%ghost %attr(0600,-,-) %{_localstatedir}/log/nbd-runner/nbd-runner.log
%ghost %attr(0600,-,-) %{_localstatedir}/log/nbd-runner/nbd-runner-glfs.log

%if ( 0%{!?_without_gluster:1} )
%dir %{_libdir}/nbd-runner/
%{_libdir}/nbd-runner/libgluster_handler.so
%endif

%if ( 0%{!?_without_azblk:1} )
%dir %{_libdir}/nbd-runner/
%{_libdir}/nbd-runner/libazblk_handler.so
%endif

%changelog
* Wed Apr 24 2019 Xiubo Li <xiubli@redhat.com> - 0.4-0
- Initial package
