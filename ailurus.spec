%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name: ailurus
Version: 10.06.93
Release: 0%{?dist}
Summary: A simple software center and GNOME tweaker
Group: Applications/System
License: GPLv2+
URL: http://ailurus.googlecode.com/
Source: http://homerxing.fedorapeople.org/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: python-devel python2-devel python-distutils-extra intltool
BuildArch: noarch
# The automatic dependency consists of python and rpmlib only. It is insufficient.
Requires: polkit pygtk2 notify-python vte rpm-python pygobject2 dbus-python wget unzip xterm gnome-python2-gnomekeyring

%description
Ailurus is a simple software center and GNOME tweaker.

Features:
* Help users learn some Linux skills
* Install some nice applications
* Display basic hardware information
* Clean YUM cache
* Backup and recover YUM status
* Change GNOME settings 

%prep
%setup -q -n %{name}-%{version}

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%{python_sitelib}/ailurus/
%{_bindir}/ailurus
%doc %{_mandir}/man1/ailurus.1*
%{_datadir}/applications/ailurus.desktop
%{_datadir}/ailurus/
%{_datadir}/icons/hicolor/*/apps/ailurus.png
%{_datadir}/dbus-1/system-services/cn.ailurus.service
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/cn.ailurus.conf
%{_datadir}/PolicyKit/policy/cn.ailurus.policy
%{_datadir}/polkit-1/actions/cn.ailurus.policy
%{_datadir}/omf/ailurus
%{python_sitelib}/ailurus*.egg-info

%changelog
* Mon Jul 12 2010 Homer Xing <homer.xing@gmail.com> 10.06.93-0
- Initial package
