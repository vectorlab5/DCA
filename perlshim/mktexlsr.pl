# Minimal shim for TeX::Update (missing from conda texlive-core packaging).
# fmtutil.pl only needs `require "mktexlsr.pl"` to succeed and TeX::Update->import().
package TeX::Update;
use strict;
use warnings;
require Exporter;
our @ISA = qw(Exporter);
our @EXPORT = qw(mktexlsr);
sub mktexlsr {
    # Rebuild ls-R databases by shelling out to the mktexlsr binary if present.
    system("mktexlsr", @_) if grep { -x "$_/mktexlsr" } split /:/, ($ENV{PATH}||"");
    return 0;
}
1;
