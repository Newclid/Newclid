export type JobStatus =
  | 'queued'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'timed_out'
  | 'cancelled';

export const TERMINAL_STATUSES = new Set<JobStatus>([
  'succeeded',
  'failed',
  'timed_out',
  'cancelled',
]);

export interface SubmitJobResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  message: string | null;
}

export interface NewclidProofSections {
  points: string[];
  assumptions: string[];
  numerical_checks: string[];
  trivial_predicates: string[];
  proven_goals: string[];
  unproven_goals: string[];
  proof_steps: string[];
  appendix_ar: string[];
  construction_signatures: string[];
}

export interface SketchPoint {
  name: string;
  x: number;
  y: number;
}

export interface JobResultPayload {
  status: 'succeeded' | 'failed' | 'timed_out';
  message: string;
  proof_text: string | null;
  proof_sections: NewclidProofSections | null;
  run_info: Record<string, unknown> | null;
  sketch_points: SketchPoint[];
  stdout: string;
  stderr: string;
}

export interface JobResultResponse {
  job_id: string;
  status: JobStatus;
  result: JobResultPayload | null;
  error: string | null;
}

export class ApiError extends Error {
  constructor(
    public readonly httpStatus: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /** Server errors and network failures are worth retrying; 4xx are not. */
  get retryable(): boolean {
    return this.httpStatus === 0 || this.httpStatus === 503 || this.httpStatus >= 500;
  }
}
