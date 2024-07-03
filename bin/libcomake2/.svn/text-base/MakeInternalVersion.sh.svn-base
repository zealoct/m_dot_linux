#!/bin/bash
#在comake2里面做好标记.天煞的SCM居然不开放$Revision$这样的keyword substitution
#这样做虽然存在原子性问题,但是对于comake2判断版本影响不大.因为comake2版本仅仅是之间比较.
LC_ALL=en_US svn info -r HEAD | awk -F: '/^Revision/ {print substr($2,2);}' > COMAKE.VERSION
