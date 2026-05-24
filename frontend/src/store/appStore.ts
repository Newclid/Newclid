import type { JobResultPayload, JobStatus } from '../api/types';

export interface JobRecord {
  jobId: string;
  status: JobStatus;
  message: string | null;
  result: JobResultPayload | null;
  error: string | null;
  submittedAt: number;
}

export class AppStore {
  /** JGEX problem string — null until the user defines one. */
  problem: string | null = null;
  /** All jobs submitted this session, keyed by job_id. */
  readonly jobs = new Map<string, JobRecord>();
  /** Job currently being tracked (submitted or polling). */
  activeJobId: string | null = null;

  private readonly listeners = new Set<() => void>();

  // ---------- mutators ----------

  setProblem(jgex: string): void {
    this.problem = jgex;
    this.emit();
  }

  addJob(jobId: string): void {
    this.jobs.set(jobId, {
      jobId,
      status: 'queued',
      message: null,
      result: null,
      error: null,
      submittedAt: Date.now(),
    });
    this.activeJobId = jobId;
    this.emit();
  }

  updateJob(jobId: string, patch: Partial<Omit<JobRecord, 'jobId' | 'submittedAt'>>): void {
    const existing = this.jobs.get(jobId);
    if (!existing) return;
    this.jobs.set(jobId, { ...existing, ...patch });
    this.emit();
  }

  setActiveJob(jobId: string | null): void {
    this.activeJobId = jobId;
    this.emit();
  }

  // ---------- pub/sub ----------

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  private emit(): void {
    for (const fn of this.listeners) fn();
  }
}
