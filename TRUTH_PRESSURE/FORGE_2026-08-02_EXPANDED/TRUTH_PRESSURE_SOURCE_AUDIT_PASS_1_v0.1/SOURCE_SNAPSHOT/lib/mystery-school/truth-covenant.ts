// The School's epistemic and crediting contract.
//
// This is deliberately plain. Mystery, scholarship, lived tradition, original
// framework work, and artistic inspiration can share a school without pretending
// they are the same kind of evidence.

export type ProvenanceKind =
  | 'scholarship'
  | 'tradition'
  | 'inspiration'
  | 'framework'
  | 'contributor';

export type ProvenanceEntry = {
  kind: ProvenanceKind;
  name: string;
  note: string;
  url?: string;
};

export const PROVENANCE_LABEL: Record<ProvenanceKind, string> = {
  scholarship: 'SCHOLARSHIP / SOURCE',
  tradition: 'TRADITION / LINEAGE',
  inspiration: 'INSPIRATION CREDIT',
  framework: 'LYCHEETAH AUTHORSHIP',
  contributor: 'CONTRIBUTOR',
};

export const SCHOOL_TRUTH_COVENANT = {
  title: 'THE SCHOOL CAN BE WRONG',
  summary:
    'We do not ask you to trust a claim because it sounds certain, ancient, scientific, or beautiful.',
  clauses: [
    'We name what is established, developed, contested, open, or unfalsifiable. A layer is a reading posture—not proof.',
    'Academic and primary sources are evidence trails, not borrowed authority. Read them, challenge them, and follow newer work.',
    'Tradition, lived practice, artistic inspiration, contributor work, and Lycheetah authorship are credited as different things.',
    'An inspiration credit is not an academic citation, endorsement, or claim that the creator agrees with our interpretation.',
    'When a claim fails, the honest move is correction with a visible receipt—not hiding the old certainty.',
  ],
  correction:
    'If you find an error or a missing source, bring the exact subject, claim, and strongest available evidence. The School is built to revise.',
} as const;

