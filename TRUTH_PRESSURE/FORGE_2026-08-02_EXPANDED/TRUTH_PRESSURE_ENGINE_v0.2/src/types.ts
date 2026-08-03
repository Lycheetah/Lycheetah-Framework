export type Register =
  | 'IMPLEMENTED'
  | 'MEASURED'
  | 'DERIVED'
  | 'ASSUMED'
  | 'INTERPRETIVE'
  | 'PROVISIONAL';

export type Score01 = number;

export type PressureComponents = {
  evidence: Score01;
  explanatoryPower: Score01;
  strain: Score01;
};

export type PressureConfig = {
  s0: number;
  appScaleFactor: number;
  reviewThresholdCanon?: number;
};

export type PressureScore = {
  components: PressureComponents;
  piCanon: number;
  piApp: number;
  scaleConversion: string;
  reviewThresholdCanon: number | null;
  reviewTriggered: boolean | null;
  interpretation: {
    dominantLimiter: 'evidence' | 'explanatoryPower' | 'strain' | 'none';
    summary: string;
    boundary: string;
  };
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
  provenance?: string;
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
  config?: Partial<PressureConfig>;
  metadata?: Record<string, unknown>;
};

export type StructuredResult = PressureScore & {
  claim: string;
  loadBearingness: Score01;
  handlingQuality: Score01;
  reviewPriority: number;
  registers: Record<string, Register>;
  provenance: {
    evidence: string[];
    explanation: string[];
    strain: string[];
  };
};

export type TextSignal = {
  family: string;
  phrase: string;
  sentence: string;
  weight: number;
};

export type TextAnalysis = StructuredResult & {
  mode: 'PROVISIONAL_TEXT_ADAPTER';
  text: string;
  wordCount: number;
  uniqueSentenceCount: number;
  signals: TextSignal[];
  warnings: string[];
  attacks: string[];
  features: Record<string, number | boolean | string>;
};
