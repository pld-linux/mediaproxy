#
Summary:	Media relay for RTP/RTCP and UDP streams
Name:		mediaproxy
Version:	2.6.1
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://download.ag-projects.com/MediaProxy/%{name}-%{version}.tar.gz
# Source0-md5:	72443d6137c77c3c9cd446ca98ec5d21
Source1:	media-dispatcher.sysconfig
Source2:	media-dispatcher.init
Source3:    media-dispatcher.service
Source4:	media-relay.sysconfig
Source5:	media-relay.init
Source6:    media-relay.service
Source7:	%{name}.tmpfiles
URL:		http://mediaproxy.ag-projects.com/
BuildRequires:	iptables-devel
BuildRequires:	libnetfilter_conntrack-devel
BuildRequires:	linux-libc-headers >= 7:2.6.37
BuildRequires:	python >= 1:2.5
BuildRequires:	python-devel >= 1:2.5
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
%pyrequires_eq	python-modules
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MediaProxy is a media relay for RTP/RTCP and UDP streams that works in
tandem with OpenSIPS to provide NAT traversal capability for media
streams from SIP user agents located behind NAT. When using
MediaProxy, NAT traversal for RTP media will work without any settings
in the SIP User Agents or the NAT router.

%package common
Summary:	Media relay for RTP/RTCP and UDP streams
Group:		Networking/Daemons
Requires:	python-SQLObject
Requires:	python-TwistedCore
Requires:	python-TwistedNames
Requires:	python-application >= 1.2.8
Requires:	python-cjson
Requires:	python-gnutls
Requires:	python-pyrad

%description common
MediaProxy is a media relay for RTP/RTCP and UDP streams that works in
tandem with OpenSIPS to provide NAT traversal capability for media
streams from SIP user agents located behind NAT. When using
MediaProxy, NAT traversal for RTP media will work without any settings
in the SIP User Agents or the NAT router.

This package contains files shared my MediaProxy dispatcher and relay.

%package dispatcher
Summary:	Media relay for RTP/RTCP and UDP streams
Group:		Networking/Daemons
Requires:	%{name}-common = %{version}-%{release}
Requires(post,preun):	/sbin/chkconfig
Suggests:	opensips

%description dispatcher
MediaProxy is a media relay for RTP/RTCP and UDP streams that works in
tandem with OpenSIPS to provide NAT traversal capability for media
streams from SIP user agents located behind NAT. When using
MediaProxy, NAT traversal for RTP media will work without any settings
in the SIP User Agents or the NAT router.

This package contains the dispatcher part of MediaProxy. The
dispatcher component always runs on the same host as OpenSIPS and
communicates with its mediaproxy module through a UNIX domain socket.
The relay(s) connect to the dispatcher using TLS. This relay component
may be on the same or on a different host as OpenSIPS. There may be
several relays for the dispatcher to choose from and a relay may
service more than one dispatcher.

%package relay
Summary:	Media relay for RTP/RTCP and UDP streams
Group:		Networking/Daemons
Requires:	%{name}-common = %{version}-%{release}
Requires(post,preun):	/sbin/chkconfig
Suggests:	opensips

%description relay
MediaProxy is a media relay for RTP/RTCP and UDP streams that works in
tandem with OpenSIPS to provide NAT traversal capability for media
streams from SIP user agents located behind NAT. When using
MediaProxy, NAT traversal for RTP media will work without any settings
in the SIP User Agents or the NAT router.

This package contains the media relay part of MediaProxy. The relay(s)
connect to the dispatcher using TLS. This relay component may be on
the same or on a different host as OpenSIPS. There may be several
relays for the dispatcher to choose from and a relay may service more
than one dispatcher.


%prep
%setup -q

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/%{name},/var/run/%{name},%{systemdtmpfilesdir}} \
	$RPM_BUILD_ROOT{/etc/sysconfig,/etc/rc.d/init.d} \
    $RPM_BUILD_ROOT%{systemdunitdir}

python setup.py install \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean

install config.ini.sample $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/config.ini

install %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/media-dispatcher
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/media-dispatcher
install %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}/media-dispatcher.service
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/media-relay
install %{SOURCE5} $RPM_BUILD_ROOT/etc/rc.d/init.d/media-relay
install %{SOURCE6} $RPM_BUILD_ROOT%{systemdunitdir}/media-relay.service
install %{SOURCE7} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post dispatcher
/sbin/chkconfig --add media-dispatcher
%service media-relay restart
%systemd_post media-dispatcher.service

%post relay
%service media-dispatcher restart
/sbin/chkconfig --add media-relay
%systemd_post media-relay.service

%preun dispatcher
%systemd_preun media-dispatcher.service
if [ "$1" = "0" ]; then
	%service -q media-dispatcher stop
	/sbin/chkconfig --del media-dispatcher
fi

%preun relay
%systemd_preun media-relay.service
if [ "$1" = "0" ]; then
	%service -q media-relay stop
	/sbin/chkconfig --del media-relay
fi

%postun dispatcher
%systemd_reload

%postun relay
%systemd_reload

%files common
%defattr(644,root,root,755)
%doc README TODO
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/config.ini
%{py_sitedir}/*-*.egg-info
%dir %{py_sitedir}/%{name}
%{py_sitedir}/%{name}/*.py[co]
%dir %{py_sitedir}/%{name}/configuration
%{py_sitedir}/%{name}/configuration/*.py[co]
%dir %{py_sitedir}/%{name}/interfaces
%{py_sitedir}/%{name}/interfaces/*.py[co]
%dir %{py_sitedir}/%{name}/interfaces/accounting
%{py_sitedir}/%{name}/interfaces/accounting/*.py[co]
%dir %{py_sitedir}/%{name}/interfaces/system
%{py_sitedir}/%{name}/interfaces/system/*.py[co]
%attr(755,root,root) %{py_sitedir}/%{name}/interfaces/system/*.so
%attr(700,root,root) %dir /var/run/mediaproxy
%{systemdtmpfilesdir}/%{name}.conf

%files dispatcher
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/media-dispatcher
%attr(754,root,root) /etc/rc.d/init.d/media-dispatcher
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/media-dispatcher
%{systemdunitdir}/media-dispatcher.service

%files relay
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/media-relay
%attr(754,root,root) /etc/rc.d/init.d/media-relay
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/media-relay
%{systemdunitdir}/media-relay.service
