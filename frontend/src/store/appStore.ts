import type { JobResultPayload, JobStatus } from '../api/types';

export interface JobRecord {
  jobId: string;
  /**
   * The JGEX string this run was for. Kept per job (not just the global
   * `problem`) so the proofs history can label each row even after newer runs.
   */
  problem: string;
  status: JobStatus;
  message: string | null;
  result: JobResultPayload | null;
  error: string | null;
  submittedAt: number;
}

export type PanelTab = 'toolbar' | 'proofs';

export class AppStore {
  // JGEX problem string, null until the user defines one.
  problem: string | null = null;
  //All jobs submitted this session, keyed by job_id.
  readonly jobs = new Map<string, JobRecord>();
  //Job currently being tracked (submitted or polling). 
  activeJobId: string | null = null;
  // True while the proof panel is shown; disables canvas editing.
  proofMode = false;
  // True while the "proof by points" plane is shown (blank placeholder for now).
  proofByPointsMode = false;
  // Which section of the side panel is currently shown.
  panelTab: PanelTab = 'toolbar';

  private readonly listeners = new Set<() => void>();

  // ---------- mutators ----------

  setProblem(jgex: string): void {
    this.problem = jgex;
    this.emit();
  }

  addJob(jobId: string, problem: string): void {
    this.jobs.set(jobId, {
      jobId,
      problem,
      status: 'queued',
      message: null,
      result: null,
      error: null,
      submittedAt: Date.now(),
    });
    this.activeJobId = jobId;
    this.proofMode = true;
    this.proofByPointsMode = false;
    this.emit();
  }

  enterProofMode(): void {
    this.proofMode = true;
    this.proofByPointsMode = false;
    this.emit();
  }

  exitProofMode(): void {
    this.proofMode = false;
    this.emit();
  }

  enterProofByPoints(): void {
    this.proofByPointsMode = true;
    // The two full-panel modes are mutually exclusive.
    this.proofMode = false;
    this.emit();
  }

  exitProofByPoints(): void {
    this.proofByPointsMode = false;
    this.emit();
  }

  setPanelTab(tab: PanelTab): void {
    if (this.panelTab === tab) return;
    this.panelTab = tab;
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
