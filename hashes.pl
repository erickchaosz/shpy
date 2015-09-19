#!/usr/bin/perl -w

%nums = ();


$nums{"name"} = ret_hash();
$nums{"name"}{"erick"} = ret_num();

print $nums{"name"}{"erick"}{"aa"};

sub ret_hash {
    my %res = ();
    $res{"erick"} = 1;
    return \%res;
}

sub ret_num {
    my %res = ();
    $res{"aa"} = 2;
    return \%res;
}
