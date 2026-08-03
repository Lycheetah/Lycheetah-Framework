export type Register =
  | 'IMPLEMENTED'
  | 'MEASURED'
  | 'DERIVED'
  | 'ASSUMED'
  | 'INTERPRETIVE'
  | 'PROVISIONAL'
  | 'OPEN';

export type Score01 = number;
export type ScoreScale = 'unit' | 'percent';

export type PressureComponents = {
  evidence: Score01;
  explanatoryPower: Score01;
  strain: Score01;
};

export type PressureConfig = {
  s0: number;
  reviewThresholdCanon?: number;
};

export type PressureScore = {
  instrument: 'TP-CANONICAL-SCALAR-v0.3';
  components: PressureComponents;
  piCanon: number;
  piNormalized: number;
  /** Compatibility alias. v0.3 defines this as piCanon × s0. */
  piApp: number;
  scale: {
    canonRange: [number, number];
    normalizedRange: [0, 1];
    conversion: string;
    s0: number;
  };
  reviewThresholdCanon: number | null;
  reviewTriggered: boolean | null;
  interpretation: {
    limitingComponents: Array<'evidence' | 'explanatoryPower' | 'strain'>;
    summary: string;
    boundary: string;
  };
  counterfactuals: {
    evidenceRequired: number | null;
    explanatoryPowerRequired: number | null;
    maximumStrain: number | null;
  } | null;
};

export type ProvenanceStatus = 'UNVERIFIED' | 'INSPECTABLE' | 'VERIFIED';
export type ProvenanceRecord = {
  label: string;
  status: ProvenanceStatus;
  locator?: string;
  note?: string;
};

export type EvidenceItem = {
  id: string;
  description: string;
  directness: Score01;
  verifiability: Score01;
  sourceQuality: Score01;
  independence: Score01;
  replication: Score01;
  weight?: number;
  duplicateGroup?: string;
  provenance?: ProvenanceRecord;
};

export type ExplanationItem = {
  id: string;
  description: string;
  mechanismSpecificity: Score01;
  scopeFit: Score01;
  predictiveRisk: Score01;
  unification: Score01;
  falsifiability: Score01;
  weight?: number;
};

export type StrainItem = {
  id: string;
  description: string;
  severity: Score01;
  unresolved: Score01;
  centrality: Score01;
  kind: 'contradiction' | 'ambiguity' | 'scope' | 'alternative' | 'missing-evidence' | 'other';
  weight?: number;
};

export type HandlingAssessment = {
  acknowledgesLimits: Score01;
  distinguishesAlternatives: Score01;
  scopesClaims: Score01;
  namesFalsifier: Score01;
};

export type StructuredAssessment = {
  claim: string;
  evidenceItems: EvidenceItem[];
  explanationItems: ExplanationItem[];
  strainItems: StrainItem[];
  loadBearingness?: Score01;
  handling?: HandlingAssessment;
  unknownStrainFloor?: Score01;
  config?: Partial<PressureConfig>;
  metadata?: Record<string, unknown>;
};

export type StructuredResult = PressureScore & {
  claim: string;
  loadBearingness: Score01;
  handlingQuality: Score01;
  reviewPriority: Score01;
  adjudicationReadiness: Score01;
  registers: Record<string, Register>;
  provenance: {
    evidence: ProvenanceRecord[];
    explanation: string[];
    strain: string[];
  };
  diagnostics: string[];
};

export type TextSignal = {
  family: 'evidence' | 'explanation' | 'strain' | 'handling' | 'load-bearingness' | 'provenance';
  phrase: string;
  sentence: string;
  weight: number;
  status?: Register | ProvenanceStatus;
};

export type TextAnalysis = StructuredResult & {
  mode: 'PROVISIONAL_TEXT_TRIAGE-v0.3';
  text: string;
  wordCount: number;
  uniqueSentenceCount: number;
  signals: TextSignal[];
  warnings: string[];
  attacks: string[];
  features: Record<string, number | boolean | string>;
};
