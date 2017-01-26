%if 0%{?fedora}
%global with_python3 1
%global _docdir_fmt %{name}
%endif

Name:           downstream-cherry-picker
Version:        1.2.0
Release:        1%{?dist}
Summary:        A command line object dispatcher
Group:          Development/Languages

License:        MIT
URL:            https://github.com/ktdreyer/downstream-cherry-picker

Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
%if 0%{?with_python3}
Requires:  python3-requests
BuildRequires:  python3-devel
BuildRequires:  python3-pytest
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
%else # python 2
Requires:  python-requests
BuildRequires:  pytest
BuildRequires:  python2-devel
BuildRequires:  python-requests
BuildRequires:  python-setuptools
%endif

%description
A tool to quickly cherry-pick whole GitHub pull requests that correspond to Red
Hat Bugzilla bugs.

This is tool is suitable for cherry-picking upstream patches into downstream
-patches branches for rdopkg to consume.

%prep
%setup -q -n %{name}-%{version}

%build

%if 0%{?with_python3}
%{__python3} setup.py build
%else
%{__python2} setup.py build
%endif # with_python3

%install
%if 0%{?with_python3}
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%else
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%endif

%check
export PYTHONPATH=$(pwd)

%if 0%{?with_python3}
py.test-%{python3_version} -v downstream_cherry_picker/tests
%else
py.test-%{python_version} -v downstream_cherry_picker/tests
%endif

%files
%{!?_licensedir:%global license %%doc}
%doc README.rst
%license LICENSE
%{_bindir}/%{name}
%if 0%{?with_python3}
%{python3_sitelib}/*
%else
%{python2_sitelib}/*
%endif # with_python3


%changelog
* Mon Aug 22 2016 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.0.1-1
- Initial package
