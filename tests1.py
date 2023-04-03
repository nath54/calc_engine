from calc_engine import *
from calc_engine import _R, _Q, _D, _Z, _N, _empty

assert _R.inclus_dans(_R)
assert _Q.inclus_dans(_R)
assert _D.inclus_dans(_R)
assert _Z.inclus_dans(_R)
assert _N.inclus_dans(_R)
assert _Q.inclus_dans(_Q)
assert _D.inclus_dans(_Q)
assert _Z.inclus_dans(_Q)
assert _N.inclus_dans(_Q)
assert _D.inclus_dans(_D)
assert _Z.inclus_dans(_D)
assert _N.inclus_dans(_D)
assert _Z.inclus_dans(_Z)
assert _N.inclus_dans(_Z)
assert _N.inclus_dans(_N)

assert not _R.inclus_dans(_empty)
assert not _Q.inclus_dans(_empty)
assert not _D.inclus_dans(_empty)
assert not _Z.inclus_dans(_empty)
assert not _N.inclus_dans(_empty)
assert _empty.inclus_dans(_R)
assert _empty.inclus_dans(_Q)
assert _empty.inclus_dans(_D)
assert _empty.inclus_dans(_Z)
assert _empty.inclus_dans(_N)


print("Les tests se sont déroulés sans encombre !")
