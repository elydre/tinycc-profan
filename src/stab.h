#ifndef __GNU_STAB__

/* Indicate the GNU stab.h is in use.  */

#define __GNU_STAB__

#define __define_stab(NAME, CODE, STRING) NAME=CODE,

enum __stab_debug_code
{
#include "stab_def.h"
LAST_UNUSED_STAB_CODE
};

#undef __define_stab

#endif /* __GNU_STAB_ */
