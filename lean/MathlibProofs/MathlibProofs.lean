import Mathlib
import MathlibProofs.Rank
import MathlibProofs.KlReal
import MathlibProofs.Marginals
import MathlibProofs.FreeEnergy

namespace MathlibProofs

/-- Version marker for the Mathlib plumbing / discharge slice. -/
def proofSliceVersion : Nat := 3

#print axioms free_energy_decomposition_full
#print axioms multiInformation_nonneg_at_joint
#print axioms streamMarginal_pos

end MathlibProofs
