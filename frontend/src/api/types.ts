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

export interface JobResultPayload {
  status: string;
  return_code: number | null;
  stdout: string;
  stderr: string;
  message: string;
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
