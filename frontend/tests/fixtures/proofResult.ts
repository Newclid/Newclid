import type { JobResultPayload, NewclidProofSections } from '../../src/api/types';

// Canonical proof step with 2 text premises and 1 conclusion.
// countTextPremises = 2, so substeps are: 0 (premise 0), 1 (premise 1), 2 (conclusion).
export const SAMPLE_PROOF_STEP =
  '000. | some premise [C0], another premise [N0] =(some-rule)> conclusion [1]';

export function makeSections(overrides?: Partial<NewclidProofSections>): NewclidProofSections {
  return {
    assumptions: ['[C0] : collinear A B C'],
    numerical_checks: ['[N0] : dist(A,B) = 1'],
    proof_steps: [SAMPLE_PROOF_STEP],
    proven_goals: ['collinear A B C'],
    unproven_goals: [],
    points: [],
    trivial_predicates: [],
    appendix_ar: [],
    construction_signatures: [],
    step_signatures: [],
    goal_signatures: [],
    step_premise_indices: [],
    ...overrides,
  };
}

export function makeSucceededResult(overrides?: Partial<JobResultPayload>): JobResultPayload {
  return {
    status: 'succeeded',
    message: '',
    proof_text: null,
    proof_sections: makeSections(),
    sketch_points: [],
    run_info: null,
    stdout: '',
    stderr: '',
    ...overrides,
  };
}

export function makeFailedResult(message = 'no proof found'): JobResultPayload {
  return {
    status: 'failed',
    message,
    proof_text: null,
    proof_sections: null,
    sketch_points: [],
    run_info: null,
    stdout: '',
    stderr: '',
  };
}

// Convenience builder for multi-step results (each step uses SAMPLE_PROOF_STEP).
export function makeMultiStepResult(stepCount: number): JobResultPayload {
  return makeSucceededResult({
    proof_sections: makeSections({
      proof_steps: Array.from({ length: stepCount }, () => SAMPLE_PROOF_STEP),
    }),
  });
}
