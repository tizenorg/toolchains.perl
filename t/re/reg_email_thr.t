#!./perl

chdir 't' if -d 't';
@INC = ('../lib', '.');

require 'thread_it.pl';
thread_it(qw(re reg_email.t));
