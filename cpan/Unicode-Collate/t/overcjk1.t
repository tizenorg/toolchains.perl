
BEGIN {
    unless ("A" eq pack('U', 0x41)) {
	print "1..0 # Unicode::Collate " .
	    "cannot stringify a Unicode code point\n";
	exit 0;
    }
    if ($ENV{PERL_CORE}) {
	chdir('t') if -d 't';
	@INC = $^O eq 'MacOS' ? qw(::lib) : qw(../lib);
    }
}

use Test;
BEGIN { plan tests => 131 }; # 11 + 15 x @Versions

use strict;
use warnings;
use Unicode::Collate;

ok(1);

#########################

# 2..11

my $overCJK = Unicode::Collate->new(
  table => 'keys.txt',
  normalization => undef,
  entry => <<'ENTRIES',
4E01 ; [.B1FC.0030.0004.4E00] # Ideograph; B1FC = FFFF - 4E03.
ENTRIES
  overrideCJK => sub {
    my $u = 0xFFFF - $_[0]; # reversed
    [$u, 0x20, 0x2, $u];
  },
);

ok($overCJK->gt("B", "A")); # diff. at level 1.
ok($overCJK->lt("a", "A")); # diff. at level 3.
ok($overCJK->lt( "\x{4E03}",  "\x{4E01}")); # diff. at level 2.
ok($overCJK->gt( "\x{4E03}B", "\x{4E01}A"));
ok($overCJK->lt( "\x{4E03}A", "\x{4E01}B"));
ok($overCJK->gt("B\x{4E03}", "A\x{4E01}"));
ok($overCJK->lt("A\x{4E03}", "B\x{4E01}"));
ok($overCJK->lt("A\x{4E03}", "A\x{4E01}"));
ok($overCJK->lt("A\x{4E03}", "a\x{4E01}"));
ok($overCJK->lt("a\x{4E03}", "A\x{4E01}"));

#####

# 9FA6..9FBB are CJK UI since UCA_Version 14 (Unicode 4.1).
# 9FBC..9FC3 are CJK UI since UCA_Version 18 (Unicode 5.1).
# 9FC4..9FCB are CJK UI since UCA_Version 20 (Unicode 5.2).

my @Versions = (8, 9, 11, 14, 16, 18, 20, 22);

for my $v (@Versions) {
    $overCJK->change(UCA_Version => $v);
    ok($overCJK->cmp("a\x{3400}", "A\x{4DB5}") == 1);
    ok($overCJK->cmp("a\x{4DB5}", "A\x{4E00}") == 1);
    ok($overCJK->cmp("a\x{4E00}", "A\x{9FA5}") == 1);
    ok($overCJK->cmp("a\x{9FA5}", "A\x{9FA6}") == ($v >= 14 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FA6}", "A\x{9FAF}") == ($v >= 14 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FAF}", "A\x{9FB0}") == ($v >= 14 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FB0}", "A\x{9FBB}") == ($v >= 14 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FBB}", "A\x{9FBC}") == ($v >= 18 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FBC}", "A\x{9FBF}") == ($v >= 18 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FBF}", "A\x{9FC3}") == ($v >= 18 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FC3}", "A\x{9FC4}") == ($v >= 20 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FC4}", "A\x{9FCA}") == ($v >= 20 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FCA}", "A\x{9FCB}") == ($v >= 20 ? 1 : -1));
    ok($overCJK->cmp("a\x{9FCB}", "A\x{9FCC}") == -1);
    ok($overCJK->cmp("a\x{9FCC}", "A\x{9FCF}") == -1);
}

