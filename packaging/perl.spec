Name:           perl
Summary:        The Perl interpreter
License:        Artistic-1.0 ; GPL-2.0+
Group:          Development/Languages/Perl
Version:        5.14.2
Release:        1
%define pversion 5.14.2
Url:            http://www.perl.org/
Source:         perl-5.14.2.tar.bz2
Source1:        %name-rpmlintrc
Source2:        macros.perl
Source3:        README.macros
Source1001:     perl.manifest
Patch0:         perl-%{pversion}.dif
Patch1:         perl-gracefull-net-ftp.diff
Patch2:         perl-regexp-refoverflow.diff
Patch3:         perl-nroff.diff
Patch4:         perl-netcmdutf8.diff
Patch5:         perl-HiRes.t-timeout.diff
Patch6:         perl-saverecontext.diff
Patch7:         perl-cbuilder-ccflags.diff
Requires(pre):  perl-base = %version
BuildRequires:  db4-devel
BuildRequires:  gdbm-devel
BuildRequires:  bzip2-devel
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel
%if "%version" != "%pversion"
Provides:       perl = %pversion-%release
%endif
Provides:       perl(:MODULE_COMPAT_%pversion)
Provides:       perl-500
Provides:       perl-macros
Obsoletes:      perl-macros
Provides:       perl-Filter-Simple perl-I18N-LangTags perl-MIME-Base64 perl-Storable
Provides:       perl-Test-Simple = 0.98-%{release}
Obsoletes:      perl-Filter-Simple perl-I18N-LangTags perl-MIME-Base64 perl-Storable
Obsoletes:      perl-Test-Simple < 0.98
Provides:       perl-Text-Balanced perl-Time-HiRes perl-libnet
Obsoletes:      perl-Text-Balanced perl-Time-HiRes perl-libnet
Provides:       perl-Compress-Zlib perl-Compress-Raw-Zlib
Obsoletes:      perl-Compress-Zlib perl-Compress-Raw-Zlib
Provides:       perl-IO-Zlib perl-IO-Compress-Base perl-IO-Compress-Zlib
Obsoletes:      perl-IO-Zlib perl-IO-Compress-Base perl-IO-Compress-Zlib
Provides:       perl-Archive-Tar perl-Module-Build
Obsoletes:      perl-Archive-Tar perl-Module-Build
Provides:       perl-Locale-Maketext-Simple perl-Module-Pluggable
Obsoletes:      perl-Locale-Maketext-Simple perl-Module-Pluggable
Provides:       perl-Pod-Escapes perl-Pod-Simple
Obsoletes:      perl-Pod-Escapes perl-Pod-Simple
Provides:       perl-version perl-ExtUtils-ParseXS
Obsoletes:      perl-version perl-ExtUtils-ParseXS

%description
perl - Practical Extraction and Report Language

Perl is optimized for scanning arbitrary text files, extracting
information from those text files, and printing reports based on that
information.  It is also good for many system management tasks. Perl is
intended to be practical (easy to use, efficient, and complete) rather
than beautiful (tiny, elegant, and minimal).

Some of the modules available on CPAN can be found in the "perl"
series.

%package base
Summary:        The Perl interpreter
Provides:       perl-Digest perl-Digest-MD5
%if "%version" != "%pversion"
Provides:       perl-base = %pversion-%release
%endif
#

%description base
perl - Practical Extraction and Report Language

Perl is optimized for scanning arbitrary text files, extracting
information from those text files, and printing reports based on that
information.  It is also good for many system management tasks.

Perl is intended to be practical (easy to use, efficient, and complete)
rather than beautiful (tiny, elegant, and minimal).

This package contains only some basic modules and the perl binary
itself.

%package doc
Summary:        Perl Documentation
Requires:       perl = %{version}
Provides:       perl:/usr/share/man/man3/CORE.3pm.gz
BuildArch:      noarch

%description doc
Perl man pages and pod files.

%prep
%setup -q -n perl-5.14.2
cp -p %{S:3} .
%patch0
%patch1
%patch2
%patch3
%patch4
%patch5
%patch6
%patch7

%build
cp %{S:1001} .
cp -a lib savelib
export BZIP2_LIB=%{_libdir}
export BZIP2_INCLUDE=%{_includedir}
export BUILD_BZIP2=0
options="-Doptimize='$RPM_OPT_FLAGS -Wall -pipe'"
# always use glibc's setenv
options="$options -Accflags='-DPERL_USE_SAFE_PUTENV'"
options="$options -Dotherlibdirs=/usr/lib/perl5/site_perl"
chmod 755 ./configure.gnu
./configure.gnu --prefix=/usr -Dvendorprefix=/usr -Dinstallusrbinperl -Dusethreads -Di_db -Di_dbm -Di_ndbm -Di_gdbm -Dd_dbm_open -Duseshrplib=\'true\' $options
make %{?_smp_mflags}
cp -p libperl.so savelibperl.so
cp -p lib/Config.pm saveConfig.pm
cp -p lib/Config_heavy.pl saveConfig_heavy.pl
make clean > /dev/null
make clobber
rm -rf lib
mv savelib lib
./configure.gnu --prefix=/usr -Dvendorprefix=/usr -Dinstallusrbinperl -Dusethreads -Di_db -Di_dbm -Di_ndbm -Di_gdbm -Dd_dbm_open $options
make %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT
cp -a $RPM_BUILD_ROOT/usr/lib/perl5/site_perl $RPM_BUILD_ROOT/usr/lib/perl5/vendor_perl
cpa=`echo $RPM_BUILD_ROOT/usr/lib/perl5/*/*/CORE | sed -e 's@/CORE$@@'`
cp=`echo "$cpa" | sed -e 's@/[^/]*$@@'`
vpa=`echo $cpa | sed -e 's@/perl5/@/perl5/vendor_perl/@'`
vp=`echo "$vpa" | sed -e 's@/[^/]*$@@'`
install -d $vp/auto
install -d $vpa/auto
install -m 555 savelibperl.so $cpa/CORE/libperl.so
install -m 444 saveConfig.pm $cpa/Config.pm
install -m 444 saveConfig_heavy.pl $cpa/Config_heavy.pl
install -D -m 644 %{S:2} $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.perl
pushd /usr/include
( rpm -ql glibc-devel | fgrep '.h' 
  find /usr/include/asm/ -name \*.h
  find /usr/include/asm-generic -name \*.h
  find /usr/include/linux -name \*.h
) | while read f; do
  $RPM_BUILD_ROOT/usr/bin/perl -I$cp -I$cpa $RPM_BUILD_ROOT/usr/bin/h2ph -d $vpa ${f/\/usr\/include\//} || : 
done
popd
d="`gcc -print-file-name=include`"
test -f "$d/stdarg.h" && (cd $d ; $RPM_BUILD_ROOT/usr/bin/perl -I$cp -I$cpa $RPM_BUILD_ROOT/usr/bin/h2ph -d $vpa stdarg.h stddef.h float.h)
# remove broken pm - we don't have the module
rm $RPM_BUILD_ROOT/usr/lib/perl5/*/Pod/Perldoc/ToTk.pm
# we don't need this in here
rm $RPM_BUILD_ROOT/usr/lib/perl5/*/*/CORE/libperl.a
# test CVE-2007-5116
$RPM_BUILD_ROOT/usr/bin/perl -e '$r=chr(128)."\\x{100}";/$r/'
# test perl-regexp-refoverflow.diff
$RPM_BUILD_ROOT/usr/bin/perl -e '/\6666666666/'
%if 0
# remove unrelated target/os manpages
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlaix.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlamiga.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlapollo.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlbeos.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlbs2000.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlcygwin.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perldgux.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perldos.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlepoc.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlfreebsd.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlhpux.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlhurd.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlirix.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlmachten.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlmacos.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlmacosx.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlmint.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlnetware.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlopenbsd.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlos2.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlos390.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlos400.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlplan9.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlqnx.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlsolaris.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perltru64.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perluts.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlvmesa.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlvms.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlvos.1*
rm $RPM_BUILD_ROOT/usr/share/man/man1/perlwin32.1*
%endif
cat << EOF > perl-base-filelist
/usr/lib/perl5/%pversion/B/Deparse.pm
/usr/lib/perl5/%pversion/Carp.pm
/usr/lib/perl5/%pversion/Carp/
/usr/lib/perl5/%pversion/Class/
/usr/lib/perl5/%pversion/Config/
/usr/lib/perl5/%pversion/Digest.pm
/usr/lib/perl5/%pversion/Digest/
/usr/lib/perl5/%pversion/Exporter.pm
/usr/lib/perl5/%pversion/Exporter/
/usr/lib/perl5/%pversion/File/
/usr/lib/perl5/%pversion/Getopt/
/usr/lib/perl5/%pversion/IPC/
/usr/lib/perl5/%pversion/Text/
/usr/lib/perl5/%pversion/Tie/Hash.pm
/usr/lib/perl5/%pversion/XSLoader.pm
/usr/lib/perl5/%pversion/warnings.pm
/usr/lib/perl5/%pversion/warnings/
/usr/lib/perl5/%pversion/AutoLoader.pm
/usr/lib/perl5/%pversion/FileHandle.pm
/usr/lib/perl5/%pversion/SelectSaver.pm
/usr/lib/perl5/%pversion/Symbol.pm
/usr/lib/perl5/%pversion/base.pm
/usr/lib/perl5/%pversion/bytes.pm
/usr/lib/perl5/%pversion/bytes_heavy.pl
/usr/lib/perl5/%pversion/constant.pm
/usr/lib/perl5/%pversion/fields.pm
/usr/lib/perl5/%pversion/feature.pm
/usr/lib/perl5/%pversion/integer.pm
/usr/lib/perl5/%pversion/locale.pm
/usr/lib/perl5/%pversion/overload.pm
/usr/lib/perl5/%pversion/strict.pm
/usr/lib/perl5/%pversion/utf8.pm
/usr/lib/perl5/%pversion/utf8_heavy.pl
/usr/lib/perl5/%pversion/vars.pm
/usr/lib/perl5/%pversion/version.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Data/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Digest/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/File/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/List/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Scalar/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Dir.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/File.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Handle.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Pipe.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Poll.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Seekable.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Select.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Socket.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/IO/Socket/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/B.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Config.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Config_heavy.pl
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Cwd.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/DynaLoader.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Errno.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Fcntl.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/POSIX.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/Socket.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/attributes.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/Data/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/Digest/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/Fcntl/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/File/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/IO/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/List/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/Cwd/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/Socket/
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/POSIX/POSIX.bs
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/POSIX/POSIX.so
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/POSIX/autosplit.ix
/usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/POSIX/load_imports.al
/usr/lib/perl5/%pversion/*-linux-thread-multi*/lib.pm
/usr/lib/perl5/%pversion/*-linux-thread-multi*/re.pm
EOF
{
  sed -e 's/^/%%exclude /' perl-base-filelist
  (cd $RPM_BUILD_ROOT
   for i in usr/lib/perl5/*/pod/*; do
     case $i in */perldiag.pod) ;;
     *) echo "%%exclude /$i" ;;
     esac
   done)
} > perl-base-excludes

%files base -f perl-base-filelist
%manifest perl.manifest
%dir /usr/lib/perl5
%dir /usr/lib/perl5/%pversion
%dir /usr/lib/perl5/%pversion/B
%dir /usr/lib/perl5/%pversion/*-linux-thread-multi*
%dir /usr/lib/perl5/%pversion/*-linux-thread-multi*/auto
%dir /usr/lib/perl5/%pversion/*-linux-thread-multi*/auto/POSIX
/usr/bin/perl
/usr/bin/perl%pversion
%doc /usr/share/man/man1/perl.1.gz

%files -f perl-base-excludes 
%manifest perl.manifest
%exclude /usr/bin/perl
%exclude /usr/bin/perl%pversion
/usr/bin/*
/usr/lib/perl5/*
%config %{_sysconfdir}/rpm/macros.perl

%files doc
%manifest perl.manifest
%doc README.macros
%exclude /usr/share/man/man1/perl.1.gz
%exclude /usr/lib/perl5/*/pod/perldiag.pod
%doc /usr/share/man/man1/*
%doc /usr/share/man/man3/*
%doc /usr/lib/perl5/*/pod
