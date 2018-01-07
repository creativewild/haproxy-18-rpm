%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy

%if 0%{?rhel} == 7
    %define dist .el7
%endif

%if 0%{?rhel} < 7
    %{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

Summary: HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Name: haproxy
Version: %{version}
Release: %{release}%{?dist}
License: GPL
Group: System Environment/Daemons
URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/1.8/src/%{name}-%{version}.tar.gz
Source1: %{name}.cfg
%{?el6:Source2: %{name}.init}
%{?el7:Source2: %{name}.service}
Source3: %{name}.logrotate
Source4: %{name}.syslog%{?dist}
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: pcre-devel make gcc openssl-devel 


Requires(pre):      shadow-utils

%if 0%{?el6}
Requires(post):     chkconfig, initscripts
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts
%endif

%if 0%{?el7}
BuildRequires:      systemd-units
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%endif

%description
HAProxy is a free, very fast and reliable solution
offering high availability, load balancing, and proxyingfor TCP and HTTP-based applications.
It is particularly suited for very high traffic web sites and powers quite a number of the world's most visited ones.
Over the years it has become the de-facto standard opensource load balancer, is now shipped 
with most mainstream Linux distributions, and is often deployed by default in cloud platforms.


%prep
%setup -q

# We don't want any perl dependecies in this RPM:
%define __perl_requires /bin/true

%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif

%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 USE_LINUX_SPLICE=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}
 
%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d %{buildroot}%{_sysconfdir}/rsyslog.d
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/errors
%{__install} -d %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -d %{buildroot}%{_mandir}/man1/

%{__install} -s %{name} %{buildroot}%{_sbindir}/
%if 0%{?el6}
%{__install} -d %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__install} -c -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%endif    
%if 0%{?el7}
%{__install} -s %{name}-systemd-wrapper %{buildroot}%{_sbindir}/
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
%endif
%{__install} -c -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/
%{__install} -c -m 755 examples/errorfiles/*.http %{buildroot}%{_sysconfdir}/%{name}/errors/
%{__install} -c -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -c -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/rsyslog.d/49-%{name}.conf
%{__install} -c -m 755 doc/%{name}.1 %{buildroot}%{_mandir}/man1/

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%pre
getent group %{haproxy_group} >/dev/null || \
       groupadd -g 188 -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
       useradd -u 188 -r -g %{haproxy_group} -d %{haproxy_home} \
       -s /sbin/nologin -c "%{name}" %{haproxy_user}
exit 0
 
%post
%if 0%{?el7}
%systemd_post %{name}.service
systemctl restart rsyslog.service
%endif

%if 0%{?el6}
/sbin/chkconfig --add %{name}
/sbin/service rsyslog restart >/dev/null 2>&1 || :
%endif

%preun
%if 0%{?el7}
%systemd_preun %{name}.service
%endif

%if 0%{?el6}
if [ $1 = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi
%endif

%postun
%if 0%{?el7}
%systemd_postun_with_restart %{name}.service
systemctl restart rsyslog.service
%endif

%if 0%{?el6}
if [ "$1" -ge "1" ]; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
  /sbin/service rsyslog restart >/dev/null 2>&1 || :
fi
%endif

%files
%defattr(-,root,root)
%doc CHANGELOG README examples/*.cfg doc/architecture.txt doc/configuration.txt doc/intro.txt doc/management.txt doc/proxy-protocol.txt
%doc %{_mandir}/man1/%{name}.1*
%dir %{_localstatedir}/log/%{name}

%attr(0755,root,root) %{_sbindir}/%{name}
%if 0%{?el6}
%attr(0755,root,root) %config %_sysconfdir/rc.d/init.d/%{name}
%endif    
%if 0%{?el7}
%attr(0755,root,root) %{_sbindir}/%{name}-systemd-wrapper
%attr(-,root,root) %{_unitdir}/%{name}.service
%endif
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/errors
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0644,root,root) %config %{_sysconfdir}/logrotate.d/%{name}
%attr(0644,root,root) %config %{_sysconfdir}/rsyslog.d/49-%{name}.conf

%changelog
HAProxy 1.8.3 was released on 2017/12/30. It added 9 new commits
after version 1.8.2.

It's essentially focused on fixing the problems reported last week on
HTTP/2 and on the master-worker :
  - fixed the HTTP/2 POST/PUT which would occasionally forward a shutdown
    to the server resulting in server errors ;

  - fixed an occasional 400 bad request on HTTP/2 which would happen when
    large headers displace previous ones within the same request, due to
    a missing copy of the name (the value was correct). It may have caused
    some authentication to occasionally be lost (eg: lost cookie header)
    and of course some requests to be rejected when this resulted in upper
    case characters in their name.

  - implemented the graceful shutdown on HTTP/2 connections during a reload
    so that we can inform the client we're going to close, encouraging the
    client to switch to a new connection. This avoids connections from
    lasting forever after reloads on H2. I also noticed that it allows the
    process to be replaced faster.

  - open /dev/null on fd 0,1,2 after startup so that we never end up with
    sockets or pipes on these FDs, which is otherwise problematic in master
    worker mode.
