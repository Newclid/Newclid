import type {
  JobResultResponse,
  JobStatusResponse,
  SubmitJobResponse,
} from './types';
import { ApiError } from './types';

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    throw new ApiError(0, `Network error: ${err instanceof Error ? err.message : String(err)}`);
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (typeof body?.detail === 'string') detail = body.detail;
    } catch {
      // ignore parse failure; use statusText
    }
    throw new ApiError(response.status, detail);
  }
  return response.json() as Promise<T>;
}

export class BackendClient {
  constructor(private readonly baseUrl: string = '/api') {}

  async healthCheck(): Promise<boolean> {
    try {
      await request(`${this.baseUrl}/health`);
      return true;
    } catch {
      return false;
    }
  }

  submitJob(problem: string, timeoutSeconds = 120): Promise<SubmitJobResponse> {
    return request<SubmitJobResponse>(`${this.baseUrl}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_type: 'jgex',
        problem_input: problem,
        timeout_seconds: timeoutSeconds,
      }),
    });
  }

  getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return request<JobStatusResponse>(`${this.baseUrl}/jobs/${encodeURIComponent(jobId)}`);
  }

  getJobResult(jobId: string): Promise<JobResultResponse> {
    return request<JobResultResponse>(
      `${this.baseUrl}/jobs/${encodeURIComponent(jobId)}/result`,
    );
  }
}
